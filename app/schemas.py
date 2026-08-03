from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class FactBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)
    category: str = Field(..., min_length=1, max_length=50)
    source: Optional[str] = Field(None, max_length=500)


class FactCreate(FactBase):
    pass


class FactResponse(FactBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class FactListResponse(BaseModel):
    facts: list[FactResponse]
    total: int
    page: int
    limit: int


class CategoryResponse(BaseModel):
    category: str
    count: int


class StatsResponse(BaseModel):
    total_facts: int
    total_categories: int
    facts_per_category: list[CategoryResponse]


class HealthResponse(BaseModel):
    status: str
    message: str
