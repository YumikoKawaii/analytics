import redis
from app.config import settings

redis_cli = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=settings.redis_db,
    password=settings.redis_password,
    decode_responses=settings.redis_decode_responses
)
