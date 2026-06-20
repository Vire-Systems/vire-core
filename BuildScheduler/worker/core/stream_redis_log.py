from utils import state
from utils.vire_logger import cfn_log


r = state.redis_con
client = state.client

# Helper called by 'stream_logs'
def publish_log_redis(line: str)-> None:
    try:
        r.publish(f"logs:{state.user_uuid}/{state.job_uuid}", line)
    except Exception as e:
        cfn_log("critical", "[publish_log_redis] Unable to publish logs. Details: %s", e)


# Calls 'publish_log_redis'
def stream_logs(job_uuid: str)-> None:
    try:
        container = client.containers.get(job_uuid)
        for line in container.logs(stream=True, follow=True, stdout=True, stderr=True, timestamps=True):
            str_line = line.decode("utf-8")
            if len(str_line) >= 32:
                publish_log_redis(str_line)
    except Exception as e:
        cfn_log("critical", "[stream_logs] Error in stream_logs. Details: (%s)", e)
