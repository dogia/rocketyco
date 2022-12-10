from typing import Optional
from uuid import uuid4
from pydantic import UUID4, BaseModel, Field


class CompanyModel(BaseModel):
    CompanyId: UUID4 = Field(default_factory=uuid4)
    CompanyName: str
    CompanyWebsite: Optional[str]
