from typing import TypedDict, List, Optional


class AgentState(TypedDict):
    query: str

    route: Optional[str]

    vector_results: List[str]
    sql_results: List[str]

    combined_context: str

    answer: Optional[str]

    confidence: float

    retry_count: int