import re
from typing import List


KNOWLEDGE_BASE = [
    (
        "Revenue declines can be associated with higher order cancellations, "
        "delivery delays, and lower purchase volume."
    ),
    (
        "Delivery delays can reduce repeat purchases and negatively affect "
        "customer satisfaction."
    ),
    (
        "Customer churn increased after repeated delivery delays and "
        "unresolved support issues."
    ),
    (
        "Customers with frequent support tickets are more likely to "
        "cancel subscriptions."
    ),
    (
        "Retention improves when high-risk customers receive "
        "proactive outreach."
    ),
    (
        "Late deliveries and poor service quality are common "
        "customer churn drivers."
    ),
    (
        "Premium customers show lower churn when support response "
        "times remain under SLA."
    ),
]


STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "how",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "the",
    "to",
    "was",
    "what",
    "when",
    "where",
    "which",
    "who",
    "why",
}


def tokenize(text: str) -> set[str]:
    words = re.findall(
        r"\b[a-zA-Z]+\b",
        text.lower(),
    )

    return {
        word
        for word in words
        if word not in STOP_WORDS
    }


def retrieve_vector_context(
    query: str,
) -> List[str]:

    query_words = tokenize(query)

    scored_results = []

    for document in KNOWLEDGE_BASE:
        document_words = tokenize(document)

        score = len(
            query_words.intersection(
                document_words
            )
        )

        if score > 0:
            scored_results.append(
                (score, document)
            )

    scored_results.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    return [
        document
        for _, document
        in scored_results[:3]
    ]