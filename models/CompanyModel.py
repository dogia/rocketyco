from typing import List, Optional
from uuid import uuid4
from pydantic import UUID4, BaseModel, Field

from models.VacancyModel import VacancyModel


class CompanyModel(BaseModel):
    CompanyId: UUID4 = Field(default_factory=uuid4)
    CompanyName: str
    CompanyWebsite: Optional[str]

    Vacancies: Optional[List[VacancyModel]]
