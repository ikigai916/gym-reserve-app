from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional
from datetime import datetime, timedelta, time
from google.cloud.firestore_v1.base_query import FieldFilter
from app.schemas.reservation import ReservationCreate, ReservationResponse
from app.core.database import db
from app.core.auth import get_current_user
from google.cloud import firestore

import logging

logger = logging.getLogger(__name__)
router = APIRouter()

def check_deadline(reservation_date_str):
    """予約・キャンセルの期限チェック (前日24時)"""
    try:
        if isinstance(reservation_date_str, datetime):
            reservation_date = reservation_date_str
        else:
            # 文字列の場合はパース
            reservation_date = datetime.fromisoformat(str(reservation_date_str).split(' ')[0])
            
        deadline = datetime.combine(reservation_date - timedelta(days=1), time(23, 59, 59))
        
        if datetime.now() > deadline:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="予約・キャンセルの期限（前日24時）を過ぎています"
            )
    except (ValueError, TypeError) as e:
        logger.error(f"Error in check_deadline: {e}")
        # パースエラーの場合は安全のため期限チェックをパスさせるか、エラーを出す
        # ここではログを出して続行を試みる（古いデータの救済）
        pass

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
        
        # 開始日時の確定 (UTC ISO形式があれば優先)
        if res.startAt:
            # Zを+00:00に置換してfromisoformatでパース
            start_dt = datetime.fromisoformat(res.startAt.replace('Z', '+00:00'))
        else:
            # フォールバック: naive datetime (サーバーのローカル時間に依存)
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
            
            # トランザクション内では stream() ではなく get() を使用する
            avail_docs = list(avail_query.get(transaction=transaction))
            
            # スロットが足りているかチェック
            if len(avail_docs) < num_slots:
                raise HTTPException(status_code=400, detail="指定された時間枠の空きがありません")
            
            # 全てのスロットが未予約かチェック
            for doc in avail_docs:
                if doc.to_dict().get("isBooked"):
                    raise HTTPException(status_code=400, detail="既に予約されている時間枠が含まれています")
            
        # 2. Reservation ドキュメントの作成
        now = datetime.now().isoformat()
        
        # 表示用の終了時刻を計算 (JSTの開始時刻文字列から計算)
        try:
            start_h, start_m = map(int, res.startTime.split(':'))
            temp_dt = datetime(2000, 1, 1, start_h, start_m) + timedelta(minutes=res.courseMinutes)
            display_end_time = temp_dt.strftime("%H:%M")
        except:
            # 念のためUTCからの変換もフォールバックとして用意
            jst_end = end_dt + timedelta(hours=9)
            display_end_time = jst_end.strftime("%H:%M")

        res_ref = db.collection("reservations").document()
        res_data = {
            "userId": current_user["id"],
            "user_name": current_user["name"],
            "trainerId": res.trainerId,
            "date": res.date,
            "startTime": res.startTime,
            "endTime": display_end_time,
            "courseMinutes": res.courseMinutes,
            "status": "active",
            "startAt": start_dt,
            "endAt": end_dt,
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
            
        docs = query.stream()
        
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
    logger.info(f"Cancellation request for ID: {reservation_id} by user: {current_user['id']}")
    try:
        res_ref = db.collection("reservations").document(reservation_id)
        res_doc = res_ref.get()
        
        if not res_doc.exists:
            logger.warning(f"Reservation {reservation_id} not found")
            raise HTTPException(status_code=404, detail="予約が見つかりません")
            
        res_data = res_doc.to_dict()
        logger.info(f"Reservation data found: {res_data}")
        
        # 権限チェック (userId がない場合は所有者確認をスキップし、トレーナーのみ許可)
        res_user_id = res_data.get("userId")
        is_owner = res_user_id == current_user["id"]
        is_trainer = current_user.get("role") == "trainer"
        
        if not is_owner and not is_trainer:
            logger.warning(f"Permission denied for user {current_user['id']} on reservation {reservation_id}")
            raise HTTPException(status_code=403, detail="権限がありません")
            
        # 期限チェック
        check_deadline(res_data["date"])
        
        if res_data["status"] == "cancelled":
            logger.info(f"Reservation {reservation_id} is already cancelled")
            return {"message": "既にキャンセルされています"}
            
        # トランザクションでキャンセル処理
        transaction = db.transaction()
        
        @firestore.transactional
        def cancel_in_transaction(transaction):
            logger.info("Starting cancellation transaction")
            
            # 1. 関連する Availability を特定（読み取りを先に行う）
            try:
                if "startAt" in res_data and res_data["startAt"]:
                    # 新しい形式のデータ（Timestamp または datetime オブジェクト）
                    start_dt = res_data["startAt"]
                    end_dt = res_data["endAt"]
                    logger.info(f"Using Timestamp formats: {start_dt} to {end_dt}")
                else:
                    # 旧データ互換: 文字列からパース
                    if not all(k in res_data for k in ['date', 'startTime', 'courseMinutes', 'trainerId']):
                        logger.error(f"Old reservation data is missing required fields: {res_data}")
                        raise HTTPException(status_code=400, detail="予約データの形式が正しくありません（旧データ不備）")

                    start_time_str = res_data['startTime']
                    if len(start_time_str) == 4: # "9:00" -> "09:00"
                        start_time_str = "0" + start_time_str
                    
                    try:
                        # date が datetime オブジェクトの場合がある
                        d_str = res_data['date']
                        if isinstance(d_str, datetime):
                            d_str = d_str.strftime('%Y-%m-%d')
                        
                        start_dt = datetime.fromisoformat(f"{d_str}T{start_time_str}:00")
                        c_mins = int(res_data["courseMinutes"])
                        end_dt = start_dt + timedelta(minutes=c_mins)
                        logger.info(f"Parsed from strings: {start_dt} to {end_dt}")
                    except (ValueError, TypeError) as ve:
                        logger.error(f"Date/Time parsing error for old data: {ve}")
                        raise HTTPException(status_code=400, detail="予約日時の形式が正しくありません")
                
                # 読み取り操作
                avail_query = db.collection("availabilities")\
                    .where(filter=FieldFilter("trainerId", "==", res_data["trainerId"]))\
                    .where(filter=FieldFilter("startAt", ">=", start_dt))\
                    .where(filter=FieldFilter("startAt", "<", end_dt))
                
                avail_docs = list(avail_query.get(transaction=transaction))
                logger.info(f"Found {len(avail_docs)} availability slots to release")
                
                # 2. 書き込み操作 (読み取りの後に実行)
                # 予約をキャンセル状態に
                transaction.update(res_ref, {
                    "status": "cancelled",
                    "updatedAt": datetime.now().isoformat()
                })
                
                # 稼働枠を解放
                for doc in avail_docs:
                    transaction.update(doc.reference, {"isBooked": False})
                    
            except Exception as inner_e:
                logger.error(f"Error during transaction execution: {inner_e}")
                raise inner_e
        
        cancel_in_transaction(transaction)
        logger.info(f"Successfully cancelled reservation {reservation_id}")
        return {"status": "success", "message": "予約をキャンセルしました"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Cancellation error for {reservation_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"キャンセルエラー: {str(e)}")
