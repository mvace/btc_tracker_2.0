from pydantic import BaseModel


class PortfolioCreate(BaseModel):
    name: str


class PortfolioRead(BaseModel):
    id: int
    name: str
    model_config = {"from_attributes": True}
