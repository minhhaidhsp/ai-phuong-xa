"""
src/api/ragas.py
Sprint 8 — RAGAS evaluation endpoints
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import require_role
from src.db.models import NguoiDung
from src.rag.ragas_eval import evaluate_rag_sample, run_full_eval
from loguru import logger

router = APIRouter(prefix="/api/v1/ragas", tags=["RAGAS Evaluation"])


# ── Schemas ───────────────────────────────────────────────────────────────

class EvalSampleRequest(BaseModel):
    question: str
    answer: str
    contexts: list[str]
    ground_truth: Optional[str] = None


class EvalSampleItem(BaseModel):
    question: str
    ground_truth: Optional[str] = None
    answer: Optional[str] = None
    contexts: Optional[list[str]] = None


class RunFullEvalRequest(BaseModel):
    test_set: list[EvalSampleItem]


# ── Endpoints ─────────────────────────────────────────────────────────────

@router.post("/evaluate-sample")
async def evaluate_sample(
    req: EvalSampleRequest,
    current_user: NguoiDung = Depends(require_role(["admin"])),
):
    """
    Đánh giá 1 sample RAG với 4 RAGAS metrics.
    Chỉ admin mới được dùng (tránh tốn tài nguyên LLM).
    """
    try:
        result = await evaluate_rag_sample(
            question=req.question,
            answer=req.answer,
            contexts=req.contexts,
            ground_truth=req.ground_truth,
        )
        return {"status": "ok", "data": result}
    except Exception as e:
        logger.error(f"RAGAS evaluate error: {e}")
        raise HTTPException(500, f"Lỗi đánh giá: {str(e)}")


@router.post("/run-eval")
async def run_evaluation(
    req: RunFullEvalRequest,
    current_user: NguoiDung = Depends(require_role(["admin"])),
):
    """
    Chạy đánh giá toàn bộ test set.
    Nếu sample chưa có answer/contexts → tự gọi RAG pipeline.
    Cảnh báo: mỗi sample tốn ~4 LLM calls, tổng có thể lâu.
    """
    if len(req.test_set) > 20:
        raise HTTPException(400, "Tối đa 20 samples mỗi lần đánh giá")

    try:
        test_set = [item.model_dump(exclude_none=True) for item in req.test_set]
        result = await run_full_eval(test_set)
        return {"status": "ok", "data": result}
    except Exception as e:
        logger.error(f"RAGAS full eval error: {e}")
        raise HTTPException(500, f"Lỗi đánh giá: {str(e)}")


@router.get("/test-set")
async def get_default_test_set(
    current_user: NguoiDung = Depends(require_role(["admin"])),
):
    """
    Trả về bộ câu hỏi test mẫu để dùng với /run-eval.
    Cán bộ có thể copy và thêm ground_truth vào.
    """
    default_questions = [
        {
            "question": "Điều kiện đăng ký kết hôn theo pháp luật Việt Nam là gì?",
            "ground_truth": None,
        },
        {
            "question": "Thủ tục đăng ký thường trú cần những giấy tờ nào?",
            "ground_truth": None,
        },
        {
            "question": "Thời hạn giải quyết hồ sơ đăng ký khai sinh là bao nhiêu ngày?",
            "ground_truth": None,
        },
        {
            "question": "Nghị định 61/2018/NĐ-CP quy định gì về cơ chế một cửa?",
            "ground_truth": None,
        },
        {
            "question": "Phí xử lý hồ sơ hộ tịch tại phường là bao nhiêu?",
            "ground_truth": None,
        },
    ]
    return {
        "status": "ok",
        "message": "Thêm 'ground_truth' vào mỗi câu hỏi trước khi gửi /run-eval",
        "data": default_questions,
    }
