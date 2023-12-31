from pydantic import BaseModel


class MessageBase(BaseModel):
    role: str
    content: str


class MessageIn(BaseModel):
    content: str


class MessageOut(MessageBase):
    id: str