import uuid

import redis

from src.config import settings

redis_client = redis.from_url(settings.REDIS_URL)

def set_jti(jti: uuid.UUID, remaining_ttl: int) -> None:
    redis_client.set(f"{jti}", "revoked", ex=remaining_ttl)

def get_jti(jti: uuid.UUID) -> bool:
    if redis_client.get(f"{jti}"):
        return True
    else:
        return False