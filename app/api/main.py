from fastapi import FastAPI
from pydantic import BaseModel

from app.agents.router import route_query
from app.agents.workflow import agent_graph

from app.retrieval.vector_retriever import retrieve_vector_context
from app.retrieval.sql_retriever import retrieve_sql_context
from app.retrieval.qdrant_retriever import retrieve_qdrant_context

from app.services.retrieval_service import retrieve_context
from app.services.answer_service import generate_grounded_answer
from app.services.llm_service import generate_llm_answer
from app.services.memory_service import (
    save_message,
    get_conversation,
    clear_conversation,
)


app = FastAPI(
    title="Enterprise Agentic RAG API",
    version="0.2.0",
)


class QueryRequest(BaseModel):
    query: str


class AgentQueryRequest(BaseModel):
    session_id: str
    query: str


@app.get("/")
def root():
    return {
        "message": "Enterprise Agentic RAG API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/route")
def route(request: QueryRequest):
    state = {
        "query": request.query,
        "rewritten_query": None,
        "route": None,
        "vector_results": [],
        "sql_results": {},
        "combined_context": "",
        "conversation_history": [],
        "answer": None,
        "confidence": 0.0,
        "retry_count": 0,
    }

    result = route_query(state)

    return {
        "query": result["query"],
        "route": result["route"],
    }


@app.post("/retrieve/vector")
def retrieve_vector(request: QueryRequest):
    results = retrieve_vector_context(
        request.query
    )

    return {
        "query": request.query,
        "results": results,
        "count": len(results),
    }


@app.post("/retrieve/qdrant")
def retrieve_qdrant(request: QueryRequest):
    results = retrieve_qdrant_context(
        request.query
    )

    return {
        "query": request.query,
        "results": results,
        "count": len(results),
    }


@app.post("/retrieve/sql")
def retrieve_sql(request: QueryRequest):
    results = retrieve_sql_context(
        request.query
    )

    return {
        "query": request.query,
        "results": results,
    }


@app.post("/retrieve")
def retrieve(request: QueryRequest):
    state = {
        "query": request.query,
        "rewritten_query": None,
        "route": None,
        "vector_results": [],
        "sql_results": {},
        "combined_context": "",
        "conversation_history": [],
        "answer": None,
        "confidence": 0.0,
        "retry_count": 0,
    }

    routed_state = route_query(state)

    context = retrieve_context(
        query=request.query,
        route=routed_state["route"],
    )

    return {
        "query": request.query,
        "route": routed_state["route"],
        "context": context,
    }


@app.post("/ask")
def ask(request: QueryRequest):
    state = {
        "query": request.query,
        "rewritten_query": None,
        "route": None,
        "vector_results": [],
        "sql_results": {},
        "combined_context": "",
        "conversation_history": [],
        "answer": None,
        "confidence": 0.0,
        "retry_count": 0,
    }

    routed_state = route_query(state)

    context = retrieve_context(
        query=request.query,
        route=routed_state["route"],
    )

    answer = generate_grounded_answer(
        query=request.query,
        context=context,
    )

    return {
        "query": request.query,
        "route": routed_state["route"],
        "context": context,
        "answer": answer,
    }


@app.post("/ask/llm")
def ask_llm(request: QueryRequest):
    state = {
        "query": request.query,
        "rewritten_query": None,
        "route": None,
        "vector_results": [],
        "sql_results": {},
        "combined_context": "",
        "conversation_history": [],
        "answer": None,
        "confidence": 0.0,
        "retry_count": 0,
    }

    routed_state = route_query(state)

    context = retrieve_context(
        query=request.query,
        route=routed_state["route"],
    )

    answer = generate_llm_answer(
        query=request.query,
        context=context,
    )

    return {
        "query": request.query,
        "route": routed_state["route"],
        "context": context,
        "answer": answer,
    }


@app.post("/agent/ask")
def agent_ask(request: AgentQueryRequest):
    conversation_history = get_conversation(
        request.session_id
    )

    initial_state = {
        "query": request.query,
        "rewritten_query": None,
        "route": None,
        "vector_results": [],
        "sql_results": {},
        "combined_context": "",
        "conversation_history": conversation_history,
        "answer": None,
        "confidence": 0.0,
        "retry_count": 0,
    }

    result = agent_graph.invoke(
        initial_state
    )

    save_message(
        session_id=request.session_id,
        role="user",
        content=request.query,
    )

    save_message(
        session_id=request.session_id,
        role="assistant",
        content=result["answer"] or "",
    )

    return {
        "session_id": request.session_id,
        "query": result["query"],
        "rewritten_query": result.get(
            "rewritten_query"
        ),
        "route": result["route"],
        "vector_results": result["vector_results"],
        "sql_results": result["sql_results"],
        "answer": result["answer"],
        "confidence": result["confidence"],
        "retry_count": result["retry_count"],
        "history_messages_used": len(
            conversation_history
        ),
    }


@app.get("/agent/history/{session_id}")
def agent_history(session_id: str):
    history = get_conversation(
        session_id
    )

    return {
        "session_id": session_id,
        "messages": history,
        "count": len(history),
    }


@app.delete("/agent/history/{session_id}")
def delete_agent_history(session_id: str):
    clear_conversation(
        session_id
    )

    return {
        "session_id": session_id,
        "message": "Conversation history cleared",
    }