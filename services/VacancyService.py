from uuid import uuid4
from sqlalchemy import DECIMAL, Column, DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from core.db import Base
from models.CompanyModel import CompanyModel
from services.CompanyService import CompanyService


class VacancyService(Base):
    __tablename__ = 'vacancies'

    VacancyId: Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    CompanyId: Column(UUID(as_uuid=True), ForeignKey('companies.CompanyId'))
    PositionName: Column(String(255))
    Salary: Column(DECIMAL(12,2))
    Currency: Column(String(3))
    VacancyLink: Column(Text, unique=True)
    
    # TODO: RequiredSkills: relation()

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


    def with_company(self, Company: CompanyService | CompanyModel):
        self.CompanyId = Company.CompanyId