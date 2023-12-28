from abc import ABC, abstractmethod
from typing import Optional


class Entity(ABC):
    def __init__(self, id: int = None):
        """
        Every business entity will inherit from this class, and all will have some identifier.

        :param id: this entity's identifier. Defaults to None, for when creating a new instance.
        """
        self.id: Optional[int] = id


class EntityRepository(ABC):
    @abstractmethod
    def add(self, entity: Entity) -> Entity:
        raise NotImplementedError

    @abstractmethod
    def get(self, id: int) -> Entity:
        raise NotImplementedError

    @abstractmethod
    def update(self, entity: Entity) -> Entity:
        raise NotImplementedError

    @abstractmethod
    def remove(self, entity: Entity) -> Entity:
        raise NotImplementedError

