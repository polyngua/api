from src.core.entities import Conversation, Message

from uuid import UUID


class DataStore:
    """
    Singleton class which holds the data used in a in memory repository.
    """
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super(DataStore, cls).__new__(cls)
            cls.conversations: dict[UUID, Conversation] = {}
            cls.messages: dict[UUID, Message] = {}

        return cls.instance
