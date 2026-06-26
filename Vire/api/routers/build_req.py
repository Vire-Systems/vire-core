"""
This module (build_req) contains the router for handling the build requests.

Functions -
    process_build_req (async, fastapi router)
"""

import traceback
from fastapi import APIRouter

from Vire.core.register_with_queue import register_build
from Vire.models.pydantic_classes import BuildRequestModel

router = APIRouter()

@router.post("/build_request")
async def process_build_req(build_request_model: BuildRequestModel):
    """Processes build requests from Middleware microservice."""
    brm = build_request_model # I can't type BuildRequestModel everytime, so this.
    try:
        result = await register_build(brm)
        return result
    except Exception:
        traceback.print_exc()
