import os
import logging
from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, HTTPException, Depends
from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

from app.core.database import db
from app.core.auth import get_current_trainer
from app.schemas.availability import AvailabilityCreate, AvailabilityResponse

router = APIRouter()

@router.post("/", response_model=List[AvailabilityResponse])
async def create_availabilities(
    data: AvailabilityCreate, 
    current_trainer: dict = Depends(get_current_trainer)
):
    """稼働枠を一括登録（トレーナー専用）"""
    try:
        # trainerIdがログインユーザーと一致するかチェック（権限強化）
        if data.trainerId != current_trainer["id"]:
             raise HTTPException(status_code=403, detail="他のトレーナーの枠は登録できません")

        availabilities_collection = db.collection("availabilities")
        results = []
        
        # 既存の枠を取得して重複チェック (タイムスタンプで比較し、精度と型不整合を回避)
        start_times = [slot.startAt for slot in data.slots]
        if not start_times:
            return []
            
        min_start = min(start_times)
        max_start = max(start_times)
        
        # 余裕を持って前後1分広げて検索
        search_start = min_start - timedelta(minutes=1)
        search_end = max_start + timedelta(minutes=1)
        
        existing_docs = availabilities_collection\
            .where(filter=FieldFilter("trainerId", "==", data.trainerId))\
            .where(filter=FieldFilter("startAt", ">=", search_start))\
            .where(filter=FieldFilter("startAt", "<=", search_end))\
            .stream()
            
        existing_starts = set()
        for doc in existing_docs:
            d = doc.to_dict()
            st = d.get("startAt")
            if isinstance(st, datetime):
                # 秒単位で丸めて比較
                existing_starts.add(st.replace(microsecond=0).timestamp())
            elif isinstance(st, str):
                try:
                    dt = datetime.fromisoformat(st.replace('Z', '+00:00'))
                    existing_starts.add(dt.replace(microsecond=0).timestamp())
                except ValueError:
                    continue

        # バッチ処理で登録
        batch = db.batch()
        count = 0
        for slot in data.slots:
            # 重複チェック (秒単位で比較)
            slot_ts = slot.startAt.replace(microsecond=0).timestamp()
            if slot_ts in existing_starts:
                continue

            doc_ref = availabilities_collection.document()
            slot_data = {
                "trainerId": data.trainerId,
                "startAt": slot.startAt,
                "endAt": slot.endAt,
                "isBooked": False
            }
            batch.set(doc_ref, slot_data)
            results.append(AvailabilityResponse(id=doc_ref.id, **slot_data))
            count += 1
            # 二重登録防止のため、追加した分も existing_starts に入れる
            existing_starts.add(slot_ts)
        
        if count > 0:
            batch.commit()
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"稼働枠登録エラー: {str(e)}")

@router.post("/copy-last-week")
async def copy_last_week_availabilities(
    target_date: str,
    current_trainer: dict = Depends(get_current_trainer)
):
    """前週の同じ曜日の稼働枠をコピー"""
    try:
        # 1. 前週の同じ曜日を計算
        target_dt = datetime.fromisoformat(f"{target_date}T00:00:00")
        last_week_dt = target_dt - timedelta(days=7)
        last_week_end_dt = last_week_dt + timedelta(days=1)
        
        # 2. 前週の稼働枠を取得
        availabilities_collection = db.collection("availabilities")
        last_week_slots = availabilities_collection\
            .where(filter=FieldFilter("trainerId", "==", current_trainer["id"]))\
            .where(filter=FieldFilter("startAt", ">=", last_week_dt))\
            .where(filter=FieldFilter("startAt", "<", last_week_end_dt))\
            .stream()
        
        # 3. 今日の既存枠を取得（重複防止）
        target_end_dt = target_dt + timedelta(days=1)
        existing_docs = availabilities_collection\
            .where(filter=FieldFilter("trainerId", "==", current_trainer["id"]))\
            .where(filter=FieldFilter("startAt", ">=", target_dt))\
            .where(filter=FieldFilter("startAt", "<", target_end_dt))\
            .stream()
        
        existing_starts = {doc.to_dict()["startAt"].isoformat() if isinstance(doc.to_dict()["startAt"], datetime) else doc.to_dict()["startAt"] for doc in existing_docs}

        # 4. コピー作成
        batch = db.batch()
        count = 0
        for doc in last_week_slots:
            data = doc.to_dict()
            
            # 時間部分を維持しつつ日付をターゲット日に変更
            # data["startAt"] は datetime オブジェクト
            old_start = data["startAt"]
            old_end = data["endAt"]
            
            new_start = datetime.combine(target_dt.date(), old_start.time())
            new_end = datetime.combine(target_dt.date(), old_end.time())
            
            if new_start.isoformat() in existing_starts:
                continue
                
            new_ref = availabilities_collection.document()
            batch.set(new_ref, {
                "trainerId": current_trainer["id"],
                "startAt": new_start,
                "endAt": new_end,
                "isBooked": False
            })
            count += 1
            
        if count > 0:
            batch.commit()
            
        return {"status": "success", "copied_count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"コピーエラー: {str(e)}")

@router.get("/", response_model=List[AvailabilityResponse])
async def get_availabilities(date: str, trainer_id: str = None):
    """指定日の稼働枠を取得（30分単位の生データ）"""
    try:
        # dateは YYYY-MM-DD 形式
        start_dt = datetime.fromisoformat(f"{date}T00:00:00")
        end_dt = start_dt + timedelta(days=1)
        
        query = db.collection("availabilities")\
            .where(filter=FieldFilter("startAt", ">=", start_dt))\
            .where(filter=FieldFilter("startAt", "<", end_dt))
            
        if trainer_id:
            query = query.where(filter=FieldFilter("trainerId", "==", trainer_id))
            
        docs = query.order_by("startAt").stream()
        
        results = []
        for doc in docs:
            data = doc.to_dict()
            results.append(AvailabilityResponse(id=doc.id, **data))
            
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"稼働枠取得エラー: {str(e)}")

@router.delete("/{availability_id}")
async def delete_availability(
    availability_id: str, 
    current_trainer: dict = Depends(get_current_trainer)
):
    """稼働枠を削除"""
    try:
        doc_ref = db.collection("availabilities").document(availability_id)
        doc = doc_ref.get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="枠が見つかりません")
        
        data = doc.to_dict()
        if data["trainerId"] != current_trainer["id"]:
            raise HTTPException(status_code=403, detail="権限がありません")
            
        if data["isBooked"]:
            raise HTTPException(status_code=400, detail="予約済みの枠は削除できません")
            
        doc_ref.delete()
        return {"status": "success", "id": availability_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
