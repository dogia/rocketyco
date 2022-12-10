from typing import Optional
from uuid import uuid4
from pydantic import UUID4, BaseModel, Field


class SkillModel(BaseModel):
    SkillId: UUID4 = Field(default_factory=uuid4)
    SkillName: str
    SkillYearExperience: int
