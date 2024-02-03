from uuid import UUID

from src.core.entities.user import User

from pydantic import BaseModel
from typing import Optional


class UserBase(BaseModel):
    email: str
    first_name: str
    surname: str


class UserOut(UserBase):
    ID: UUID


class UserCreate(UserBase):
    password: str

