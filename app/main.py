from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.api.router import api_router
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# APIルーターの登録
app.include_router(api_router, prefix="/api")

# 静的ファイルの配信設定
# 1. 既存の /reservations エンドポイントなどの互換性のためのリダイレクトや直接定義が必要な場合
# ここでは api/router.py で定義したものとは別に、旧エンドポイントへの対応が必要ならここで行う

@app.get("/health")
def health_check():
    return {"status": "ok", "service": settings.PROJECT_NAME}

# フロントエンドの配信
static_path = os.path.join(os.path.dirname(__file__), "static")

# StaticFilesをマウント
app.mount("/assets", StaticFiles(directory=static_path), name="static")

@app.get("/")
async def serve_index():
    return FileResponse(os.path.join(static_path, "index.html"))

@app.get("/index.html")
async def serve_index_html():
    return await serve_index()

@app.get("/login.html")
async def serve_login():
    return FileResponse(os.path.join(static_path, "login.html"))

# 互換性のためのルート（旧 /reservations への対応など）
@app.get("/reservations")
async def legacy_get_reservations():
    from app.api.endpoints.reservations import get_reservations_legacy
    return await get_reservations_legacy()

@app.post("/reservations")
async def legacy_create_reservation(res: dict):
    from app.api.endpoints.reservations import create_reservation_legacy
    from app.schemas.reservation import ReservationLegacy
    return await create_reservation_legacy(ReservationLegacy(**res))

