from uuid import UUID

from pydantic import BaseModel
from typing import Optional, Union


class MessageBase(BaseModel):
    role: str
    content: str


class MessageIn(BaseModel):
    content: str


class MessageOut(MessageBase):
    ID: Optional[UUID]
