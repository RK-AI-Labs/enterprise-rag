"""Declarative base for SQLAlchemy ORM table models."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class shared by all ORM table models in the Postgres schema."""
