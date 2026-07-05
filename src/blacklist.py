import uuid

import redis

redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)

def set_jti(jti: uuid.UUID, remaining_ttl: int) -> None:
    redis_client.set(f"{jti}", "revoked", ex=remaining_ttl)

def get_jti(jti: uuid.UUID) -> bool:
    if redis_client.get(f"{jti}"):
        return True
    else:
        return False