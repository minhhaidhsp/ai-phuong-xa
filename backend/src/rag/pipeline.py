from loguru import logger
from src.rag.retriever import retrieve
from src.rag.generator import generate


async def rag_query(
    question: str,
    top_k: int = 5,
    filter_loai: str = None,
    min_score: float = 0.0,  # nomic-embed-text tieng Viet score thap, de LLM tu loc
) -> dict:
    logger.info(f"RAG query: '{question[:80]}'")

    documents = await retrieve(
        query=question,
        top_k=top_k,
        filter_loai=filter_loai,
        min_score=min_score,
    )

    logger.info(f"Retrieved {len(documents)} relevant documents")

    result = await generate(
        question=question,
        documents=documents,
    )

    return {
        "question": question,
        "answer": result["answer"],
        "sources": result["sources"],
        "found_docs": len(documents),
        "model": result["model"],
    }
