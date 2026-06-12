"""
This module (models) is responsible foe providing the db schemas and the init function.

DB Schema classes -
    1.

Functions -
    1. init (async)
"""

from sqlalchemy import TIMESTAMP, String, func
from sqlalchemy.orm import Mapped, mapped_column

from Vire.db.db import Base, engine
from Vire.utils.logger import vire_logger


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
    job_uuid: Mapped[str] = mapped_column(String, nullable=False, primary_key=True)
    user_uuid: Mapped[str] = mapped_column(String, nullable=False)
    remote_link: Mapped[str] = mapped_column(String, nullable=False)
    commit_id: Mapped[str] = mapped_column(String, nullable=False)
    provider: Mapped[str] = mapped_column(String, nullable=False)
    remote_user: Mapped[str] = mapped_column(String, nullable=False)
    remote_reponame: Mapped[str] = mapped_column(String, nullable=False)
    branch: Mapped[str] = mapped_column(String, nullable=False)


class BuildState(Base):
    """
    Table for build states.

    This SQLAlchemy schema handles build states.
    Only running / queued builds should be present here.
    """

    __tablename__ = "BuildState"
    job_uuid: Mapped[str] = mapped_column(String, nullable=False, primary_key=True)
    user_uuid: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, nullable=False, server_default=func.now())
    finished_at: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP)
    error: Mapped[str] = mapped_column(String)


async def init_db():
    """Initialize the database and start sqlalchemy engine."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await vire_logger("info", "Vire state database has started up.")
