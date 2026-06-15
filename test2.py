import aiosqlite as asql
import asyncio

# test
async def idk( job_uuid: str, status: str, prev_status: str):
    async with asql.connect("/home/vire/Vire-DB/vire_state.db") as db:
        await db.execute("""
            UPDATE BuildState
            SET status=?
            WHERE 
            job_uuid=? AND status=?
            """,
            (status, job_uuid, prev_status)
        )
        await db.commit()

asyncio.run(idk("test", "finished", "running"))