from uuid import uuid4
from sqlalchemy import Column, DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from core.db import Base


class CompanyService(Base):
    __tablename__ = 'companies'

    CompanyId = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    CompanyName = Column(String(255), unique=True)
    CompanyWebsite = Column(Text, unique=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def dict(self):
        return {
            "CompanyId": str(self.CompanyId),
            "CompanyName": str(self.CompanyName),
            "CompanyWebsite": str(self.CompanyWebsite)
        }

Base.metadata.create_all()
