from enum import Enum


class UserRole(str, Enum):
    MANAGER = "manager"
    LEAD = "lead"
    DEV = "dev"
    CLIENT = "client"


class TicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"