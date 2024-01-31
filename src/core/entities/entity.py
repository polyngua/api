from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID, uuid4


class Entity(ABC):
    def __init__(self, ID: UUID = None):
        """
        Every business entity will inherit from this class, and all will have some identifier.

        :param ID: this entity's identifier. Defaults to None, for when creating a new instance.
        """
        self.ID: Optional[UUID] = ID

    def as_dict(self) -> dict:
        """
        Returns a dictionary of the object.
        """
        return self.__dict__


class EntityRepository[TEntity: Entity](ABC):
    @abstractmethod
    def add(self, entity: TEntity, *args, **kwargs) -> TEntity:
        raise NotImplementedError

    @abstractmethod
    def create(self, *args, **kwargs) -> TEntity:
        raise NotImplementedError

    @abstractmethod
    def get(self, ID: UUID) -> TEntity:
        raise NotImplementedError

    @abstractmethod
    def update(self, entity: TEntity) -> TEntity:
        raise NotImplementedError

    @abstractmethod
    def remove(self, ID: UUID) -> TEntity:
        raise NotImplementedError

