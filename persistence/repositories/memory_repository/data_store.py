from entities import Conversation


class DataStore:
    """
    Singleton class which holds the data used in a in memory repository.
    """
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super(DataStore, cls).__new__(cls)
            cls.conversations: dict[int, Conversation] = {}

        return cls.instance
