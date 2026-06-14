from Vire.core.validate_request import validate_details
from BuildScheduler.Scheduler.db.crud import create
from Vire.models.pydantic_classes import BuildRequestModel
from Vire.objects.dataclass_objects.validation_models import ValidatorContext

async def register_build(BRM: BuildRequestModel):
    try:
        validator_context = ValidatorContext(
            job_uuid=BRM.job_uuid,
            user_uuid=BRM.user_uuid,
            provider=BRM.provider,
            remote_user=BRM.remote_user,
            remote_reponame=BRM.remote_reponame,
            branch=BRM.branch,
            commit_id=BRM.commit_id
        )
        validated_toml = await validate_details(VC=validator_context)
        if not validated_toml:
            return

        await create.register_build_data(BRM, validated_toml)
        await create.register_build_state(job_uuid=BRM.job_uuid, user_uuid=BRM.user_uuid, status="queued")
    except Exception as e:
        print(e)