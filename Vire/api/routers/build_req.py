"""
This module (build_req) contains the router for handling the build requests.

Functions -
    process_build_req (async, fastapi router)
"""

import traceback
from fastapi import APIRouter

from BuildScheduler.Scheduler.db.sqlite_orm.crud import create
from Vire.core.validate_request import validate_details
from Vire.models.pydantic_classes import BuildRequestModel
from Vire.objects.dataclass_objects.validation_models import ValidatorContext

router = APIRouter()

@router.post("/build_request")
async def process_build_req(build_request_model: BuildRequestModel):
    """Processes build requests from Middleware microservice."""
    brm = build_request_model # I can't type BuildRequestModel everytime, so this.
    try:
        validator_context = ValidatorContext(
            job_uuid = brm.job_uuid,
            user_uuid= brm.user_uuid,
            provider= brm.provider,
            remote_user= brm.remote_user,
            remote_reponame= brm.remote_reponame,
            branch = brm.branch,
            commit_id= brm.commit_id
        )
        parsed_toml = await validate_details(validator_context)
        if not parsed_toml:
            return {"success": False, "Reason":"Server refused TOML object."}
        await create.register_build_data(brm, parsed_toml)
        await create.register_build_state(brm.job_uuid, user_uuid=brm.user_uuid, status="queued")
        return {"success": True, "Reason": "Server accepted the request."}
    except Exception:
        traceback.print_exc()
