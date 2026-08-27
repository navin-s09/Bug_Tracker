from enum import Enum


class UserRole(str, Enum):
    MANAGER = "manager"
    LEAD = "lead"
    DEV = "dev"
    CLIENT = "client"