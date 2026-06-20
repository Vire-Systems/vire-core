import logging

import redis
from Vire.utils import state

assert state.redis_url is not None
r = redis.Redis.from_url(state.redis_url)

def publish_log_redis(line: str, user_uuid: str ,job_uuid: str)-> None:
    try:
        r.publish(f"logs:{user_uuid}/{job_uuid}", line)
    except Exception as e:
        logging.critical("pub_redis failed. Details: %s", e, exc_info=True, stack_info=True)
