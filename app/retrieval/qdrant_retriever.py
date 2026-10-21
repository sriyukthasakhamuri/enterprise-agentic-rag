from typing import List

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
)
from sentence_transformers import SentenceTransformer


COLLECTION_NAME = "enterprise_knowledge"

embedding_model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

client = QdrantClient(
    path="qdrant_data"
)


KNOWLEDGE_BASE = [
    {
        "id": 1,
        "text": (
            "Revenue declines can be associated with higher "
            "order cancellations, delivery delays, and lower "
            "purchase volume."
        ),
    },
    {
        "id": 2,
        "text": (
            "Delivery delays can reduce repeat purchases and "
            "negatively affect customer satisfaction."
        ),
    },
    {
        "id": 3,
        "text": (
            "Customer churn increased after repeated delivery "
            "delays and unresolved support issues."
        ),
    },
    {
        "id": 4,
        "text": (
            "Customers with frequent support tickets are more "
            "likely to cancel subscriptions."
        ),
    },
    {
        "id": 5,
        "text": (
            "Retention improves when high-risk customers receive "
            "proactive outreach."
        ),
    },
    {
        "id": 6,
        "text": (
            "Late deliveries and poor service quality are common "
            "customer churn drivers."
        ),
    },
    {
        "id": 7,
        "text": (
            "Premium customers show lower churn when support "
            "response times remain under SLA."
        ),
    },
]


def initialize_qdrant() -> None:
    collections = client.get_collections().collections

    collection_names = {
        collection.name
        for collection in collections
    }

    if COLLECTION_NAME in collection_names:
        return

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=384,
            distance=Distance.COSINE,
        ),
    )

    points = []

    for document in KNOWLEDGE_BASE:
        vector = embedding_model.encode(
            document["text"]
        ).tolist()

        points.append(
            PointStruct(
                id=document["id"],
                vector=vector,
                payload={
                    "text": document["text"],
                },
            )
        )

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points,
    )


def retrieve_qdrant_context(
    query: str,
    limit: int = 3,
) -> List[str]:
    initialize_qdrant()

    query_vector = embedding_model.encode(
        query
    ).tolist()

    response = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=limit,
    )

    results = response.points

    return [
        point.payload["text"]
        for point in results
        if point.payload
        and "text" in point.payload
    ]