
from BuildScheduler.shared.pub_redis import r as client
from BuildScheduler.shared.shared_state import core_id
from Vire.objects.dataclass_objects.validation_models import ValidatorContext

async def register_job_with_redis(VC: ValidatorContext):
    assert core_id is not None
    async with client as r:
        r.hset(
            f"job_session:{VC.user_uuid}/{VC.job_uuid}",
            mapping= {
                "core_id": core_id,
                "remote_user": VC.remote_user,
                "repo": VC.remote_reponame,
                "commit_id": VC.commit_id,
                "provider": VC.provider
            }
        )