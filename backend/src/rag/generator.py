# src/rag/generator.py
# Generator: nhận câu hỏi + context → sinh câu trả lời bằng LLM
# Đây là bước "G" trong RAG (Retrieval-Augmented Generation)
#
# LLM được cung cấp:
#   1. System prompt: vai trò và quy tắc trả lời
#   2. Context: các đoạn văn bản pháp luật liên quan (từ Retriever)
#   3. Question: câu hỏi của cán bộ
# → LLM tổng hợp và trả lời DỰA TRÊN context, không tự bịa

import ollama
from loguru import logger
from src.core.config import get_settings

settings = get_settings()

# System prompt định nghĩa vai trò và hành vi của AI
SYSTEM_PROMPT = """Bạn là trợ lý AI hành chính cho cán bộ phường/xã tại TP.HCM.

Nhiệm vụ: Trả lời câu hỏi về thủ tục hành chính, pháp luật dựa trên văn bản được cung cấp.

Quy tắc bắt buộc:
1. CHỈ trả lời dựa trên Context được cung cấp, không tự bịa thông tin
2. Trích dẫn rõ nguồn: "Theo [tên văn bản], [điều khoản]..."
3. Nếu không tìm thấy thông tin trong Context → nói rõ "Tôi không tìm thấy thông tin về vấn đề này trong cơ sở dữ liệu"
4. Dùng ngôn ngữ rõ ràng, dễ hiểu cho cán bộ hành chính
5. Trả lời bằng tiếng Việt"""


def _build_context_text(documents: list[dict]) -> str:
    """
    Ghép các đoạn văn bản thành context string để đưa vào LLM.
    
    Format:
        [1] Tên văn bản (Điều X)
        Nội dung...
        
        [2] Tên văn bản khác
        Nội dung...
    """
    if not documents:
        return "Không tìm thấy văn bản liên quan."

    parts = []
    for i, doc in enumerate(documents, 1):
        header = f"[{i}] {doc['ten_van_ban']}"
        if doc.get("dieu_khoan"):
            header += f" ({doc['dieu_khoan']})"
        parts.append(f"{header}\n{doc['noi_dung']}")

    return "\n\n".join(parts)


async def generate(
    question: str,
    documents: list[dict],
    stream: bool = False,
) -> dict:
    """
    Sinh câu trả lời từ LLM dựa trên câu hỏi và context.
    
    documents: kết quả từ retriever — danh sách văn bản liên quan
    stream: True → streaming response (chưa implement, để sau)
    
    Trả về:
        answer:    câu trả lời của LLM
        sources:   danh sách nguồn trích dẫn
        model:     tên model đã dùng
    """
    # Xây dựng context từ documents
    context = _build_context_text(documents)

    # Prompt kết hợp context + câu hỏi
    user_message = f"""Context (văn bản pháp luật liên quan):
{context}

Câu hỏi: {question}

Hãy trả lời câu hỏi dựa trên Context trên."""

    try:
        client = ollama.AsyncClient(host=settings.OLLAMA_BASE_URL)

        response = await client.chat(
            model=settings.LLM_MODEL_MAIN,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_message},
            ],
            options={
                "temperature": 0.1,  # Thấp → câu trả lời nhất quán, ít sáng tạo
                "num_ctx": 4096,     # Context window 4096 tokens
            },
        )

        answer = response.message.content

        # Trích xuất danh sách nguồn để hiển thị citation
        sources = [
            {
                "ten_van_ban": doc["ten_van_ban"],
                "dieu_khoan": doc.get("dieu_khoan", ""),
                "score": round(doc["score"], 3),
                "url": doc.get("url", ""),
            }
            for doc in documents
        ]

        return {
            "answer": answer,
            "sources": sources,
            "model": settings.LLM_MODEL_MAIN,
        }

    except Exception as e:
        logger.error(f"Generate error: {e}")
        raise