# src/rag/retriever.py
# Retriever: nhận câu hỏi → tìm văn bản pháp luật liên quan
# Đây là bước "R" trong RAG (Retrieval-Augmented Generation)

from loguru import logger
from src.rag.embeddings import embed_text
from src.rag.vector_store import search_similar


async def retrieve(
    query: str,
    top_k: int = 5,
    filter_loai: str = None,
    min_score: float = 0.3,
) -> list[dict]:
    """
    Tìm các đoạn văn bản pháp luật liên quan đến câu hỏi.
    
    Luồng xử lý:
    1. Embed câu hỏi → vector
    2. Tìm top_k vectors gần nhất trong Qdrant
    3. Lọc bỏ kết quả có score thấp (< min_score)
    
    min_score=0.3: loại bỏ kết quả không liên quan
    (score < 0.3 = gần như không liên quan)
    
    Ví dụ:
        results = await retrieve("Điều kiện đăng ký kết hôn là gì?")
        # → [{noi_dung: "Theo Luật HN&GĐ...", score: 0.87}, ...]
    """
    try:
        # Bước 1: Chuyển câu hỏi thành vector
        query_vector = await embed_text(query)

        # Bước 2: Tìm kiếm trong Qdrant
        results = await search_similar(
            query_vector=query_vector,
            top_k=top_k,
            filter_loai=filter_loai,
        )

        # Bước 3: Lọc kết quả không đủ liên quan
        filtered = [r for r in results if r["score"] >= min_score]

        logger.info(
            f"Retrieve: '{query[:50]}...' → "
            f"{len(filtered)}/{len(results)} results (min_score={min_score})"
        )
        return filtered

    except Exception as e:
        logger.error(f"Retrieve error: {e}")
        return []