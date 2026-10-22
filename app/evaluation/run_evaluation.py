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


def run_test_case(
    test_case: Dict[str, Any],
) -> Dict[str, Any]:

    initial_state = {
        "query":
            test_case["question"],
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

    retrieval_score = (
        contains_expected_terms(
            result,
            test_case[
                "expected_terms"
            ],
        )
    )

    answer = result.get(
        "answer",
        "",
    )

    answer_generated = bool(
        answer
        and len(answer.strip()) > 20
    )

    return {
        "id":
            test_case["id"],
        "question":
            test_case["question"],
        "expected_route":
            expected_route,
        "actual_route":
            actual_route,
        "route_correct":
            route_correct,
        "retrieval_score":
            round(
                retrieval_score,
                2,
            ),
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
    }


def run_evaluation() -> None:
    test_cases = load_test_cases()

    results = []

    print(
        "\nEnterprise Agentic RAG Evaluation"
    )

    print(
        "=" * 50
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

        print(
            f"Question: "
            f"{result['question']}"
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

        print(
            f"Retrieval score: "
            f"{result['retrieval_score']}"
        )

        print(
            f"Confidence: "
            f"{result['confidence']}"
        )

        print(
            f"Retries: "
            f"{result['retry_count']}"
        )

    route_accuracy = (
        sum(
            1
            for result in results
            if result["route_correct"]
        )
        / len(results)
    )

    average_retrieval_score = (
        sum(
            result[
                "retrieval_score"
            ]
            for result in results
        )
        / len(results)
    )

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
        + "=" * 50
    )

    print(
        "Evaluation Summary"
    )

    print(
        "=" * 50
    )

    print(
        f"Test cases: "
        f"{len(results)}"
    )

    print(
        f"Route accuracy: "
        f"{route_accuracy:.1%}"
    )

    print(
        f"Average retrieval score: "
        f"{average_retrieval_score:.1%}"
    )

    print(
        f"Answer generation success: "
        f"{answer_success_rate:.1%}"
    )


if __name__ == "__main__":
    run_evaluation()