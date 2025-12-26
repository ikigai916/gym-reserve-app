from google.cloud import firestore
import os

def get_db():
    """
    Firestore クライアントの初期化
    """
    try:
        db = firestore.Client()
        print("Firestore client initialized successfully")
        return db
    except Exception as e:
        print(f"⚠️  Error initializing Firestore client: {e}")
        print("⚠️  Firestore認証情報を設定してください:")
        print("    gcloud auth application-default login")
        # 開発環境では、エラーを表示して続行（本番環境では適切に処理）
        raise e

db = get_db()

