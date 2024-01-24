import uuid
from . entity import *
from . message import Message


class Conversation(Entity):
    def __init__(self, id: int, name: str, system_prompt: str):
        """
        A conversation containing messages between the user and the assistant

        :param name:
        """
        super().__init__(id)
        self.user_name: str = name
        self.identifier: str = str(uuid.uuid4())
        self.messages: dict[int, Message] = {}
        self.give_message(Message(None, "system", system_prompt))

    def give_message(self, message: Message) -> None:
        """
        Adds the given message to this conversation.

        :param message: the message to add to the conversation.
        """
        self.messages[message.id] = message

    def message_exists(self, identifier: uuid):
        """
        :param identifier: identifier of relevant message.
        :return: boolean indicating whether the message is in this conversation.
        """
        return identifier in self.messages.keys()

    def get_message(self, identifier: uuid) -> Optional[Message]:
        """
        Returns the specific message specified (if it exists)

        :param identifier: the message to return.
        :return:
        """
        if not self.message_exists(identifier):
            return None

        return self.messages[identifier]

    def get_all_messages(self) -> dict[int, Message]:
        """
        :return: the messages which make up this conversion, barring the first one; that is not part of the conversation
        but rather the system prompt.
        """
        return {k: v for i, (k, v) in enumerate(self.messages.items()) if i > 0}

    def get_system_prompt(self) -> Message:
        """
        :return: the system prompt for this conversation.
        """
        return next(iter(self.messages.values()))  # Supposedly has a lower overhead than making a list. Makes sense.


class ConversationRepository(EntityRepository, ABC):
    pass
