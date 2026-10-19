from app.services.llm_service import generate_llm_answer
from app.services.answer_service import generate_grounded_answer
from app.services.retrieval_service import retrieve_context
from app.retrieval.sql_retriever import retrieve_sql_context
from fastapi import FastAPI
from pydantic import BaseModel

from app.agents.router import route_query
from app.retrieval.vector_retriever import retrieve_vector_context


app = FastAPI(
    title="Enterprise Agentic RAG API",
    version="0.1.0",
)


class QueryRequest(BaseModel):
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
        "route": None,
        "vector_results": [],
        "sql_results": [],
        "combined_context": "",
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
        "route": None,
        "vector_results": [],
        "sql_results": [],
        "combined_context": "",
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
        "route": None,
        "vector_results": [],
        "sql_results": [],
        "combined_context": "",
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
        "route": None,
        "vector_results": [],
        "sql_results": [],
        "combined_context": "",
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