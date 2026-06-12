"""
Note: This is NOT permanent. It is a means to view logs sent by the core.

redis_sub.py -

A redis subscriber (Blocking) to observe logs. Run as a separate process (Not in program).
"""

import redis

client = redis.Redis.from_url("redis://127.0.0.1:6379")

pubsub = client.pubsub()

channel_name = "logs:sparrow/test"

pubsub.subscribe(channel_name)
print("Subscribed to ", channel_name)

while True:
    try:
        for message in pubsub.listen():
            if message["type"] == "message":
                channel = message["channel"]
                data:bytes = message["data"]
                print(f"[{channel_name}] Received: {data.decode()}\n")
    except redis.TimeoutError:
        continue