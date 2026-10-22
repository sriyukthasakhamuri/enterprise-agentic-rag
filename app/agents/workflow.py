from concurrent.futures import ThreadPoolExecutor

from langgraph.graph import StateGraph, END

from app.agents.state import AgentState
from app.agents.router import route_query
from app.retrieval.qdrant_retriever import retrieve_qdrant_context
from app.retrieval.sql_retriever import retrieve_sql_context
from app.services.llm_service import generate_llm_answer
from app.services.evaluation_service import evaluate_answer
from app.services.query_rewrite_service import rewrite_query


MAX_RETRIES = 2
CONFIDENCE_THRESHOLD = 0.75


def router_node(state: AgentState) -> AgentState:
    return route_query(state)


def vector_node(state: AgentState) -> AgentState:
    query_to_use = (
        state.get("rewritten_query")
        or state["query"]
    )

    state["vector_results"] = retrieve_qdrant_context(
        query_to_use
    )

    return state


def sql_node(state: AgentState) -> AgentState:
    query_to_use = (
        state.get("rewritten_query")
        or state["query"]
    )

    state["sql_results"] = retrieve_sql_context(
        query_to_use
    )

    return state


def parallel_retrieval_node(
    state: AgentState,
) -> AgentState:
    query_to_use = (
        state.get("rewritten_query")
        or state["query"]
    )

    with ThreadPoolExecutor(
        max_workers=2
    ) as executor:

        vector_future = executor.submit(
            retrieve_qdrant_context,
            query_to_use,
        )

        sql_future = executor.submit(
            retrieve_sql_context,
            query_to_use,
        )

        state["vector_results"] = (
            vector_future.result()
        )

        state["sql_results"] = (
            sql_future.result()
        )

    return state


def answer_node(state: AgentState) -> AgentState:
    context = {
        "vector_results": state["vector_results"],
        "sql_results": state["sql_results"],
    }

    query_to_use = (
        state.get("rewritten_query")
        or state["query"]
    )

    state["answer"] = generate_llm_answer(
        query=query_to_use,
        context=context,
    )

    return state


def evaluation_node(
    state: AgentState,
) -> AgentState:

    context = {
        "vector_results": state["vector_results"],
        "sql_results": state["sql_results"],
    }

    state["confidence"] = evaluate_answer(
        query=state["query"],
        context=context,
        answer=state["answer"] or "",
        route=state["route"],
    )

    return state


def rewrite_node(
    state: AgentState,
) -> AgentState:

    state["retry_count"] += 1

    state["rewritten_query"] = rewrite_query(
        original_query=state["query"],
        answer=state["answer"] or "",
    )

    state["vector_results"] = []
    state["sql_results"] = {}

    return state


def route_decision(
    state: AgentState,
) -> str:

    return state["route"]


def evaluation_decision(
    state: AgentState,
) -> str:

    if (
        state["confidence"]
        >= CONFIDENCE_THRESHOLD
    ):
        return "end"

    if (
        state["retry_count"]
        >= MAX_RETRIES
    ):
        return "end"

    return "rewrite"


workflow = StateGraph(AgentState)

workflow.add_node(
    "router",
    router_node,
)

workflow.add_node(
    "vector",
    vector_node,
)

workflow.add_node(
    "sql",
    sql_node,
)

workflow.add_node(
    "parallel_retrieval",
    parallel_retrieval_node,
)

workflow.add_node(
    "answer",
    answer_node,
)

workflow.add_node(
    "evaluate",
    evaluation_node,
)

workflow.add_node(
    "rewrite",
    rewrite_node,
)

workflow.set_entry_point("router")


# Initial routing
workflow.add_conditional_edges(
    "router",
    route_decision,
    {
        "vector": "vector",
        "sql": "sql",
        "both": "parallel_retrieval",
    },
)


# Retrieval → Answer
workflow.add_edge(
    "vector",
    "answer",
)

workflow.add_edge(
    "sql",
    "answer",
)

workflow.add_edge(
    "parallel_retrieval",
    "answer",
)


# Answer → Evaluation
workflow.add_edge(
    "answer",
    "evaluate",
)


# Evaluation → End or Rewrite
workflow.add_conditional_edges(
    "evaluate",
    evaluation_decision,
    {
        "rewrite": "rewrite",
        "end": END,
    },
)


# Rewritten query follows same route again
workflow.add_conditional_edges(
    "rewrite",
    route_decision,
    {
        "vector": "vector",
        "sql": "sql",
        "both": "parallel_retrieval",
    },
)


agent_graph = workflow.compile()