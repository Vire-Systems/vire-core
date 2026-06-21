"""
This module (create_worker) is responsible for worker process creation.

Functions -
1. create_worker_process (async)
"""

import json
import subprocess
from textwrap import dedent

from BuildScheduler.Scheduler.dataclass_models.scheduler_dc import WorkerCreationParams
from BuildScheduler.Scheduler.errors.db_errors import NoJobStateError
from BuildScheduler.Scheduler.manage_worker.del_container import delayed_delete
from BuildScheduler.Scheduler.utils.pub_redis import publish_log_redis
from BuildScheduler.Scheduler.utils.state import python_bin_path, worker_path
from BuildScheduler.shared.scheduler_logger import vire_logger
from BuildScheduler.Scheduler.db.crud import update



async def create_worker_process(WCP : WorkerCreationParams) -> None:
    """
    An abstraction for worker process creation.

    Args- 
        WCP - Worker creation params, abbrev. Params for this function.

    Raises JobCreationFailed
    """

    async def _wk_helper(WCP: WorkerCreationParams) -> None:
        try:
            # I def didn't forget to change paths after the refactor 😑 /s
            assert python_bin_path is not None, "Path for python bin does not exist. Fix it. Current path appears to be 'None'."
            assert worker_path is not None, "The path for worker does not exist. Fix it. Current path appears to be 'None'."

            cmd_b = {
                "job_uuid": WCP.job_uuid,
                "user_uuid": WCP.user_uuid,
                "remote": WCP.remote_link,
                "repo_name": WCP.repo_name,
                "framework": WCP.framework,
                "pm": WCP.pm,
                "output_dir": WCP.output_dir,
                "install_req": WCP.install_req,
                "commit_id": WCP.commit_id,
            }
            argument = json.dumps(cmd_b)
            cmd = [
                "nohup",
                python_bin_path,
                worker_path,
                "--json_struct",
                argument,
            ]
        except Exception as e:
            await vire_logger("critical", "[_wk_helper] Worker creation failed for job_uuid: %s, user_uuid: %s. Details: %s", WCP.job_uuid, WCP.user_uuid,e)

            line = f"""
            Error: VC-SC-001 & VC-SC-004. Failed to run job.
            Details:
              Job UUID: {WCP.job_uuid}
              User UUID: {WCP.user_uuid}
              SHA ID: {WCP.commit_id}

            NOTE: This is an internal error. Contact us if you see this.
            """
            publish_log_redis(dedent(line), user_uuid=WCP.user_uuid,job_uuid=WCP.job_uuid)
            await update.update_job_status(job_uuid=WCP.job_uuid, status_msg = "crashed", error_code="VC-SC-001")
            return

        try:
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            await update.update_job_status(job_uuid=WCP.job_uuid, status_msg="running")
            await delayed_delete(WCP.job_uuid)

        except NoJobStateError:
            await vire_logger("critical", "[create_worker] raised NoJobStateError. Worker creation failed for job_uuid '%s' owned by user uuid '%s'.", WCP.job_uuid, WCP.user_uuid)
            await update.update_job_status(job_uuid=WCP.job_uuid, status_msg="crashed", error_code="VC-SC-003")

            line = f"""
            Error: VC-SC-003. Failed to run job.
            Details:
              Job UUID: {WCP.job_uuid}
              User UUID: {WCP.user_uuid}
              SHA ID: {WCP.commit_id}
            """
            publish_log_redis(dedent(line), user_uuid=WCP.user_uuid,job_uuid=WCP.job_uuid)

        except Exception as e:
            await vire_logger("critical", "[create_worker] Worker creation failed. Details: %s", e)
            await update.update_job_status(job_uuid=WCP.job_uuid, status_msg="crashed", error_code="VC-SH-001")

            line = f"""
            Error: VC-SC-001. Failed to run job.
            Details:
              Job UUID: {WCP.job_uuid}
              User UUID: {WCP.user_uuid}
              SHA ID: {WCP.commit_id}

            NOTE: This is an internal error. Contact us if you see this.
            """
            publish_log_redis(dedent(line), user_uuid=WCP.user_uuid,job_uuid=WCP.job_uuid)

    await _wk_helper(WCP)
