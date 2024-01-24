from src.core.entities import ConversationRepository, Conversation
from persistence.repositories.base_repository import SessionManagerRepository
from persistence.repositories.memory_repository.data_store import DataStore


class MemoryConversationRepository(ConversationRepository, SessionManagerRepository):
    def __init__(self):
        self.data_store = DataStore()

    def get(self, conversation_id: int) -> Conversation:
        """
        Returns the conversation with the given ID.

        :param conversation_id: the ID of the conversation to get.
        :return: the conversation.
        """
        return self.data_store.conversations[conversation_id]

    def add(self, conversation: Conversation) -> Conversation:
        """
        Adds the given conversation to the repo's data store.

        :param conversation: the conversation to add.
        :return: the added conversation. Note that this will have a new ID.
        """
        id = len(self.data_store.conversations) + 1  # TODO: Note that this will not work after a conversation gets removed.
        conversation.id = id
        self.data_store.conversations[id] = conversation

        return conversation

    def update(self, conversation: Conversation) -> Conversation:
        """
        Overwrites the given conversation in the datastore.

        Lookup is done using the ID of the given conversation.

        :param conversation: the conversation (with ID) to update.
        :return: the updated conversation.
        """
        # TODO: Note that this is a crude method: we just overwrite for now.
        self.data_store.conversations[conversation.id] = conversation
        return conversation

    def remove(self, conversation: Conversation) -> Conversation:
        """
        Removes the given conversation from the data store.

        :param conversation: the conversation to remove.
        :return: the removed conversation.
        """
        return self.data_store.conversations.pop(conversation.id)

    def commit(self):
        """
        No commit needed for an in memory repo, but other repositories will be context managed, so this provides a
        consistent interface.
        """
        pass
