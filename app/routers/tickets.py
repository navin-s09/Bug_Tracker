import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.core.dependencies import get_current_user, require_roles
from app.db.database import SessionLocal
from app.models.enums import UserRole
from app.models.ticket import Ticket
from app.models.user import User
from app.schemas.ticket import TicketCreate, TicketResponse, TicketUpdate


router = APIRouter(
    prefix="/tickets",
    tags=["tickets"],
)


logger = logging.getLogger(__name__)


@router.post(
    "",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_ticket(
    ticket_data: TicketCreate,
    current_user: User = Depends(
        require_roles(
            UserRole.MANAGER,
            UserRole.LEAD,
            UserRole.DEV,
            UserRole.CLIENT,
        )
    ),
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

        logger.info(
            "Ticket created: ticket_id=%s user_id=%s role=%s",
            ticket.id,
            current_user.id,
            current_user.role.value,
        )

        return ticket

    except Exception:
        logger.exception(
            "Failed to create ticket: user_id=%s",
            current_user.id,
        )
        raise

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

        # Clients and developers can only see their own tickets.
        if current_user.role in (
            UserRole.CLIENT,
            UserRole.DEV,
        ):
            query = query.where(
                Ticket.owner_id == current_user.id
            )

        # Managers and leads can see all tickets.
        tickets = db.scalars(query).all()

        logger.info(
            "Tickets listed: user_id=%s role=%s count=%s",
            current_user.id,
            current_user.role.value,
            len(tickets),
        )

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
            logger.warning(
                "Ticket not found: ticket_id=%s user_id=%s",
                ticket_id,
                current_user.id,
            )

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found",
            )

        # Developers and clients can only view their own tickets.
        if (
            current_user.role in (
                UserRole.CLIENT,
                UserRole.DEV,
            )
            and ticket.owner_id != current_user.id
        ):
            logger.warning(
                "Unauthorized ticket access: ticket_id=%s user_id=%s",
                ticket_id,
                current_user.id,
            )

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found",
            )

        logger.info(
            "Ticket viewed: ticket_id=%s user_id=%s",
            ticket_id,
            current_user.id,
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
    current_user: User = Depends(
        require_roles(
            UserRole.MANAGER,
            UserRole.LEAD,
            UserRole.DEV,
        )
    ),
):
    db = SessionLocal()

    try:
        ticket = db.scalar(
            select(Ticket).where(Ticket.id == ticket_id)
        )

        if not ticket:
            logger.warning(
                "Update failed: ticket not found: ticket_id=%s user_id=%s",
                ticket_id,
                current_user.id,
            )

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found",
            )

        # Developers can update only their own tickets.
        if (
            current_user.role == UserRole.DEV
            and ticket.owner_id != current_user.id
        ):
            logger.warning(
                "Unauthorized ticket update: ticket_id=%s user_id=%s",
                ticket_id,
                current_user.id,
            )

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

        logger.info(
            "Ticket updated: ticket_id=%s user_id=%s",
            ticket.id,
            current_user.id,
        )

        return ticket

    except HTTPException:
        raise

    except Exception:
        logger.exception(
            "Failed to update ticket: ticket_id=%s user_id=%s",
            ticket_id,
            current_user.id,
        )
        raise

    finally:
        db.close()


@router.delete(
    "/{ticket_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_ticket(
    ticket_id: int,
    current_user: User = Depends(
        require_roles(UserRole.MANAGER)
    ),
):
    db = SessionLocal()

    try:
        ticket = db.scalar(
            select(Ticket).where(Ticket.id == ticket_id)
        )

        if not ticket:
            logger.warning(
                "Delete failed: ticket not found: ticket_id=%s user_id=%s",
                ticket_id,
                current_user.id,
            )

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found",
            )

        db.delete(ticket)
        db.commit()

        logger.info(
            "Ticket deleted: ticket_id=%s user_id=%s",
            ticket_id,
            current_user.id,
        )

    except HTTPException:
        raise

    except Exception:
        logger.exception(
            "Failed to delete ticket: ticket_id=%s user_id=%s",
            ticket_id,
            current_user.id,
        )
        raise

    finally:
        db.close()