from fastapi import APIRouter
from app.api.endpoints import users, reservations, auth, availabilities

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(reservations.router, prefix="/reservations", tags=["reservations"])
api_router.include_router(availabilities.router, prefix="/availabilities", tags=["availabilities"])


