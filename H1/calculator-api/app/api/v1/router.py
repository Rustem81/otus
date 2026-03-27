"""Versioned API router — aggregates all v1 endpoints.

Follows the fastapi-templates skill pattern with centralized router.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import calculator, health

api_router = APIRouter()
api_router.include_router(calculator.router, tags=["calculator"])
api_router.include_router(health.router, tags=["health"])
