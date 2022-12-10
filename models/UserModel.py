from typing import List, Optional
from uuid import uuid4
from pydantic import UUID4, BaseModel, Field

from models.SkillModel import SkillModel


class UserModel(BaseModel):
    UserId: UUID4 = Field(default_factory=uuid4)
    FirstName: str
    LastName: Optional[str]
    Email: str
    YearPreviousExperience: int
    Skills: Optional[List[SkillModel]]
