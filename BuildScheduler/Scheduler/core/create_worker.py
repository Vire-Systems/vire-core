"""
This module (create_worker) is responsible for worker process creation.

Functions -
1. create_worker_process (async)
"""

import subprocess, json
from BuildScheduler.shared.scheduler_logger import vire_logger
from BuildScheduler.Scheduler.core.del_container import delayed_delete

async def create_worker_process(json_struct: tuple)-> None:
    """
    An abstraction for worker process creation.

    json_struct:
        1. job_uuid - string, Job's uuid4.
        2. user_uuid - string, User's uuid4.
        3. remote - string, Remote link (ex: GitHub link, GitLab link, etc.).
        4. repo_name - string, Name of repository.
        5. framework - string, Name of the framework (ex: nextjs, vite, etc).
        6. pm - string, Name of the package manager (ex: npm, pnpm, etc).
        7. install_req - str(lowercase "true" or "false"), Whether to run the package manager's install command or not.
        8. output_dir - string, User provided output directory. 
    """
    async def _wk_helper(json_struct)-> None:
        job_uuid, user_uuid, remote, repo_name, framework, pm, install_req, output_dir = json_struct
        try:
            cmd_b = {
                "job_uuid": job_uuid,
                "user_uuid": user_uuid,
                "remote": remote,
                "repo_name": repo_name,
                "framework": framework,
                "pm": pm,
                "install_req": install_req,
                "output_dir":output_dir
            }
            argument = json.dumps(cmd_b)
            cmd = [
                "nohup",
                "/home/vire/Vire-Core/venv/bin/python",
                "/home/vire/Vire-Core/BuildScheduler/worker/worker.py",
                "--json_struct", argument
            ]
        except Exception as e:
            await vire_logger("critical", "[_wk_helper] Parsing the command for creating a worker failed. Details %s", e)
        try:
            subprocess.Popen( #pylint: disable=consider-using-with
                cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            await delayed_delete(job_uuid)
        except Exception as e:
            await vire_logger("critical", "[create_worker] Worker creation failed. Details: %s", e)
    await _wk_helper(json_struct)
