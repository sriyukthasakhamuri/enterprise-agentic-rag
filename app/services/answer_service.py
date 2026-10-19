from typing import Dict, Any


def generate_grounded_answer(
    query: str,
    context: Dict[str, Any],
) -> str:
    vector_results = context.get("vector_results", [])
    sql_results = context.get("sql_results", {})

    answer_parts = []

    if sql_results:
        answer_parts.append("Structured metrics:")

        for key, value in sql_results.items():
            readable_key = key.replace("_", " ").title()
            answer_parts.append(
                f"- {readable_key}: {value}"
            )

    if vector_results:
        answer_parts.append(
            "\nRelevant knowledge:"
        )

        for result in vector_results:
            answer_parts.append(
                f"- {result}"
            )

    if not answer_parts:
        return (
            "I could not find enough grounded "
            "information to answer this query."
        )

    return "\n".join(answer_parts)