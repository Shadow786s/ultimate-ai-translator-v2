from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="queued",
        nullable=False,
    )

    source_language: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    target_language: Mapped[str] = mapped_column(
        String(50),
        default="hinglish",
        nullable=False,
    )

    total_items: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    completed_items: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    progress: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid4()),
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="queued",
        nullable=False,
    )

    source_language: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    target_language: Mapped[str] = mapped_column(
        String(50),
        default="hinglish",
        nullable=False,
    )

    total_items: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    completed_items: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    progress: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    retry_seconds: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    retry_until: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    retry_message: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    original_filename: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    translation_preview: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    retry_seconds: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    retry_until: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    retry_message: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    original_filename: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    translation_preview: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
