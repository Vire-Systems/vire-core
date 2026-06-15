"""The aiosqlite+sqlalchemy db initialization module."""

import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from BuildScheduler.Scheduler.utils.state import sqlite_db_path, DB_URL

if sqlite_db_path:
    os.makedirs(os.path.dirname(sqlite_db_path), exist_ok=True)
else:
    print("sqlite_db_path failed to load (/home/vire/vire/BuildScheduler/Scheduler/db/db.py)")

DATABASE_URL = DB_URL

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()
