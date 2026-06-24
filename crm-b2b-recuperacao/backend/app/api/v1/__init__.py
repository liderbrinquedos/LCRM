from fastapi import APIRouter
from app.api.v1.endpoints import opportunities

api_router = APIRouter()

api_router.include_router(opportunities.router)
