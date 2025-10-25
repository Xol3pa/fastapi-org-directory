from fastapi import APIRouter

from src.api.routers import activities, buildings, organizations

main_router = APIRouter()

main_router.include_router(buildings.router)
main_router.include_router(activities.router)
main_router.include_router(organizations.router)

