"""
This module(async_requests) is an asynchronous set-up for requests (aiohttp). Keeps a pool of connections.

Functions -
    1. send_request
"""

import asyncio, httpx
from Vire.utils.logger import vire_logger

MAX_CONCURRENT = 10
TIMEOUT = 3
MAX_ALIVE = 20

semaphore = asyncio.Semaphore(MAX_ALIVE)

limits = httpx.Limits(
    max_keepalive_connections=MAX_ALIVE,
    max_connections=MAX_CONCURRENT
    )

timeout = httpx.Timeout(TIMEOUT, connect=5.0, read=5.0)

async def _send_request_helper(client: httpx.AsyncClient, url: str)-> httpx.Response:
    """Helper for send_request."""
    async with semaphore:
        try:
            response = await client.get(url, timeout= TIMEOUT)
            response.raise_for_status()
            return response
        except Exception as e:
            await vire_logger("warn", e)

async def send_request(url: str)-> httpx.Response:
    """
    Async implementation for requests (using httpx). Performs a GET request on the specified URL.
    
    Behavior -
        Works asynchronously using asyncio.Semaphore for limiting max outbound requests. Semaphore blocks until a thread calls release().
        Uses httpx.Limits to avoid OOM and 100k requests under load (...).
        Timeout of 3s is used as to not wait for long periods of time.
    
    Args -
        client - httpx.AsyncClient, an asynchronous HTTP client with connection pooling, HTTP/2, redirects, cookie persistence, etc.
        url - The url to perform a GET request on.
    """
    async with httpx.AsyncClient(limits=limits) as client:
        return await _send_request_helper(client, url)
