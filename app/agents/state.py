from typing import TypedDict, List, Optional, Dict, Any


class AgentState(TypedDict):
    query: str
    rewritten_query: Optional[str]

    route: Optional[str]

    vector_results: List[str]
    sql_results: Dict[str, Any]

    combined_context: str
    conversation_history: List[Dict[str, str]]

    answer: Optional[str]

    confidence: float
    retry_count: int