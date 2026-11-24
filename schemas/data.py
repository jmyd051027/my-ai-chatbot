
from datetime import date
from pydantic import BaseModel, Field


class DataCreate(BaseModel):
    date: date
    value: float = Field(ge=0, le=24)
    memo: str = Field(default="", max_length=500)


class DataUpdate(DataCreate):
    pass


class DataResponse(DataCreate):
    id: str
