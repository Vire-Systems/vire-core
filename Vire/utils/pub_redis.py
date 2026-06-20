"""
This module (pub_redis) is responsible for providing an async redis publisher function.
"""

import redis.asyncio as redis
from Vire.utils import state
from BuildScheduler.shared.scheduler_logger import vire_logger

assert state.redis_url is not None
client = redis.Redis.from_url(state.redis_url)

async def publish_log_redis(line: str, user_uuid: str ,job_uuid: str)-> None:
    """Publishes a single line to the channel 'logs:<user_uuid>/<job_uuid>'."""
    try:
        await client.publish(f"logs:{user_uuid}/{job_uuid}", line)
    except Exception as e:
        await vire_logger("critical", "[Core publish_log_redis] Unable to publish logs. Details: %s", e)
    finally:
        await client.aclose()
