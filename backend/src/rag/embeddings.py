# src/rag/embeddings.py
# Tạo vector embeddings từ text dùng nomic-embed-text qua Ollama
# Embedding = chuyển text thành vector số học để so sánh ngữ nghĩa
# Ví dụ: "đăng ký kết hôn" và "thủ tục hôn nhân" → 2 vector gần nhau

import ollama
from loguru import logger
from src.core.config import get_settings

settings = get_settings()

# Kích thước vector của nomic-embed-text (cố định 768 chiều)
EMBEDDING_DIM = 768


async def embed_text(text: str) -> list[float]:
    """
    Tạo embedding vector cho 1 đoạn text.
    
    Dùng khi: index văn bản mới vào Qdrant
    
    Ví dụ:
        vector = await embed_text("Điều kiện đăng ký kết hôn")
        # → [0.123, -0.456, 0.789, ...] (768 số)
    """
    try:
        client = ollama.AsyncClient(host=settings.OLLAMA_BASE_URL)
        response = await client.embed(
            model=settings.EMBED_MODEL,
            input=text,
        )
        return response.embeddings[0]
    except Exception as e:
        logger.error(f"Embedding error: {e}")
        raise


async def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Tạo embeddings cho nhiều đoạn text cùng lúc (batch).
    
    Dùng khi: index nhiều văn bản một lúc → nhanh hơn gọi từng cái
    """
    try:
        client = ollama.AsyncClient(host=settings.OLLAMA_BASE_URL)
        response = await client.embed(
            model=settings.EMBED_MODEL,
            input=texts,
        )
        return response.embeddings
    except Exception as e:
        logger.error(f"Batch embedding error: {e}")
        raise