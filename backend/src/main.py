from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from src.core.config import get_settings
from src.api.auth import router as auth_router
from src.api.ho_so import router as ho_so_router
from src.api.rag import router as rag_router
from src.api.agents import router as agents_router
from src.rag.vector_store import init_collection

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Khởi động AI Phường Xã...")
    await init_collection()
    logger.info("✅ Qdrant collection sẵn sàng")
    yield
    logger.info("👋 Tắt server")


app = FastAPI(
    title=settings.APP_NAME,
    description="Hệ thống AI Hành chính Phường/Xã TP.HCM",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(ho_so_router)
app.include_router(rag_router)
app.include_router(agents_router)


@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.APP_NAME}