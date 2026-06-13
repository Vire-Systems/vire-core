from Vire.core.validate_request import validate_details
from BuildScheduler.Scheduler.db.crud import register_build_data, register_build_state, async_session
from Vire.models.pydantic_classes import BuildRequestModel
from Vire.objects.dataclass_objects.validation_models import ValidatorContext

async def register_build(BRM: BuildRequestModel):
    try:
        validator_context = ValidatorContext(**BRM.model_dump(exclude={"remote_link"}))
        valid_build = await validate_details(VC=validator_context)
        print(validator_context)
        if not valid_build:
            return

        await register_build_data(BRM)
        await register_build_state(job_uuid=BRM.job_uuid, user_uuid=BRM.user_uuid, status="queued")
        print("test")
    except Exception as e:
        print(e)