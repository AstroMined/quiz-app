# filename: backend/app/middleware/cors_middleware.py

from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import settings_core


def add_cors_middleware(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings_core.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
