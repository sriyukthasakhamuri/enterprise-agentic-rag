from pathlib import Path
from typing import List, Dict

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
)

from sentence_transformers import SentenceTransformer


COLLECTION_NAME = "enterprise_knowledge"

KNOWLEDGE_DIRECTORY = (
    Path(__file__).resolve().parent
    / "knowledge"
)


QDRANT_PATH = "qdrant_data"


embedding_model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

client = QdrantClient(
    path=QDRANT_PATH
)


def load_documents() -> List[Dict[str, str]]:
    documents = []

    for file_path in sorted(
        KNOWLEDGE_DIRECTORY.glob("*.txt")
    ):
        text = file_path.read_text(
            encoding="utf-8"
        )

        documents.append(
            {
                "source": file_path.name,
                "text": text,
            }
        )

    return documents


def chunk_text(
    text: str,
    chunk_size: int = 500,
) -> List[str]:

    paragraphs = [
        paragraph.strip()
        for paragraph in text.split("\n")
        if paragraph.strip()
    ]

    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:
        candidate = (
            f"{current_chunk}\n{paragraph}"
            if current_chunk
            else paragraph
        )

        if len(candidate) <= chunk_size:
            current_chunk = candidate
        else:
            if current_chunk:
                chunks.append(
                    current_chunk
                )

            current_chunk = paragraph

    if current_chunk:
        chunks.append(
            current_chunk
        )

    return chunks


def recreate_collection() -> None:
    collections = (
        client.get_collections().collections
    )

    collection_names = {
        collection.name
        for collection in collections
    }

    if COLLECTION_NAME in collection_names:
        client.delete_collection(
            collection_name=COLLECTION_NAME
        )

    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=384,
            distance=Distance.COSINE,
        ),
    )


def ingest_documents() -> None:
    documents = load_documents()

    recreate_collection()

    points = []

    point_id = 1

    for document in documents:
        chunks = chunk_text(
            document["text"]
        )

        for chunk_index, chunk in enumerate(
            chunks
        ):
            vector = embedding_model.encode(
                chunk
            ).tolist()

            points.append(
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={
                        "text": chunk,
                        "source":
                            document["source"],
                        "chunk_index":
                            chunk_index,
                    },
                )
            )

            point_id += 1

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=points,
    )

    print(
        f"Ingested {len(points)} chunks "
        f"from {len(documents)} documents."
    )


if __name__ == "__main__":
    ingest_documents()