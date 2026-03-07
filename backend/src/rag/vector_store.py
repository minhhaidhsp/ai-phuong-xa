from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance, VectorParams,
    PointStruct, Filter, FieldCondition, MatchValue,
)
from loguru import logger
from src.core.config import get_settings
from src.rag.embeddings import EMBEDDING_DIM

settings = get_settings()
COLLECTION_NAME = "van_ban_phap_luat"


def get_qdrant_client() -> AsyncQdrantClient:
    return AsyncQdrantClient(
        host=settings.QDRANT_HOST,
        port=settings.QDRANT_PORT,
        timeout=30,
        check_compatibility=False,
    )


async def init_collection():
    client = get_qdrant_client()
    try:
        exists = await client.collection_exists(COLLECTION_NAME)
        if not exists:
            await client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=EMBEDDING_DIM,
                    distance=Distance.COSINE,
                ),
            )
            logger.info(f"Tao Qdrant collection: {COLLECTION_NAME}")
        else:
            logger.info(f"Qdrant collection da ton tai: {COLLECTION_NAME}")
    except Exception as e:
        logger.warning(f"Qdrant init warning: {e}")
    finally:
        await client.close()


async def upsert_documents(documents: list[dict]) -> int:
    client = get_qdrant_client()
    try:
        points = [
            PointStruct(
                id=doc["id"],
                vector=doc["vector"],
                payload=doc["payload"],
            )
            for doc in documents
        ]
        await client.upsert(
            collection_name=COLLECTION_NAME,
            points=points,
        )
        logger.info(f"Upsert {len(points)} documents vao Qdrant")
        return len(points)
    finally:
        await client.close()


async def search_similar(
    query_vector: list[float],
    top_k: int = 5,
    filter_loai: str = None,
) -> list[dict]:
    client = get_qdrant_client()
    try:
        search_filter = None
        if filter_loai:
            search_filter = Filter(
                must=[FieldCondition(
                    key="loai",
                    match=MatchValue(value=filter_loai)
                )]
            )
        results = await client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            limit=top_k,
            query_filter=search_filter,
            with_payload=True,
        )
        return [
            {
                "noi_dung": r.payload.get("noi_dung", ""),
                "ten_van_ban": r.payload.get("ten_van_ban", ""),
                "loai": r.payload.get("loai", ""),
                "dieu_khoan": r.payload.get("dieu_khoan", ""),
                "url": r.payload.get("url", ""),
                "score": r.score,
            }
            for r in results
        ]
    finally:
        await client.close()


async def get_collection_info() -> dict:
    client = get_qdrant_client()
    try:
        info = await client.get_collection(COLLECTION_NAME)
        # Tương thích cả version cũ và mới
        count = getattr(info, 'points_count', None) or getattr(info, 'vectors_count', None) or 0
        return {
            "vectors_count": count,
            "indexed_vectors_count": count,
            "status": str(info.status),
        }
    except Exception as e:
        return {"vectors_count": 0, "indexed_vectors_count": 0, "status": "error"}
    finally:
        await client.close()
