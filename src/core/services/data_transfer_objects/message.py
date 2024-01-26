from uuid import UUID

from pydantic import BaseModel
from typing import Optional


class MessageBase(BaseModel):
    role: str
    content: str


class MessageIn(BaseModel):
    content: str


class MessageOut(MessageBase):
    id: Optional[UUID]
