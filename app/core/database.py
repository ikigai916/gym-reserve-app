from google.cloud import firestore
import os
import logging

logger = logging.getLogger(__name__)

# 遅延初期化のためのグローバル変数
_db = None

def get_db():
    """
    Firestore クライアントの初期化（シングルトン・遅延初期化）
    """
    global _db
    if _db is None:
        try:
            project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
            if project_id:
                logger.info(f"Initializing Firestore client for project: {project_id}")
                _db = firestore.Client(project=project_id)
            else:
                logger.info("Initializing Firestore client (automatic project detection)")
                _db = firestore.Client()
            logger.info("Firestore client initialized successfully")
        except Exception as e:
            logger.error(f"⚠️  Error initializing Firestore client: {e}")
            # ここで例外を投げるとアプリケーション全体がクラッシュするため、
            # 呼び出し側でハンドリングできるようにするか、Noneを返して後でリトライする
            # ただし、現状のコードベースが `db` が常に存在することを前提としているため
            # ここでは敢えて例外を投げ、ログを確認できるようにする
            raise e
    return _db

# 他のモジュールが `from app.core.database import db` としているため、
# 直接 Client オブジェクトを公開するのではなく、プロキシ的に振る舞うか、
# 各エンドポイントで get_db() を呼ぶように修正するのが理想的。
# 短期的な修正として、モジュールロード時の即時初期化を避け、
# 最初のアクセスで初期化されるプロキシ風のオブジェクトを導入する。

class FirestoreProxy:
    def __getattr__(self, name):
        return getattr(get_db(), name)

    def collection(self, *args, **kwargs):
        return get_db().collection(*args, **kwargs)

    def document(self, *args, **kwargs):
        return get_db().document(*args, **kwargs)

    def transaction(self, *args, **kwargs):
        return get_db().transaction(*args, **kwargs)

    def batch(self, *args, **kwargs):
        return get_db().batch(*args, **kwargs)

db = FirestoreProxy()


