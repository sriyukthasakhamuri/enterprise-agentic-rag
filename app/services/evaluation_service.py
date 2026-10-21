from typing import Dict, Any


def evaluate_answer(
    query: str,
    context: Dict[str, Any],
    answer: str,
) -> float:
    score = 0.0

    vector_results = context.get(
        "vector_results",
        [],
    )

    sql_results = context.get(
        "sql_results",
        {},
    )

    if answer and len(answer.strip()) > 20:
        score += 0.30

    if vector_results:
        score += 0.30

    if sql_results:
        score += 0.30

    if (
        "not enough evidence" in answer.lower()
        or "not enough information" in answer.lower()
    ):
        score += 0.10

    return min(score, 1.0)