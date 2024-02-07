import uuid

from src.core.entities.conversation_aggregate import ConversationAggregateRepository, Conversation, Message
from src.core.entities import User
from src.persistence.repositories import SessionManagerRepository
from src.persistence.repositories.memory_repository.data_store import DataStore

from uuid import UUID


# TODO: Note that this entire repository is curerntly implemented "optimistically"; it doesn't handle any errors (what
#  should happen if a conversation ID doesn't exist, or if a message isn't in the given conversation?). Unit tests
#  will eventually obligate this to be fixed, but it's a (low) priority to fix before then. However, a SQLRepo is a
#  higher priority for now.


class MemoryConversationAggregateRepository(ConversationAggregateRepository, SessionManagerRepository):
    def __init__(self, user: User):
        super().__init__(user)

        self.data_store = DataStore()

    def get(self, ID: UUID) -> Conversation:
        """
        Returns the conversation with the given ID.
        """
        return self.data_store.conversations.get(ID)

    def add(self, conversation: Conversation) -> Conversation:
        """
        Adds the given conversation to the repository.

        Note: I'm not clear where this would be used yet.
        """
        self.data_store.conversations[conversation.ID] = conversation

        return conversation

    def create(self, system_prompt: str) -> Conversation:
        """
        Creates a new repository using the given parameters, adds it to the repo and return it.
        """
        id = uuid.uuid4()
        conversation = Conversation(id, self.user, system_prompt)
        self.data_store.conversations[id] = conversation

        return conversation

    def update(self, conversation: Conversation) -> Conversation:
        """
        Updates the given conversation; the conversation is identified using the ID in the given conversation, but all
        other parameters are overwritten.
        """
        self.data_store.conversations[conversation.ID] = conversation

        return conversation

    def remove(self, ID: UUID) -> Conversation:
        """
        Removes the conversation with the given ID and returns it.
        """
        return self.data_store.conversations.pop(ID)

    def create_message_in_conversation(self, message: Message, conversation_id: UUID) -> Message:
        """
        Adds the given message to the given conversation and return the conversation.
        """
        message.ID = uuid.uuid4()

        self.data_store.conversations[conversation_id].messages[message.ID] = message
        return self.data_store.conversations[conversation_id].messages[message.ID]

    def get_message_from_conversation(self, message_id: UUID, conversation_id: UUID) -> Message:
        """
        Returns a specific message from the given conversation.
        """
        return self.data_store.conversations[conversation_id].messages[message_id]

    def remove_message_from_conversation(self, message_id: UUID, conversation_id: UUID) -> Message:
        """
        Removes the given message from the given conversation and returns it.
        """
        return self.data_store.conversation[conversation_id].messages.pop(message_id)

    def commit(self):
        """
        No commit needed for an in-memory repository, so we just pass here.
        """
        ...
