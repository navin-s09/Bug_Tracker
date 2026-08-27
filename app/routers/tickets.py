from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.core.dependencies import get_current_user
from app.db.database import SessionLocal
from app.models.enums import UserRole
from app.models.ticket import Ticket
from app.models.user import User
from app.schemas.ticket import TicketCreate, TicketResponse, TicketUpdate


router = APIRouter(
    prefix="/tickets",
    tags=["tickets"],
)


@router.post(
    "",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_ticket(
    ticket_data: TicketCreate,
    current_user: User = Depends(get_current_user),
):
    db = SessionLocal()

    try:
        ticket = Ticket(
            title=ticket_data.title,
            description=ticket_data.description,
            owner_id=current_user.id,
        )

        db.add(ticket)
        db.commit()
        db.refresh(ticket)

        return ticket

    finally:
        db.close()


@router.get(
    "",
    response_model=list[TicketResponse],
)
def list_tickets(
    current_user: User = Depends(get_current_user),
):
    db = SessionLocal()

    try:
        query = select(Ticket)

        if current_user.role == UserRole.CLIENT:
            query = query.where(Ticket.owner_id == current_user.id)

        tickets = db.scalars(query).all()

        return tickets

    finally:
        db.close()


@router.get(
    "/{ticket_id}",
    response_model=TicketResponse,
)
def get_ticket(
    ticket_id: int,
    current_user: User = Depends(get_current_user),
):
    db = SessionLocal()

    try:
        ticket = db.scalar(
            select(Ticket).where(Ticket.id == ticket_id)
        )

        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found",
            )

        if (
            current_user.role == UserRole.CLIENT
            and ticket.owner_id != current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found",
            )

        return ticket

    finally:
        db.close()


@router.put(
    "/{ticket_id}",
    response_model=TicketResponse,
)
def update_ticket(
    ticket_id: int,
    ticket_data: TicketUpdate,
    current_user: User = Depends(get_current_user),
):
    db = SessionLocal()

    try:
        ticket = db.scalar(
            select(Ticket).where(Ticket.id == ticket_id)
        )

        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found",
            )

        if (
            current_user.role == UserRole.CLIENT
            and ticket.owner_id != current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot update this ticket",
            )

        if ticket_data.title is not None:
            ticket.title = ticket_data.title

        if ticket_data.description is not None:
            ticket.description = ticket_data.description

        if ticket_data.status is not None:
            ticket.status = ticket_data.status

        db.commit()
        db.refresh(ticket)

        return ticket

    finally:
        db.close()


@router.delete(
    "/{ticket_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_ticket(
    ticket_id: int,
    current_user: User = Depends(get_current_user),
):
    db = SessionLocal()

    try:
        ticket = db.scalar(
            select(Ticket).where(Ticket.id == ticket_id)
        )

        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found",
            )

        if (
            current_user.role == UserRole.CLIENT
            and ticket.owner_id != current_user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot delete this ticket",
            )

        db.delete(ticket)
        db.commit()

    finally:
        db.close()