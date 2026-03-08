"""
src/rag/ragas_eval.py
Sprint 8 — Đánh giá chất lượng RAG pipeline bằng RAGAS metrics
Chạy offline, không cần internet, dùng Ollama local.

Metrics:
  - Faithfulness:    câu trả lời có bịa hay không (dựa trên context)
  - Answer Relevancy: câu trả lời có liên quan câu hỏi không
  - Context Recall:  context có đủ thông tin để trả lời không
  - Context Precision: context có nhiều nhiễu không

Cách dùng:
  from src.rag.ragas_eval import evaluate_rag_sample, run_full_eval
"""
from __future__ import annotations

import json
import re
from datetime import datetime
from typing import Optional
import httpx
from loguru import logger

from src.core.config import settings


# ── Ollama helper ─────────────────────────────────────────────────────────

async def _llm_judge(prompt: str, system: str = "") -> str:
    """Gọi Ollama để judge — trả về text response."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            f"{settings.OLLAMA_BASE_URL}/api/chat",
            json={
                "model": settings.LLM_MODEL_FAST,
                "messages": messages,
                "stream": False,
                "options": {"temperature": 0.0, "num_ctx": 4096},
            },
        )
        resp.raise_for_status()
        return resp.json()["message"]["content"].strip()


def _parse_score(text: str) -> float:
    """Extract score 0.0-1.0 từ LLM response."""
    # Tìm số thập phân đầu tiên trong text
    matches = re.findall(r"\b(0\.\d+|1\.0|0|1)\b", text)
    if matches:
        score = float(matches[0])
        return min(max(score, 0.0), 1.0)
    # Fallback: tìm điểm / 10
    match10 = re.search(r"(\d+)\s*/\s*10", text)
    if match10:
        return min(float(match10.group(1)) / 10, 1.0)
    return 0.5  # unknown → trung bình


# ── Individual metrics ────────────────────────────────────────────────────

async def score_faithfulness(answer: str, contexts: list[str]) -> dict:
    """
    Faithfulness: câu trả lời có được hỗ trợ bởi context không?
    Score 1.0 = hoàn toàn dựa context, 0.0 = tự bịa hoàn toàn.
    """
    context_text = "\n---\n".join(contexts[:5])
    prompt = f"""Bạn là chuyên gia đánh giá AI.

NGỮ CẢNH (context):
{context_text}

CÂU TRẢ LỜI CỦA AI:
{answer}

Nhiệm vụ: Đánh giá xem câu trả lời có hoàn toàn dựa trên ngữ cảnh không, hay có thông tin bịa thêm không có trong ngữ cảnh.

Cho điểm từ 0.0 đến 1.0:
- 1.0: Mọi thông tin trong câu trả lời đều có trong ngữ cảnh
- 0.5: Một phần dựa ngữ cảnh, một phần suy luận
- 0.0: Câu trả lời không liên quan hoặc bịa hoàn toàn

Chỉ trả lời bằng một số thập phân duy nhất (ví dụ: 0.8)"""

    raw = await _llm_judge(prompt)
    score = _parse_score(raw)
    return {"metric": "faithfulness", "score": score, "raw": raw}


async def score_answer_relevancy(question: str, answer: str) -> dict:
    """
    Answer Relevancy: câu trả lời có đúng trọng tâm câu hỏi không?
    """
    prompt = f"""Bạn là chuyên gia đánh giá AI.

CÂU HỎI: {question}

CÂU TRẢ LỜI: {answer}

Đánh giá mức độ liên quan của câu trả lời với câu hỏi.

Cho điểm từ 0.0 đến 1.0:
- 1.0: Câu trả lời trả lời đúng và đầy đủ câu hỏi
- 0.5: Câu trả lời liên quan nhưng không đầy đủ hoặc lạc đề một phần
- 0.0: Câu trả lời không liên quan đến câu hỏi

Chỉ trả lời bằng một số thập phân duy nhất (ví dụ: 0.9)"""

    raw = await _llm_judge(prompt)
    score = _parse_score(raw)
    return {"metric": "answer_relevancy", "score": score, "raw": raw}


async def score_context_recall(question: str, answer: str, contexts: list[str]) -> dict:
    """
    Context Recall: context có đủ thông tin để tạo ra câu trả lời không?
    """
    context_text = "\n---\n".join(contexts[:5])
    prompt = f"""Bạn là chuyên gia đánh giá AI.

CÂU HỎI: {question}

NGỮ CẢNH ĐƯỢC TRUY XUẤT:
{context_text}

CÂU TRẢ LỜI ĐÚNG (ground truth):
{answer}

Đánh giá xem ngữ cảnh có chứa đủ thông tin để trả lời câu hỏi không.

Cho điểm từ 0.0 đến 1.0:
- 1.0: Ngữ cảnh chứa đầy đủ thông tin cần thiết
- 0.5: Ngữ cảnh có một phần thông tin nhưng thiếu chi tiết quan trọng
- 0.0: Ngữ cảnh không có thông tin liên quan

Chỉ trả lời bằng một số thập phân duy nhất (ví dụ: 0.7)"""

    raw = await _llm_judge(prompt)
    score = _parse_score(raw)
    return {"metric": "context_recall", "score": score, "raw": raw}


async def score_context_precision(question: str, contexts: list[str]) -> dict:
    """
    Context Precision: tỷ lệ context thực sự liên quan trong số đã retrieve.
    """
    relevant_count = 0
    for ctx in contexts[:5]:
        prompt = f"""Câu hỏi: {question}

Đoạn văn bản: {ctx[:500]}

Đoạn văn bản này có liên quan và hữu ích để trả lời câu hỏi không?
Chỉ trả lời: có hoặc không"""
        raw = await _llm_judge(prompt)
        if any(w in raw.lower() for w in ["có", "yes", "relevant", "liên quan", "hữu ích"]):
            relevant_count += 1

    total = len(contexts[:5])
    score = relevant_count / total if total > 0 else 0.0
    return {
        "metric": "context_precision",
        "score": round(score, 2),
        "relevant": relevant_count,
        "total": total,
    }


# ── Main evaluation function ──────────────────────────────────────────────

async def evaluate_rag_sample(
    question: str,
    answer: str,
    contexts: list[str],
    ground_truth: Optional[str] = None,
) -> dict:
    """
    Đánh giá 1 sample RAG với 4 metrics.

    Args:
        question: Câu hỏi gốc
        answer: Câu trả lời của AI
        contexts: Danh sách đoạn văn bản đã retrieve
        ground_truth: Câu trả lời đúng (nếu có, dùng cho context_recall)

    Returns:
        {
          "question": ...,
          "scores": { faithfulness, answer_relevancy, context_recall, context_precision },
          "overall": float,
          "grade": "A/B/C/D/F"
        }
    """
    logger.info(f"RAGAS evaluating: {question[:60]}...")

    ref_answer = ground_truth or answer

    f_result = await score_faithfulness(answer, contexts)
    ar_result = await score_answer_relevancy(question, answer)
    cr_result = await score_context_recall(question, ref_answer, contexts)
    cp_result = await score_context_precision(question, contexts)

    scores = {
        "faithfulness": f_result["score"],
        "answer_relevancy": ar_result["score"],
        "context_recall": cr_result["score"],
        "context_precision": cp_result["score"],
    }
    overall = round(sum(scores.values()) / len(scores), 3)

    grade = "A" if overall >= 0.8 else \
            "B" if overall >= 0.65 else \
            "C" if overall >= 0.5 else \
            "D" if overall >= 0.35 else "F"

    return {
        "question": question,
        "answer_preview": answer[:200],
        "n_contexts": len(contexts),
        "scores": scores,
        "overall": overall,
        "grade": grade,
        "evaluated_at": datetime.now().isoformat(),
    }


async def run_full_eval(test_set: list[dict]) -> dict:
    """
    Chạy đánh giá toàn bộ test set.

    test_set format:
    [
      {
        "question": "...",
        "ground_truth": "...",  # optional
        "answer": "...",        # nếu đã có sẵn, không cần gọi RAG
      }
    ]

    Nếu "answer" chưa có, sẽ gọi RAG pipeline để lấy.
    """
    from src.rag.pipeline import rag_query

    results = []
    for item in test_set:
        question = item["question"]
        ground_truth = item.get("ground_truth")

        # Lấy answer + contexts từ RAG nếu chưa có
        if "answer" in item and "contexts" in item:
            answer = item["answer"]
            contexts = item["contexts"]
        else:
            rag_result = await rag_query(question)
            answer = rag_result["answer"]
            contexts = [s.get("noi_dung", s.get("ten_van_ban", "")) 
                       for s in rag_result.get("sources", [])]

        result = await evaluate_rag_sample(question, answer, contexts, ground_truth)
        results.append(result)
        logger.info(f"  → Overall: {result['overall']} ({result['grade']})")

    # Aggregate stats
    if results:
        avg_scores = {}
        for metric in ["faithfulness", "answer_relevancy", "context_recall", "context_precision"]:
            avg_scores[metric] = round(
                sum(r["scores"][metric] for r in results) / len(results), 3
            )
        avg_overall = round(sum(r["overall"] for r in results) / len(results), 3)
        grade_dist = {}
        for r in results:
            grade_dist[r["grade"]] = grade_dist.get(r["grade"], 0) + 1
    else:
        avg_scores = {}
        avg_overall = 0.0
        grade_dist = {}

    return {
        "summary": {
            "total_samples": len(results),
            "avg_scores": avg_scores,
            "avg_overall": avg_overall,
            "grade_distribution": grade_dist,
            "evaluated_at": datetime.now().isoformat(),
        },
        "details": results,
    }
