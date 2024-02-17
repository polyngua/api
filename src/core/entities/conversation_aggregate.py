import uuid
from io import BytesIO

from . user import User, UserRepository
from . entity import *


class Message(Entity):
    """
    A message in a conversation.
    """
    def __init__(self, ID: Optional[UUID], role: str, content: str, audio: BytesIO = None) -> None:
        super().__init__(ID)

        self.role: str = role
        self.content: str = content
        self.audio: BytesIO = audio


class Conversation(Entity):
    """
    A conversation made up of messages between a user and the langauge model.
    """
    def __init__(self, ID: Optional[UUID], user: User, system_prompt: str):
        """
        Constructor for the class.

        :param ID: the conversation ID. Optional because this is defined by the repository.
        :param user: the user in this conversation.
        :param system_prompt: the system prompt being used in this conversation.
        """
        super().__init__(ID)
        self.user = user
        self.messages: dict[UUID, Message] = {}
        self.give_message(Message(None, "system", system_prompt))

    def give_message(self, message: Message) -> None:
        """
        Adds the given message to this conversation.

        :param message: the message to add to the conversation.
        """
        self.messages[message.ID] = message

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

    def get_all_messages(self) -> dict[UUID, Message]:
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


class ConversationAggregateRepository(EntityRepository[Conversation], ABC):
    """
    The domain aggregate for a conversation. This consolidates access to both conversations and the messages contained
    in them.
    """
    def __init__(self, user: User):
        """
        Because conversations belong to users, this class must be instantiated with a user. This allows for user-level
        permissions
        :param user:
        """
        self.user = user

    @abstractmethod
    def create(self, system_prompt: str) -> Conversation:
        raise NotImplementedError

    @abstractmethod
    def create_message_in_conversation(self, message: Message, conversation_id: UUID) -> Message:
        raise NotImplementedError

    @abstractmethod
    def get_message_from_conversation(self, message_id: UUID, conversation_id: UUID) -> Message:
        raise NotImplementedError

    @abstractmethod
    def remove_message_from_conversation(self, message_id: UUID, conversation_id: UUID) -> Message:
        raise NotImplementedError
