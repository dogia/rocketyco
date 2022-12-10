from uuid import uuid4
from sqlalchemy import Column, DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from core.db import Base


class UserService(Base):
    __tablename__ = 'users'

    UserId: Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    FirstName: Column(String(255))
    LastName: Column(String(255))
    Email: Column(String(255), unique=True)
    YearPreviousExperience: Column(Integer)

    # TODO: Skills

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
