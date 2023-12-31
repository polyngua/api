from pydantic import BaseModel

from . message import *


class ConversationBase(BaseModel):
    id: int
    with_who: str


class ConversationOut(ConversationBase):
    messages: list[MessageOut]
