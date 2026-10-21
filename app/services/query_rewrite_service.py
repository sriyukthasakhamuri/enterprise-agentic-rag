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
You are improving a retrieval query for an enterprise RAG system.

Original query:
{original_query}

Previous answer:
{answer}

Rewrite the query so semantic retrieval can find more useful evidence.

Rules:
- Preserve the original intent.
- Do not invent companies, industries, dates, metrics, people, or facts.
- Do not add placeholders such as [company] or [industry].
- Do not assume information the user did not provide.
- Make the query clearer and more searchable.
- Return only one rewritten query.
"""

    response = llm.invoke(prompt)

    rewritten_query = response.content.strip()

    if not rewritten_query:
        return original_query

    return rewritten_query