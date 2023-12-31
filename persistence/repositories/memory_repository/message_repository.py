from entities import Message, MessageRepository
from persistence.repositories.base_repository import SessionManagerRepository
from persistence.repositories.memory_repository.data_store import DataStore


class MemoryMessageRepository(MessageRepository, SessionManagerRepository):
    def __init__(self):
        self.data_store = DataStore()

    def get(self, message_id: int) -> Message:
        """
        Returns the message with the given ID.

        :param message_id: the ID of the message to get.
        :return: the message.
        """
        return self.data_store.messages[message_id]

    def add(self, message: Message) -> Message:
        """
        Adds the given message to the repo's data store.

        :param message: the message to add.
        :return: the added message. Note that this will have a new ID.
        """
        id = len(self.data_store.messages) + 1  # TODO: Note that this will not work after a message gets removed.
        message.id = id
        self.data_store.messages[id] = message

        return message

    def update(self, message: Message) -> Message:
        """
        Overwrites the given message in the datastore.

        Lookup is done using the ID of the given message.

        :param message: the message (with ID) to update.
        :return: the updated message.
        """
        # TODO: Note that this is a crude method: we just overwrite for now.
        self.data_store.messages[message.id] = message
        return message

    def remove(self, message: Message) -> Message:
        """
        Removes the given conversation from the data store.

        :param message: the message to remove.
        :return: the removed message.
        """
        return self.data_store.messages.pop(message.id)

    def commit(self):
        """
        No commit needed for an in memory repo, but other repositories will be context managed, so this provides a
        consistent interface.
        """
        pass
