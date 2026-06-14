import asyncio

from BuildScheduler.Scheduler.core.make_worker import scheduler_create_worker
from BuildScheduler.Scheduler.dataclass_models.scheduler_dc import WorkerCreationParams
from BuildScheduler.Scheduler.manage_worker.create_worker import create_worker_process


async def test():
    #await scheduler_create_worker("test")
    data = WorkerCreationParams(job_uuid='test', user_uuid='sparrow', remote_link='https://github.com/Poojit-Matukumalli/test.git', commit_id='273e6dce1d8f810e385cbfa5a7458f49301cc8e9', repo_name='test', framework='vite', pm='npm', install_req=True, output_dir='dist')
    await create_worker_process(data)
    print("done")
    await asyncio.sleep(20)


asyncio.run(test())