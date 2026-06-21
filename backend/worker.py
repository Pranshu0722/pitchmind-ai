"""
Dramatiq worker entry point.

Start with:
    uv run dramatiq pitchmind.queue.tasks --queues video --processes 2 --threads 4
"""

import pitchmind.queue.broker  # noqa: F401 — registers RedisBroker as global broker
import pitchmind.queue.tasks  # noqa: F401 — registers @dramatiq.actor decorators
