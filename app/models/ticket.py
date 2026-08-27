from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base
from app.models.enums import TicketStatus


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    status: Mapped[TicketStatus] = mapped_column(
        SQLEnum(
            TicketStatus,
            name="ticketstatus",
            values_callable=lambda enum: [member.value for member in enum],
        ),
        nullable=False,
        default=TicketStatus.OPEN,
    )

    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    