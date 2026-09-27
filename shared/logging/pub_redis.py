import logging

import redis.asyncio as aredis
from Vire.utils import state

r = aredis.Redis.from_url(state.redis_url) #pyright: ignore[reportUnknownMemberType]


async def publish_log_redis(line: str, user_uuid: str, job_uuid: str) -> None:
    try:
        stream = f"logs:{user_uuid}/{job_uuid}"
        data: dict[str, str] = {"payload": line}
        _ = await r.xadd(stream, data, maxlen=1000, approximate=True)  # pyright: ignore[reportArgumentType]
    except Exception as e:
        logging.critical(
            "pub_redis failed. Details: %s", e, exc_info=True, stack_info=True
        )
