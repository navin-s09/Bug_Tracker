import logging
import os

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select

from app.core.dependencies import get_current_user
from app.core.logging_config import setup_logging
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.db.database import SessionLocal
from app.models.enums import UserRole
from app.models.user import User
from app.routers.tickets import router as tickets_router
from app.schemas.user import (
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)


load_dotenv()

setup_logging()

logger = logging.getLogger(__name__)


COMPANY_EMAIL_DOMAIN = os.getenv(
    "COMPANY_EMAIL_DOMAIN",
    "fulcrumdigital.com",
).lower()


app = FastAPI(
    title="BUG TRACKER V1",
    version="1.0.0",
)


app.include_router(tickets_router)


@app.get("/")
def root():
    logger.info("Root endpoint accessed")

    return {
        "message": " bug tracking app is running",
    }


@app.get("/health")
def health_check():
    logger.info("Health check requested")

    return {
        "status": "healthy",
    }


@app.post(
    "/users/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(user_data: UserCreate):
    email = user_data.email.strip().lower()

    email_domain = email.rsplit("@", 1)[1]

    if (
        user_data.role != UserRole.CLIENT
        and email_domain != COMPANY_EMAIL_DOMAIN
    ):
        logger.warning(
            "Registration rejected: invalid company email domain"
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Internal users must use a company email address",
        )

    db = SessionLocal()

    try:
        existing_user = db.scalar(
            select(User).where(User.email == email)
        )

        if existing_user:
            logger.warning(
                "Registration rejected: email already registered: %s",
                email,
            )

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )

        new_user = User(
            email=email,
            hashed_password=hash_password(user_data.password),
            role=user_data.role,
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        logger.info(
            "User registered successfully: user_id=%s role=%s",
            new_user.id,
            new_user.role.value,
        )

        return new_user

    finally:
        db.close()


@app.post(
    "/auth/login",
    response_model=TokenResponse,
)
def login_user(user_data: UserLogin):
    email = user_data.email.strip().lower()

    db = SessionLocal()

    try:
        user = db.scalar(
            select(User).where(User.email == email)
        )

        if not user:
            logger.warning(
                "Login failed: user not found: %s",
                email,
            )

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not verify_password(
            user_data.password,
            user.hashed_password,
        ):
            logger.warning(
                "Login failed: invalid password for email: %s",
                email,
            )

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        access_token = create_access_token(
            {
                "sub": str(user.id),
                "email": user.email,
                "role": user.role.value,
            }
        )

        logger.info(
            "User login successful: user_id=%s role=%s",
            user.id,
            user.role.value,
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
        }

    finally:
        db.close()


@app.get(
    "/users/me",
    response_model=UserResponse,
)
def get_me(
    current_user: User = Depends(get_current_user),
):
    logger.info(
        "Current user requested: user_id=%s",
        current_user.id,
    )

    return current_user