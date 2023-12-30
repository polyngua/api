from pydantic import BaseModel


class MessageBase(BaseModel):
    role: str
    content: str


class MessageIn(MessageBase):
    pass


class MessageOut(MessageBase):
    id: str