from uuid import uuid4
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from core.db import Base
from services.UserService import UserService
from services.VacancyService import VacancyService


class SkillService(Base):
    __tablename__ = 'skills'

    SkillId = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    SkillName = Column(String(255), unique=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def dict(self):
        return {
            "SkillId": str(self.SkillId),
            "SkillName": str(self.SkillName)
        }


class SkillVacancyService(Base):
    __tablename__ = 'vacancies_skills'

    SkillVacancyId = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    SkillId = Column(UUID(as_uuid=True), ForeignKey(SkillService.SkillId))
    VacancyId = Column(UUID(as_uuid=True), ForeignKey(VacancyService.VacancyId))
    SkillYearExperience = Column(Integer)

    def dict(self):
        return {
            "SkillVacancyId": str(self.SkillVacancyId),
            "SkillId": str(self.SkillId),
            "VacancyId": str(self.VacancyId),
            "SkillYearExperience": str(self.SkillYearExperience)
        }


class SkillUserService(Base):
    __tablename__ = 'users_skills'

    SkillUserId = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    SkillId = Column(UUID(as_uuid=True), ForeignKey(SkillService.SkillId))
    UserId = Column(UUID(as_uuid=True), ForeignKey(UserService.UserId))
    SkillYearExperience = Column(Integer)

    def dict(self):
        return {
            "SkillUserId": str(self.SkillUserId),
            "SkillId": str(self.SkillId),
            "UserId": str(self.UserId),
            "SkillYearExperience": str(self.SkillYearExperience)
        }

Base.metadata.create_all()
