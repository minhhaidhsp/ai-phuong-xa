# src/api/rag.py
# Endpoints RAG — hỏi đáp AI về pháp luật hành chính
#
# POST /api/v1/rag/query        → hỏi đáp AI (cần login)
# POST /api/v1/rag/index        → index văn bản mới (chỉ admin)
# GET  /api/v1/rag/stats        → thống kê collection

from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from loguru import logger

from src.core.dependencies import get_current_user, require_admin
from src.db.models import NguoiDung
from src.rag.pipeline import rag_query
from src.rag.embeddings import embed_text
from src.rag.vector_store import upsert_documents, get_collection_info
import uuid

router = APIRouter(prefix="/api/v1/rag", tags=["🤖 AI / RAG"])


# ── Schemas ───────────────────────────────────────────────────────────

class QueryRequest(BaseModel):
    """Request hỏi đáp AI"""
    question: str                       # Câu hỏi của cán bộ
    top_k: int = 5                      # Số văn bản tìm kiếm
    filter_loai: Optional[str] = None   # Lọc loại văn bản
    min_score: float = 0.0              # Ngưỡng tối thiểu


class SourceItem(BaseModel):
    """1 nguồn trích dẫn"""
    ten_van_ban: str
    dieu_khoan: str
    score: float
    url: str


class QueryResponse(BaseModel):
    """Response câu trả lời AI"""
    question: str
    answer: str
    sources: list[SourceItem]
    found_docs: int
    model: str


class IndexRequest(BaseModel):
    """Request index văn bản mới vào Qdrant"""
    ten_van_ban: str        # Tên văn bản: "Luật Hôn nhân và Gia đình 2014"
    loai: str               # luat | nghi_dinh | thong_tu | quyet_dinh
    dieu_khoan: str         # "Điều 8" hoặc "" nếu là toàn văn
    noi_dung: str           # Nội dung đoạn văn bản
    url: Optional[str] = "" # Link nguồn gốc


class IndexResponse(BaseModel):
    message: str
    indexed_count: int


# ── Endpoints ─────────────────────────────────────────────────────────

@router.post("/query", response_model=QueryResponse)
async def query_ai(
    body: QueryRequest,
    current_user: Annotated[NguoiDung, Depends(get_current_user)],
):
    """
    Hỏi đáp AI về thủ tục hành chính và pháp luật.
    
    AI sẽ:
    1. Tìm văn bản pháp luật liên quan trong Qdrant
    2. Dùng LLM (qwen2.5:7b) tổng hợp câu trả lời
    3. Trích dẫn nguồn rõ ràng
    
    Ví dụ câu hỏi:
    - "Điều kiện đăng ký kết hôn là gì?"
    - "Hồ sơ đăng ký thường trú cần những giấy tờ gì?"
    """
    if not body.question.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Câu hỏi không được để trống"
        )

    try:
        result = await rag_query(
            question=body.question,
            top_k=body.top_k,
            filter_loai=body.filter_loai,
            min_score=body.min_score,
        )
        return QueryResponse(**result)
    except Exception as e:
        logger.error(f"RAG query error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi xử lý AI: {str(e)}"
        )


@router.post("/index", response_model=IndexResponse)
async def index_document(
    body: IndexRequest,
    current_user: Annotated[NguoiDung, Depends(require_admin)],
):
    """
    Index văn bản pháp luật mới vào Qdrant.
    Chỉ Admin mới được phép index.
    
    Luồng:
    1. Embed nội dung văn bản → vector
    2. Lưu vector + metadata vào Qdrant
    """
    try:
        # Tạo embedding cho nội dung văn bản
        vector = await embed_text(body.noi_dung)

        # Upsert vào Qdrant
        count = await upsert_documents([{
            "id": str(uuid.uuid4()),
            "vector": vector,
            "payload": {
                "ten_van_ban": body.ten_van_ban,
                "loai": body.loai,
                "dieu_khoan": body.dieu_khoan,
                "noi_dung": body.noi_dung,
                "url": body.url,
            }
        }])

        return IndexResponse(
            message=f"Đã index thành công: {body.ten_van_ban}",
            indexed_count=count,
        )
    except Exception as e:
        logger.error(f"Index error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi index văn bản: {str(e)}"
        )


@router.get("/stats")
async def get_stats(
    current_user: Annotated[NguoiDung, Depends(get_current_user)],
):
    """Thống kê số lượng văn bản đã index trong Qdrant."""
    try:
        info = await get_collection_info()
        return {
            "collection": "van_ban_phap_luat",
            "vectors_count": info["vectors_count"],
            "status": info["status"],
        }
    except Exception as e:
        return {"collection": "van_ban_phap_luat", "vectors_count": 0, "status": "error"}