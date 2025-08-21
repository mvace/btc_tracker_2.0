from pydantic import BaseModel
from datetime import datetime


class PortfolioCreate(BaseModel):
    name: str


class PortfolioRead(BaseModel):
    id: int
    name: str
    model_config = {"from_attributes": True}
