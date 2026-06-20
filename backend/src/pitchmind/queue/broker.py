import dramatiq
from dramatiq.brokers.redis import RedisBroker
from dramatiq.middleware import Retries

from pitchmind.config import settings

_retries = Retries(max_retries=3, min_backoff=1_000, max_backoff=60_000)
broker = RedisBroker(url=settings.redis_url, middleware=[_retries])  # type: ignore[no-untyped-call]
dramatiq.set_broker(broker)
