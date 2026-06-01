import redis
from Vire.utils import state
from Vire.utils.logger import vire_logger

r = redis.Redis.from_url(state.redis_url)

def publish_log_redis(line: str, user_uuid: str ,job_uuid: str)-> None:
    try:
        r.publish(f"logs:{user_uuid}/{job_uuid}", line)
    except Exception as e:
        vire_logger("critical", "[Core publish_log_redis] Unable to publish logs. Details: %s", e)
