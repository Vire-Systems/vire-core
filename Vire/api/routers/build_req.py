"""
This module (build_req) contains the router for handling the build requests.

Functions -
    process_build_req (async, fastapi router)
"""

import traceback
from fastapi import APIRouter
from Vire.models.pydantic_classes import BuildRequestModel
from Vire.core.make_worker import scheduler_create_worker


router = APIRouter()

@router.post("/build_request")
async def process_build_req(build_request_model: BuildRequestModel):
    """Processes build requests from Middleware microservice."""
    brm = build_request_model # I can't type BuildRequestModel everytime, so this.
    try:
        await scheduler_create_worker(
            job_uuid=brm.job_uuid, user_uuid=brm.user_uuid, remote_link=brm.remote_link,
            commit_id=brm.commit_id, provider=brm.provider, remote_user=brm.remote_user,
            remote_reponame=brm.remote_reponame, branch=brm.branch
        )
        return {"success": True, "Reason": "Server accepted the request."}
    except Exception:
        traceback.print_exc()
