"""The aiosqlite+sqlalchemy db initialization module."""

import os
from Vire.utils.state import sqlite_db_path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

os.makedirs(os.path.dirname(sqlite_db_path), exist_ok=True)

DATABASE_URL = f"sqlite+aiosqlite:///{sqlite_db_path}"

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
Base = declarative_base()
