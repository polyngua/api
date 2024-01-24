from pydantic import BaseModel
from core.entities import Message
from core.entities import Conversation


class MessageOut(BaseModel):
    id: str
    role: str
    content: str

    @classmethod
    def from_message(cls, message: Message):
        """
        Creates this Pydantic model based off of the given message.

        :param message: the message to create the Pydantic model for.
        :return: MessageOut
        """
        return cls(id=message.identifier, role=message.role, content=message.content)


class ConversationOut(BaseModel):
    id: str
    messages: list[MessageOut]
    with_who: str

    @classmethod
    def from_conversation(cls, conversation: Conversation):
        return cls(id=conversation.identifier,
                   messages=[MessageOut.from_message(mes) for mes in conversation.get_all_messages()])


class MessageIn(BaseModel):
    content: str

class Name(BaseModel):
    name: str


