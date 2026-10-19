from typing import Dict, Any

from langchain_ollama import ChatOllama


llm = ChatOllama(
    model="llama3.2:3b",
    temperature=0,
)


def generate_llm_answer(
    query: str,
    context: Dict[str, Any],
) -> str:
    vector_results = context.get(
        "vector_results",
        [],
    )

    sql_results = context.get(
        "sql_results",
        {},
    )

    prompt = f"""
You are an enterprise analytics assistant.

Answer the user's question using ONLY the
retrieved context below.

Do not invent facts, causes, metrics, or
relationships that are not supported by
the provided context.

If the context is insufficient, clearly
say there is not enough evidence.

User question:
{query}

Structured metrics:
{sql_results}

Retrieved knowledge:
{vector_results}

Return a concise business-friendly answer.
"""

    response = llm.invoke(prompt)

    return response.content