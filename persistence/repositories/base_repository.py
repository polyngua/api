"""
Contains the interfaces / abstract base classes for the
"""
from abc import ABC, abstractmethod
from core.entities import Entity


class SessionManagerRepository(ABC):
    @abstractmethod
    def commit(self):
        """
        Required function, intended to be called at the end of a series of transactions to commit them to a permanent
        store.
        """
        raise NotImplementedError

    def __enter__(self):
        """
        Gets this object when we enter a "with" statement (i.e., entering the "context" which gives this class its name).

        :return: this repository.
        """
        return self

    def __exit__(self, *args, **kwargs) -> None:
        """
        Calls the commit function, which will save any transactions performed while in the context.
        """
        self.commit()


class ReadOnlyRepository(ABC):
    @abstractmethod
    def get(self, identifier: int) -> Entity:
        """
        Required function. Will return the entity with the given ID.

        :param identifier: the ID of entity to get.
        :return: the entity.
        """
        raise NotImplementedError

    def get_all(self) -> list[Entity]:
        """
        Required function. Returns all entities in this repository.

        :return: a list of all entities.
        """
        raise NotImplementedError


class WriteOnlyRepository(ABC):
    @abstractmethod
    def add(self, item: Entity) -> Entity:
        """
        Required function. Adds the given entity to the repository.

        :param item: the entity to add.
        :return: the added entity.
        """
        raise NotImplementedError

    @abstractmethod
    def update(self, entity: Entity) -> Entity:
        """
        Required function. Updates the given entity with the information provided - uses entity ID for lookup.

        :param entity: the entity to update.
        :return: the altered entity
        """
        raise NotImplementedError

    def remove(self, identifier: int) -> bool:
        """
        Required function. Removes the entity with the given identifier from the repository.

        :param identifier: the entity to remove.
        :return: a boolean indicating success.
        """
        raise NotImplementedError



