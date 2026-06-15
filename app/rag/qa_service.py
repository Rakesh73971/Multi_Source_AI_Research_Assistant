from langchain_google_genai import ChatGoogleGenerativeAI

from app.db.config import settings


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


def generate_answer(
    question: str, chunks: list[dict], chat_history: list[dict] = None
) -> str:
    if not chunks:
        return "I could not find relevant context in the uploaded sources."

    llm = ChatGoogleGenerativeAI(
        model=settings.gemini_chat_model,
        google_api_key=settings.google_api_key,
        temperature=0.2,
    )

    history_blocks = []
    if chat_history:
        for msg in chat_history:
            role = "User" if msg.get("role") == "user" else "Assistant"
            content = msg.get("content", "")
            history_blocks.append(f"{role}: {content}")
    history_str = "\n".join(history_blocks)

    prompt = f"""
You are a research assistant. Answer the user's question using only the provided context.
If the context is not enough, say that the uploaded sources do not contain enough information.
Include concise source citations using source_id and chunk_index.

Chat History:
{history_str}

Question:
{question}

Context:
{build_context(chunks)}
"""
    response = llm.invoke(prompt)
    return response.content
