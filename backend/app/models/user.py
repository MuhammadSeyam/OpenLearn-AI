import uuid

from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    password_hash: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    preferred_lang: Mapped[str] = mapped_column(
        String(10),
        default="en",
        nullable=False,
    )

    role: Mapped[str] = mapped_column(
        String(20),
        default="student",
        nullable=False,
    )

    settings: Mapped[dict] = mapped_column(
        JSONB,
        default=dict,
        nullable=False,
    )
