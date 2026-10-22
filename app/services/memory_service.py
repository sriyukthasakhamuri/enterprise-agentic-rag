import json
from typing import List, Dict

import redis


redis_client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True,
)


def save_message(
    session_id: str,
    role: str,
    content: str,
) -> None:
    key = f"conversation:{session_id}"

    message = {
        "role": role,
        "content": content,
    }

    redis_client.rpush(
        key,
        json.dumps(message),
    )


def get_conversation(
    session_id: str,
    limit: int = 10,
) -> List[Dict[str, str]]:
    key = f"conversation:{session_id}"

    messages = redis_client.lrange(
        key,
        -limit,
        -1,
    )

    return [
        json.loads(message)
        for message in messages
    ]


def clear_conversation(
    session_id: str,
) -> None:
    key = f"conversation:{session_id}"

    redis_client.delete(key)