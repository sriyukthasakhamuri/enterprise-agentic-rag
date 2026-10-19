from typing import Dict, Any

from app.retrieval.vector_retriever import retrieve_vector_context
from app.retrieval.sql_retriever import retrieve_sql_context


def retrieve_context(query: str, route: str) -> Dict[str, Any]:
    vector_results = []
    sql_results = {}

    if route in ["vector", "both"]:
        vector_results = retrieve_vector_context(query)

    if route in ["sql", "both"]:
        sql_results = retrieve_sql_context(query)

    combined_context = {
        "vector_results": vector_results,
        "sql_results": sql_results,
    }

    return combined_context