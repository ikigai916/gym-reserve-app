from fastapi import APIRouter
from app.api.endpoints import users, reservations

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(reservations.router, prefix="/reservations", tags=["reservations"])

