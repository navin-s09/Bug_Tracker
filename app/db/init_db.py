from app.db.database import Base, engine
from app.models.user import User


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)