from langchain_google_genai import ChatGoogleGenerativeAI

from app.db.config import settings


CHAT_MODEL = "gemini-1.5-flash"


def build_context(chunks: list[dict]) -> str:
    context_blocks = []
    for index, chunk in enumerate(chunks, start=1):
        metadata = chunk["metadata"]
        source_id = metadata.get("source_id")
        chunk_index = metadata.get("chunk_index")
        source_title = metadata.get("source_title", "Unknown source")
        context_blocks.append(
            "\n".join(
                [
                    f"Source {index}",
                    f"source_id: {source_id}",
                    f"chunk_index: {chunk_index}",
                    f"title: {source_title}",
                    "content:",
                    chunk["content"],
                ]
            )
        )
    return "\n\n---\n\n".join(context_blocks)


def generate_answer(question: str, chunks: list[dict]) -> str:
    if not chunks:
        return "I could not find relevant context in the uploaded sources."

    llm = ChatGoogleGenerativeAI(
        model=CHAT_MODEL,
        google_api_key=settings.google_api_key,
        temperature=0.2,
    )

    prompt = f"""
You are a research assistant. Answer the user's question using only the provided context.
If the context is not enough, say that the uploaded sources do not contain enough information.
Include concise source citations using source_id and chunk_index.

Question:
{question}

Context:
{build_context(chunks)}
"""
    response = llm.invoke(prompt)
    return response.content
