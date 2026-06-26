
from typing import Literal

from BuildScheduler.shared.pub_redis import r as client
from BuildScheduler.shared.shared_state import core_id
from Vire.models.pydantic_classes import BuildRequestModel

async def register_job_with_redis(BRM: BuildRequestModel, state: Literal["validating", "passed", "failed"]):
    assert core_id is not None
    async with client as r:
        await r.hset(
            f"job_session:{BRM.user_uuid}/{BRM.job_uuid}",
            mapping= {
                "core_id": core_id,
                "remote_user": BRM.remote_user,
                "repo": BRM.remote_reponame,
                "commit_id": BRM.commit_id,
                "provider": BRM.provider,
                "state": state
            }
        )