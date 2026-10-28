from fastapi import APIRouter

from app.api.routes import achievements, auth, health, hints, missions, progress

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(missions.router)
api_router.include_router(hints.router)
api_router.include_router(progress.router)
api_router.include_router(achievements.router)
