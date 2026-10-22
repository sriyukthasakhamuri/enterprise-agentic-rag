import json
from pathlib import Path
from typing import Any, Dict, List

from app.agents.workflow import agent_graph


PROJECT_ROOT = (
    Path(__file__).resolve().parents[2]
)

TEST_DATA_PATH = (
    PROJECT_ROOT
    / "app"
    / "data"
    / "evaluation"
    / "test_questions.json"
)


INSUFFICIENT_EVIDENCE_PHRASES = [
    "not enough evidence",
    "not enough information",
    "insufficient evidence",
    "insufficient information",
    "cannot determine",
    "can't determine",
    "cannot confirm",
    "can't confirm",
    "not provided",
    "no evidence",
    "does not provide",
    "do not have enough",
]


def load_test_cases() -> List[Dict[str, Any]]:
    with open(
        TEST_DATA_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def contains_expected_terms(
    result: Dict[str, Any],
    expected_terms: List[str],
) -> float:

    searchable_content = json.dumps(
        {
            "vector_results":
                result.get(
                    "vector_results",
                    [],
                ),
            "sql_results":
                result.get(
                    "sql_results",
                    {},
                ),
            "answer":
                result.get(
                    "answer",
                    "",
                ),
        }
    ).lower()

    if not expected_terms:
        return 1.0

    matches = 0

    for term in expected_terms:
        if term.lower() in searchable_content:
            matches += 1

    return matches / len(expected_terms)


def check_groundedness_behavior(
    answer: str,
    expected_behavior: str,
) -> bool:

    answer_lower = answer.lower()

    if (
        expected_behavior
        == "insufficient_evidence"
    ):
        return any(
            phrase in answer_lower
            for phrase
            in INSUFFICIENT_EVIDENCE_PHRASES
        )

    return False


def build_initial_state(
    question: str,
) -> Dict[str, Any]:

    return {
        "query": question,
        "rewritten_query": None,
        "route": None,
        "vector_results": [],
        "sql_results": {},
        "combined_context": "",
        "conversation_history": [],
        "answer": None,
        "confidence": 0.0,
        "retry_count": 0,
    }


def run_test_case(
    test_case: Dict[str, Any],
) -> Dict[str, Any]:

    initial_state = build_initial_state(
        test_case["question"]
    )

    result = agent_graph.invoke(
        initial_state
    )

    expected_route = (
        test_case["expected_route"]
    )

    actual_route = result.get(
        "route"
    )

    route_correct = (
        expected_route
        == actual_route
    )

    answer = result.get(
        "answer",
        "",
    ) or ""

    answer_generated = (
        len(answer.strip()) > 20
    )

    evaluation_type = (
        test_case["evaluation_type"]
    )

    retrieval_score = None
    groundedness_passed = None

    if evaluation_type == "retrieval":
        retrieval_score = (
            contains_expected_terms(
                result,
                test_case.get(
                    "expected_terms",
                    [],
                ),
            )
        )

    elif evaluation_type == "groundedness":
        groundedness_passed = (
            check_groundedness_behavior(
                answer=answer,
                expected_behavior=(
                    test_case[
                        "expected_answer_behavior"
                    ]
                ),
            )
        )

    return {
        "id":
            test_case["id"],
        "question":
            test_case["question"],
        "evaluation_type":
            evaluation_type,
        "expected_route":
            expected_route,
        "actual_route":
            actual_route,
        "route_correct":
            route_correct,
        "retrieval_score":
            (
                round(
                    retrieval_score,
                    2,
                )
                if retrieval_score
                is not None
                else None
            ),
        "groundedness_passed":
            groundedness_passed,
        "answer_generated":
            answer_generated,
        "confidence":
            result.get(
                "confidence",
                0.0,
            ),
        "retry_count":
            result.get(
                "retry_count",
                0,
            ),
        "answer":
            answer,
    }


def print_test_result(
    result: Dict[str, Any],
) -> None:

    print(
        f"\n{result['id']}"
    )

    print(
        f"Question: "
        f"{result['question']}"
    )

    print(
        f"Evaluation type: "
        f"{result['evaluation_type']}"
    )

    print(
        f"Expected route: "
        f"{result['expected_route']}"
    )

    print(
        f"Actual route: "
        f"{result['actual_route']}"
    )

    print(
        f"Route correct: "
        f"{result['route_correct']}"
    )

    if (
        result["evaluation_type"]
        == "retrieval"
    ):
        print(
            f"Retrieval score: "
            f"{result['retrieval_score']}"
        )

    if (
        result["evaluation_type"]
        == "groundedness"
    ):
        print(
            f"Groundedness passed: "
            f"{result['groundedness_passed']}"
        )

        print(
            f"Answer: "
            f"{result['answer']}"
        )

    print(
        f"Confidence: "
        f"{result['confidence']}"
    )

    print(
        f"Retries: "
        f"{result['retry_count']}"
    )


def run_evaluation() -> None:
    test_cases = load_test_cases()

    results = []

    print(
        "\nEnterprise Agentic RAG Evaluation"
    )

    print(
        "=" * 60
    )

    for test_case in test_cases:
        print(
            f"\nRunning "
            f"{test_case['id']}..."
        )

        result = run_test_case(
            test_case
        )

        results.append(
            result
        )

        print_test_result(
            result
        )

    route_accuracy = (
        sum(
            1
            for result in results
            if result["route_correct"]
        )
        / len(results)
    )

    retrieval_results = [
        result
        for result in results
        if (
            result["evaluation_type"]
            == "retrieval"
        )
    ]

    groundedness_results = [
        result
        for result in results
        if (
            result["evaluation_type"]
            == "groundedness"
        )
    ]

    if retrieval_results:
        average_retrieval_score = (
            sum(
                result["retrieval_score"]
                for result
                in retrieval_results
            )
            / len(retrieval_results)
        )
    else:
        average_retrieval_score = 0.0

    if groundedness_results:
        groundedness_safety = (
            sum(
                1
                for result
                in groundedness_results
                if result[
                    "groundedness_passed"
                ]
            )
            / len(
                groundedness_results
            )
        )
    else:
        groundedness_safety = 0.0

    answer_success_rate = (
        sum(
            1
            for result in results
            if result[
                "answer_generated"
            ]
        )
        / len(results)
    )

    print(
        "\n"
        + "=" * 60
    )

    print(
        "Evaluation Summary"
    )

    print(
        "=" * 60
    )

    print(
        f"Total test cases: "
        f"{len(results)}"
    )

    print(
        f"Routing test cases: "
        f"{len(results)}"
    )

    print(
        f"Retrieval test cases: "
        f"{len(retrieval_results)}"
    )

    print(
        f"Groundedness test cases: "
        f"{len(groundedness_results)}"
    )

    print()

    print(
        f"Route accuracy: "
        f"{route_accuracy:.1%}"
    )

    print(
        f"Retrieval relevance: "
        f"{average_retrieval_score:.1%}"
    )

    print(
        f"Answer generation success: "
        f"{answer_success_rate:.1%}"
    )

    print(
        f"Groundedness safety: "
        f"{groundedness_safety:.1%}"
    )

    failed_groundedness = [
        result
        for result in groundedness_results
        if not result[
            "groundedness_passed"
        ]
    ]

    if failed_groundedness:
        print(
            "\nGroundedness failures:"
        )

        for result in failed_groundedness:
            print(
                f"- {result['id']}: "
                f"{result['question']}"
            )


if __name__ == "__main__":
    run_evaluation()