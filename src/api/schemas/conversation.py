from uuid import UUID

from src.core.entities import Message
from pydantic import Field, field_validator

from . message import *


class ConversationBase(BaseModel):
    ID: UUID
    with_who: str = Field(validation_alias="user_name")


class ConversationIn(BaseModel):
    name: str


class ConversationOut(ConversationBase):
    messages: Optional[list[MessageOut]]

    @field_validator("messages", mode="before")
    @classmethod
    def parse_conversation_messages(cls, messages: dict[int, Message]):
        print([(message.as_dict()) for message in messages.values()])

        return [(message.as_dict()) for message in messages.values()]
