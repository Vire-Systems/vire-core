import subprocess, json, asyncio
from BuildScheduler.shared.scheduler_logger import vire_logger
from BuildScheduler.Scheduler.core.del_container import delayed_delete


async def create_worker_process(job_uuid: str, remote: str):
    async def _wk_helper(job_uuid, remote):
        try:
            cmd_b = {"job_uuid":job_uuid, "remote":remote}
            argument = json.dumps(cmd_b)
            cmd = [
                "nohup",
                "/home/vire/Vire-Core/venv/bin/python",
                "/home/vire/Vire-Core/BuildScheduler/worker/worker.py",
                "--json_struct", argument
            ]
        except Exception as e:
            await vire_logger("critical", "[_wk_helper] Parsing the command for creating a worker failed. Details %s", e)
            return
        try:
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            await delayed_delete(job_uuid)
        except Exception as e:
            await vire_logger("critical", "[create_worker] Worker creation failed. Details: %s", e) 
    await _wk_helper(job_uuid, remote)