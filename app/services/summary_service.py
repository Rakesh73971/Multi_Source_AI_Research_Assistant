from langchain_classic.chains.summarize import load_summarize_chain
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.documents import Document
from app.db.config import settings


def generate_map_reduce_summary(docs: list[Document]) -> str:
    if not docs:
        return ""

    llm = ChatGoogleGenerativeAI(
        model=settings.gemini_chat_model,
        google_api_key=settings.google_api_key,
        temperature=0.2,
    )

    # Map phase prompt: summarizes individual text chunks
    map_template = """Write a concise summary of the following text:
"{text}"
CONCISE SUMMARY:"""
    map_prompt = PromptTemplate.from_template(map_template)

    # Reduce phase prompt: combines the summaries into exactly 5 bullet points
    reduce_template = """The following is a set of summaries of research documents:
{text}
Take these and distill them into a unified, high-level summary of the research topic in exactly 5 bullet points:
UNIFIED SUMMARY:"""
    reduce_prompt = PromptTemplate.from_template(reduce_template)

    # Load the Map-Reduce summarization chain
    chain = load_summarize_chain(
        llm=llm,
        chain_type="map_reduce",
        map_prompt=map_prompt,
        combine_prompt=reduce_prompt,
    )

    result = chain.invoke(docs)
    return result.get("output_text", "").strip()
