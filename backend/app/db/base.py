from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


from app import models  # noqa: E402,F401  # Ensure models are imported for Alembic
