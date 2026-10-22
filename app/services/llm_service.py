from typing import Dict, Any, List

from langchain_ollama import ChatOllama


llm = ChatOllama(
    model="llama3.2:3b",
    temperature=0,
)


def generate_llm_answer(
    query: str,
    context: Dict[str, Any],
    conversation_history: List[Dict[str, str]] | None = None,
) -> str:
    vector_results = context.get(
        "vector_results",
        [],
    )

    sql_results = context.get(
        "sql_results",
        {},
    )

    conversation_history = conversation_history or []

    history_text = "\n".join(
        f"{message['role']}: {message['content']}"
        for message in conversation_history
    )

    prompt = f"""
You are an enterprise analytics assistant.

Answer the user's question using ONLY:
1. The retrieved evidence.
2. Relevant conversation history.

Do not invent facts, causes, metrics, or relationships.

If the retrieved evidence is insufficient, clearly say so.

Conversation history:
{history_text if history_text else "No previous conversation."}

Current user question:
{query}

Structured metrics:
{sql_results}

Retrieved knowledge:
{vector_results}

Important:
- Use conversation history only to understand references and follow-up questions.
- Do not treat previous assistant statements as verified evidence.
- Ground factual claims in the retrieved knowledge or structured metrics.
- Return a concise business-friendly answer.
"""

    response = llm.invoke(prompt)

    return response.content