import sys
from datetime import timedelta
from typing import Any
from typing import Optional

import redis
from decouple import config


def redis_connect() -> redis.client.Redis:
    """Connect to redis client."""
    try:
        client = redis.StrictRedis(
            host=config('REDIS_HOST'),
            port=config('REDIS_PORT', cast=int),
            db=config('REDIS_DB', cast=int),
            password=config('REDIS_PASSWORD'),
            socket_timeout=5,
            charset='utf-8',
            decode_responses=True,
        )
        return client
    except redis.AuthenticationError:
        print('AuthenticationError')
        sys.exit(1)


client = redis_connect()
ping = client.ping()
if not ping:
    print("Can't reach Redis, please check your config!")
    sys.exit(1)


def get_key_from_cache(key: Optional[str] = None) -> Optional[Any]:
    """Get data from redis."""
    if not key or not client:
        return None
    return client.get(key)


def get_key_ttl(key: str) -> int:
    """Get key ttl from redis"""
    ttl = client.ttl(key)
    if not ttl:
        return 0
    return ttl


def set_key_expiry(key: str, timeout: int) -> None:
    client.expire(key, timeout)


def set_key_in_cache(key: str, value: Any, timeout: int = 3600) -> Optional[bool]:
    """Store data in redis."""
    if client:
        return client.setex(key, timedelta(seconds=timeout), value=value)
    return None
