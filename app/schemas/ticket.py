from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import TicketStatus


class TicketCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)


class TicketUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    description: str | None = Field(
        default=None,
        min_length=1,
    )

    status: TicketStatus | None = None


class TicketResponse(BaseModel):
    id: int
    title: str
    description: str
    status: TicketStatus
    owner_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }