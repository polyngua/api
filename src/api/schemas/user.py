from uuid import UUID

from pydantic import BaseModel


class UserBase(BaseModel):
    email: str
    first_name: str
    surname: str


class UserOut(UserBase):
    ID: UUID


class UserCreate(UserBase):
    password: str

