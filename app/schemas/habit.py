from pydantic import BaseModel, Field, field_validator
from typing import Annotated

class HabitCreate(BaseModel):
    name: str
    days: Annotated[list[Annotated[int, Field(ge=1, le=7)]], Field(max_length=7)]

    @field_validator("days")
    def unique_elements(cls, v):
        if len(v) != len(set(v)):
            raise ValueError('Days must be unique')
        return v

class HabitChange(BaseModel):
    days: Annotated[list[Annotated[int, Field(ge=1, le=7)]], Field(max_length=7)]

    @field_validator("days")
    def unique_elements(cls, v):
        if len(v) != len(set(v)):
            raise ValueError('Days must be unique')
        return v
