from pydantic import BaseModel, Field
from datetime import datetime


class PortfolioCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class PortfolioRead(BaseModel):
    id: int
    name: str
    model_config = {"from_attributes": True}
