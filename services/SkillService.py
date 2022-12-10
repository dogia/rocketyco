from uuid import uuid4
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from core.db import Base


class SkillService(Base):
    __tablename__ = 'skills'

    SkillId: Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    SkillName: Column(String(255))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SkillVacancyService(Base):
    __tablename__ = 'vacancies_skills'

    SkillId: Column(UUID(as_uuid=True), ForeignKey('skills.SkillId'))
    VacancyId: Column(UUID(as_uuid=True), ForeignKey('vacancies.VacancyId'))
    SkillYearExperience: Column(Integer)


class SkillUserService(Base):
    __tablename__ = 'users_skills'

    SkillId: Column(UUID(as_uuid=True), ForeignKey('skills.SkillId'))
    UserId: Column(UUID(as_uuid=True), ForeignKey('users.UserId'))
    SkillYearExperience: Column(Integer)
