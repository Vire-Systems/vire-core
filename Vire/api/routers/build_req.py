from fastapi import APIRouter
import traceback
from Vire.models.pydantic_classes import BuildRequestModel
from Vire.core.make_worker import scheduler_create_worker


router = APIRouter()

@router.post("/build_request")
async def process_build_req(BuildRequestModel: BuildRequestModel):
    """Processes build requests from Middleware microservice."""
    brm = BuildRequestModel # I can't type BuildRequestModel everytime, so this.
    try:
        await scheduler_create_worker(
            job_uuid=brm.job_uuid, user_uuid=brm.user_uuid, remote_link=brm.remote_link,
            commit_id=brm.commit_id, provider=brm.provider, remote_user=brm.remote_user,
            remote_reponame=brm.remote_reponame, branch=brm.branch, lockfile_name="package-lock.json"
        )
    except Exception:
        traceback.print_exc()
