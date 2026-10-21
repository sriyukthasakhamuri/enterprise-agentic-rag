from langchain_ollama import ChatOllama


llm = ChatOllama(
    model="llama3.2:3b",
    temperature=0,
)


def rewrite_query(
    original_query: str,
    answer: str,
) -> str:
    prompt = f"""
You are improving a search query for an enterprise RAG system.

Original query:
{original_query}

Previous answer:
{answer}

Rewrite the query so retrieval can find more specific and useful evidence.

Rules:
- Keep the original intent.
- Do not invent facts.
- Make the query clearer and more specific.
- Return only the rewritten query.
"""

    response = llm.invoke(prompt)

    return response.content.strip()