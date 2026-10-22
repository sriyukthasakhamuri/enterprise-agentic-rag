from app.agents.state import AgentState


SQL_KEYWORDS = [
    "count",
    "how many",
    "average",
    "avg",
    "sum",
    "total",
    "revenue",
    "sales",
    "order value",
    "average order",
    "average order value",
    "total orders",
    "total customers",
    "customer count",
    "churn rate",
    "average delivery delay",
    "highest",
    "lowest",
    "top",
    "metric",
]


VECTOR_KEYWORDS = [
    "explain",
    "why",
    "reason",
    "reasons",
    "cause",
    "causes",
    "factor",
    "factors",
    "risk",
    "risks",
    "issue",
    "issues",
    "affect",
    "impact",
    "meaning",
    "describe",
    "policy",
    "guidance",
    "recommend",
    "recommendation",
    "retention",
    "loyalty",
    "support",
    "service quality",
    "customer satisfaction",
    "likely to churn",
    "cancel",
    "cancelling",
    "buy again",
]


def contains_any(
    query: str,
    keywords: list[str],
) -> bool:
    return any(
        keyword in query
        for keyword in keywords
    )


def route_query(
    state: AgentState,
) -> AgentState:

    query = state["query"].lower().strip()

    has_sql_signal = contains_any(
        query,
        SQL_KEYWORDS,
    )

    has_vector_signal = contains_any(
        query,
        VECTOR_KEYWORDS,
    )

    if (
        has_sql_signal
        and has_vector_signal
    ):
        state["route"] = "both"

    elif has_sql_signal:
        state["route"] = "sql"

    elif has_vector_signal:
        state["route"] = "vector"

    else:
        state["route"] = "vector"

    return state