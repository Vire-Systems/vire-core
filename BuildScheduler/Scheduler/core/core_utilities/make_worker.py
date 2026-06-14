"""
This module (make_worker) is repsonsible with providing an abstracted function called scheduler_create_worker.
This is made so that the API layer does not mess with fetching raw data, parsing, etc.
"""

import traceback

from BuildScheduler.Scheduler.db.crud import read, update
from BuildScheduler.Scheduler.manage_worker.create_worker import create_worker_process

async def scheduler_create_worker(job_uuid: str)-> None:
    try:
        job_data = await read.fetch_build_data(job_uuid)
        if not job_data:
            print("No worker data") #TODO: change this to raise an error or smtn
            return
  
        await create_worker_process(job_data)
        await update.update_job_status(job_uuid=job_data.job_uuid, status_msg="finished")
    except Exception as e:
        traceback.print_exc()
        print("scheduler_create_worker failed", e)
