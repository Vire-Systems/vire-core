"""
This module (models) is responsible foe providing the db schemas and the init function.

DB Schema classes -
    1. 

Functions -
    1. init (async)
"""

from Vire.db.db import engine, Base
from Vire.utils.logger import vire_logger
from sqlalchemy import Column, String


class BuildData(Base):
    """
    The DB schema class for Build request related data.
    
    Attributes - 
        job_uuid: String,
        user_uuid: str,
        remote_link: str,
        commit_id: str,
        provider: str,
        remote_user: str,
        remote_reponame: str,
        branch: str
    """
    __tablename__ = "BuildData"
    job_uuid = Column(String, nullable=False, primary_key=True)
    user_uuid = Column(String, nullable=False)
    remote_link = Column(String, nullable=False)
    commit_id = Column(String, nullable=False)
    provider = Column(String, nullable=False)
    remote_user = Column(String, nullable=False)
    remote_reponame = Column(String, nullable=False)
    branch = Column(String, nullable=False)



async def init_db():
    """Initialize the database and start sqlalchemy engine."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await vire_logger("info", "Vire state database has started up.")
