from abc import ABC, abstractmethod
from typing import Optional


class Entity(ABC):
    def __init__(self, id: int = None):
        """
        Every business entity will inherit from this class, and all will have some identifier.

        :param id: this entity's identifier. Defaults to None, for when creating a new instance.
        """
        self.id: Optional[int] = id

    def as_dict(self) -> dict:
        """
        Returns a dictionary of the object.
        """
        return self.__dict__


class EntityRepository[TEntity: Entity](ABC):
    @abstractmethod
    def add(self, entity: TEntity) -> TEntity:
        raise NotImplementedError

    @abstractmethod
    def get(self, id: int) -> TEntity:
        raise NotImplementedError

    @abstractmethod
    def update(self, entity: TEntity) -> TEntity:
        raise NotImplementedError

    @abstractmethod
    def remove(self, entity: TEntity) -> TEntity:
        raise NotImplementedError

