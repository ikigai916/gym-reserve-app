from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from datetime import datetime, timedelta, time
from google.cloud.firestore_v1.base_query import FieldFilter
from app.schemas.reservation import ReservationCreate, ReservationResponse
from app.core.database import db
from app.core.auth import get_current_user
from google.cloud import firestore

router = APIRouter()

def check_deadline(reservation_date_str: str):
    """予約・キャンセルの期限チェック (前日24時)"""
    # 予約日の前日 23:59:59 (実質24時)
    reservation_date = datetime.fromisoformat(reservation_date_str)
    deadline = datetime.combine(reservation_date - timedelta(days=1), time(23, 59, 59))
    
    if datetime.now() > deadline:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="予約・キャンセルの期限（前日24時）を過ぎています"
        )

@router.post("/", response_model=ReservationResponse)
async def create_reservation(
    res: ReservationCreate, 
    current_user: dict = Depends(get_current_user)
):
    """予約を作成（トランザクション処理）"""
    try:
        # 期限チェック
        check_deadline(res.date)
        
        # 必要なスロット数を計算 (30分単位)
        num_slots = res.courseMinutes // 30
        start_dt = datetime.fromisoformat(f"{res.date}T{res.startTime}:00")
        
        # 連続スロットの開始から終了までの時間を計算
        end_dt = start_dt + timedelta(minutes=res.courseMinutes)
        
        # トランザクション
        transaction = db.transaction()
        
        @firestore.transactional
        def create_in_transaction(transaction):
            # 1. 指定された時間枠の Availability を取得
            avail_query = db.collection("availabilities")\
                .where(filter=FieldFilter("trainerId", "==", res.trainerId))\
                .where(filter=FieldFilter("startAt", ">=", start_dt))\
                .where(filter=FieldFilter("startAt", "<", end_dt))\
                .order_by("startAt")
            
            avail_docs = list(avail_query.stream(transaction=transaction))
            
            # スロットが足りているかチェック
            if len(avail_docs) < num_slots:
                raise HTTPException(status_code=400, detail="指定された時間枠の空きがありません")
            
            # 全てのスロットが未予約かチェック
            for doc in avail_docs:
                if doc.to_dict().get("isBooked"):
                    raise HTTPException(status_code=400, detail="既に予約されている時間枠が含まれています")
            
            # 2. Reservation ドキュメントの作成
            now = datetime.now().isoformat()
            res_ref = db.collection("reservations").document()
            res_data = {
                "userId": current_user["id"],
                "user_name": current_user["name"],
                "trainerId": res.trainerId,
                "date": res.date,
                "startTime": res.startTime,
                "endTime": end_dt.strftime("%H:%M"),
                "courseMinutes": res.courseMinutes,
                "status": "active",
                "createdAt": now,
                "updatedAt": now
            }
            transaction.set(res_ref, res_data)
            
            # 3. Availability の更新
            for doc in avail_docs:
                transaction.update(doc.reference, {"isBooked": True})
            
            return res_ref.id, res_data

        res_id, res_data = create_in_transaction(transaction)
        
        return ReservationResponse(id=res_id, **res_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"予約作成エラー: {str(e)}")

@router.get("/", response_model=List[ReservationResponse])
async def get_reservations(current_user: dict = Depends(get_current_user)):
    """予約一覧を取得（ロールに応じてフィルタリング）個人またはトレーナーに関連するもの"""
    try:
        query = db.collection("reservations")
        
        # ロールに応じてフィルタリング
        if current_user.get("role") == "trainer":
            # トレーナーは自分宛の予約をすべて取得
            query = query.where(filter=FieldFilter("trainerId", "==", current_user["id"]))
        else:
            # 一般会員は自分の予約のみ
            query = query.where(filter=FieldFilter("userId", "==", current_user["id"]))
            
        docs = query.order_by("createdAt", direction=firestore.Query.DESCENDING).stream()
        
        results = []
        for doc in docs:
            data = doc.to_dict()
            results.append(ReservationResponse(id=doc.id, **data))
            
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"予約取得エラー: {str(e)}")

@router.post("/{reservation_id}/cancel")
async def cancel_reservation(
    reservation_id: str, 
    current_user: dict = Depends(get_current_user)
):
    """予約をキャンセル"""
    try:
        res_ref = db.collection("reservations").document(reservation_id)
        res_doc = res_ref.get()
        
        if not res_doc.exists:
            raise HTTPException(status_code=404, detail="予約が見つかりません")
            
        res_data = res_doc.to_dict()
        
        # 権限チェック
        if res_data["userId"] != current_user["id"] and current_user.get("role") != "trainer":
            raise HTTPException(status_code=403, detail="権限がありません")
            
        # 期限チェック
        check_deadline(res_data["date"])
        
        if res_data["status"] == "cancelled":
            return {"message": "既にキャンセルされています"}
            
        # トランザクションでキャンセル処理
        transaction = db.transaction()
        
        @firestore.transactional
        def cancel_in_transaction(transaction):
            # 1. 予約をキャンセル状態に
            transaction.update(res_ref, {
                "status": "cancelled",
                "updatedAt": datetime.now().isoformat()
            })
            
            # 2. 関連する Availability を解放
            start_dt = datetime.fromisoformat(f"{res_data['date']}T{res_data['startTime']}:00")
            end_dt = start_dt + timedelta(minutes=res_data["courseMinutes"])
            
            avail_query = db.collection("availabilities")\
                .where(filter=FieldFilter("trainerId", "==", res_data["trainerId"]))\
                .where(filter=FieldFilter("startAt", ">=", start_dt))\
                .where(filter=FieldFilter("startAt", "<", end_dt))
            
            avail_docs = avail_query.stream(transaction=transaction)
            for doc in avail_docs:
                transaction.update(doc.reference, {"isBooked": False})
        
        cancel_in_transaction(transaction)
        return {"status": "success", "message": "予約をキャンセルしました"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"キャンセルエラー: {str(e)}")
