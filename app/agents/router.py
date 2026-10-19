from app.agents.state import AgentState


def route_query(state: AgentState) -> AgentState:
    query = state["query"].lower()

    sql_keywords = [
      "count",
      "average",
      "sum",
      "total",
      "revenue",
      "sales",
      "top",
      "highest",
      "lowest",
      "how many",
    ]
   

    vector_keywords = [
        "explain",
        "why",
        "policy",
        "document",
        "meaning",
        "describe",
        "recommend",
        "cause",
    ]

    has_sql_signal = any(
        keyword in query
        for keyword in sql_keywords
    )

    has_vector_signal = any(
        keyword in query
        for keyword in vector_keywords
    )

    if has_sql_signal and has_vector_signal:
        route = "both"
    elif has_sql_signal:
        route = "sql"
    elif has_vector_signal:
        route = "vector"
    else:
        route = "both"

    state["route"] = route

    return state