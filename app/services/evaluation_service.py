from typing import Dict, Any


def evaluate_answer(
    query: str,
    context: Dict[str, Any],
    answer: str,
    route: str | None = None,
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

    answer_lower = answer.lower().strip()

    # Basic answer quality
    if len(answer_lower) > 20:
        score += 0.30

    # Score evidence according to the route
    if route == "vector":
        if vector_results:
            score += 0.50

    elif route == "sql":
        if sql_results:
            score += 0.50

    elif route == "both":
        if vector_results:
            score += 0.25

        if sql_results:
            score += 0.25

    else:
        if vector_results:
            score += 0.25

        if sql_results:
            score += 0.25

    # Reward safe refusal when evidence is insufficient
    insufficient_phrases = [
        "not enough evidence",
        "not enough information",
        "insufficient evidence",
        "cannot determine",
    ]

    if any(
        phrase in answer_lower
        for phrase in insufficient_phrases
    ):
        score += 0.20

    return min(score, 1.0)