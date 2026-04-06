from redis_client import redis_client

LIMIT = 5      # max requests
WINDOW = 60    # seconds


def is_allowed(user_id: str) -> bool:
    key = f"rate:{user_id}"

    current = redis_client.get(key)

    if current and int(current) >= LIMIT:
        return False

    pipe = redis_client.pipeline()
    pipe.incr(key, 1)
    pipe.expire(key, WINDOW)
    pipe.execute()

    return True