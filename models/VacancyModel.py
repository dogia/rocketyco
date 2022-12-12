from typing import List, Optional
from uuid import uuid4
from pydantic import UUID4, BaseModel, Field

from models.SkillModel import SkillModel


class VacancyModel(BaseModel):
    VacancyId: UUID4 = Field(default_factory=uuid4)
    CompanyId: Optional[UUID4]
    PositionName: str
    Salary: Optional[float]
    Currency: Optional[str]
    VacancyLink: Optional[str]
    RequiredSkills: Optional[List[SkillModel]]
