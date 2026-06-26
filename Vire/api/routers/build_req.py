"""
This module (build_req) contains the router for handling the build requests.

Functions -
    process_build_req (async, fastapi router)
"""

import traceback
from fastapi import APIRouter

from BuildScheduler.Scheduler.db.caching.redis_registry import register_job_with_redis
from BuildScheduler.Scheduler.db.sqlite_orm.crud import create
from Vire.core.register_with_queue import register_build
from Vire.core.validate_request import validate_details
from Vire.models.pydantic_classes import BuildRequestModel
from Vire.objects.dataclass_objects.validation_models import ValidatorContext

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
