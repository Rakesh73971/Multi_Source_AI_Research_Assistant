from typing import Any, Literal, TypedDict

from langgraph.graph import END, StateGraph

from app.rag.qa_service import generate_answer
from app.rag.vector_store import retrieve_relevant_chunks


class ResearchAgentState(TypedDict):
    collection_name: str
    question: str
    top_k: int
    route: Literal["retrieve", "answer_without_context"]
    chunks: list[dict[str, Any]]
    answer: str


def route_question(state: ResearchAgentState) -> ResearchAgentState:
    question = state["question"].strip()
    route: Literal["retrieve", "answer_without_context"] = (
        "retrieve" if question else "answer_without_context"
    )
    return {**state, "route": route}


def retrieve_context(state: ResearchAgentState) -> ResearchAgentState:
    chunks = retrieve_relevant_chunks(
        collection_name=state["collection_name"],
        question=state["question"],
        top_k=state["top_k"],
    )
    return {**state, "chunks": chunks}


def check_confidence(state: ResearchAgentState) -> str:
    if not state["chunks"]:
        return "answer_without_context"

    best_score = min(chunk["score"] for chunk in state["chunks"])
    return "generate" if best_score <= 1.2 else "answer_without_context"


def generate_response(state: ResearchAgentState) -> ResearchAgentState:
    answer = generate_answer(state["question"], state["chunks"])
    return {**state, "answer": answer}


def answer_without_context(state: ResearchAgentState) -> ResearchAgentState:
    return {
        **state,
        "chunks": [],
        "answer": "I could not find enough relevant context in the uploaded sources.",
    }


def build_research_graph():
    graph = StateGraph(ResearchAgentState)
    graph.add_node("router", route_question)
    graph.add_node("retriever", retrieve_context)
    graph.add_node("generator", generate_response)
    graph.add_node("fallback", answer_without_context)

    graph.set_entry_point("router")
    graph.add_conditional_edges(
        "router",
        lambda state: state["route"],
        {
            "retrieve": "retriever",
            "answer_without_context": "fallback",
        },
    )
    graph.add_conditional_edges(
        "retriever",
        check_confidence,
        {
            "generate": "generator",
            "answer_without_context": "fallback",
        },
    )
    graph.add_edge("generator", END)
    graph.add_edge("fallback", END)
    return graph.compile()


research_graph = build_research_graph()


def run_research_agent(collection_name: str, question: str, top_k: int = 4) -> dict[str, Any]:
    return research_graph.invoke(
        {
            "collection_name": collection_name,
            "question": question,
            "top_k": top_k,
            "route": "retrieve",
            "chunks": [],
            "answer": "",
        }
    )
