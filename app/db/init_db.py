from app.db.database import Base, engine


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)