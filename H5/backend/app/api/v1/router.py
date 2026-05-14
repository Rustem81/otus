from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints import admin, advertisements, auth, blacklist, history, profile, scoring

api_v1_router = APIRouter(prefix="/api/v1")

# Auth endpoints
api_v1_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# Profile endpoints
api_v1_router.include_router(profile.router, prefix="/profile", tags=["profile"])

# Advertisement endpoints
api_v1_router.include_router(advertisements.router, prefix="/advertisements", tags=["advertisements"])

# Scoring endpoints
api_v1_router.include_router(scoring.router, prefix="/scoring", tags=["scoring"])

# Blacklist endpoints
api_v1_router.include_router(blacklist.router, prefix="/blacklist", tags=["blacklist"])

# View history endpoints
api_v1_router.include_router(history.router, prefix="/history", tags=["history"])

# Admin endpoints
api_v1_router.include_router(admin.router, prefix="/admin", tags=["admin"])
