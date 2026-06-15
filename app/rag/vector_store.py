from pathlib import Path
from typing import Any
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from app.db.config import settings
from app.ingestion.text_splitter import TextChunk


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CHROMA_DIR = PROJECT_ROOT / "chroma_db"


def _get_embeddings():
    return GoogleGenerativeAIEmbeddings(
        model=settings.gemini_embedding_model,
        google_api_key=settings.google_api_key,
    )


def get_vector_store(collection_name: str) -> Chroma:
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    return Chroma(
        collection_name=collection_name,
        embedding_function=_get_embeddings(),
        persist_directory=str(CHROMA_DIR),
    )


def index_source_chunks(
    collection_name: str,
    source_id: int,
    source_title: str,
    chunks: list[TextChunk],
) -> int:
    if not chunks:
        return 0

    documents = [
        Document(
            page_content=chunk.content,
            metadata={
                "source_id": source_id,
                "source_title": source_title,
                "chunk_index": chunk.chunk_index,
            },
        )
        for chunk in chunks
    ]
    ids = [f"source_{source_id}_chunk_{chunk.chunk_index}" for chunk in chunks]

    vector_store = get_vector_store(collection_name)
    vector_store.add_documents(documents=documents, ids=ids)
    vector_store.persist()
    return len(documents)


def retrieve_relevant_chunks(
    collection_name: str,
    question: str,
    top_k: int = 4,
    source_id: int | None = None,
) -> list[dict[str, Any]]:
    vector_store = get_vector_store(collection_name)
    filter_query = {"source_id": source_id} if source_id is not None else None
    results = vector_store.similarity_search_with_score(
        question,
        k=top_k,
        filter=filter_query,
    )

    return [
        {
            "content": document.page_content,
            "score": score,
            "metadata": document.metadata,
        }
        for document, score in results
    ]


def get_all_documents_in_store(collection_name: str) -> list[Document]:
    vector_store = get_vector_store(collection_name)
    collection_data = vector_store._collection.get()
    documents_list = collection_data.get("documents", [])
    metadatas_list = collection_data.get("metadatas", []) or []

    docs = []
    for i, content in enumerate(documents_list):
        metadata = metadatas_list[i] if i < len(metadatas_list) else {}
        docs.append(Document(page_content=content, metadata=metadata))
    return docs
