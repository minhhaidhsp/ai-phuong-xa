# src/main.py
# Entrypoint FastAPI — đăng ký middleware và routers

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from src.core.config import get_settings
from src.api.auth import router as auth_router

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    description="Hệ thống AI Hành chính Phường/Xã TP.HCM",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS: cho phép Next.js frontend gọi API từ domain khác
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,  # Cho phép gửi Authorization header
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Đăng ký Routers ───────────────────────────────────────────────────
app.include_router(auth_router)   # /api/v1/auth/*

# Sprint 3+ sẽ thêm dần:
# app.include_router(ho_so_router)
# app.include_router(rag_router)
# app.include_router(agent_router)


@app.get("/", tags=["⚙️ System"])
async def root():
    return {"app": settings.APP_NAME, "env": settings.APP_ENV, "docs": "/docs"}


@app.get("/health", tags=["⚙️ System"])
async def health_check():
    return {"status": "ok"}


logger.info(f"🚀 {settings.APP_NAME} started — ENV: {settings.APP_ENV}")