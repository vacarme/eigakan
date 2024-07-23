from fastapi import APIRouter

from eigakan.auth.router import router as auth_router
from eigakan.theater.router import router as theater_router

router = APIRouter()
router.include_router(theater_router, prefix="/theaters", tags=["Theatres"])
router.include_router(auth_router, prefix="/auth", tags=["Auth"])
