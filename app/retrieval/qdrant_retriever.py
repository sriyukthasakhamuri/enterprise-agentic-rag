from typing import List

from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer


COLLECTION_NAME = "enterprise_knowledge"
QDRANT_PATH = "qdrant_data"


embedding_model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

client = QdrantClient(
    path=QDRANT_PATH
)


def retrieve_qdrant_context(
    query: str,
    limit: int = 3,
) -> List[str]:

    query_vector = embedding_model.encode(
        query
    ).tolist()

    response = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=limit,
    )

    return [
        point.payload["text"]
        for point in response.points
        if point.payload
        and "text" in point.payload
    ]