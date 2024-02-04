from abc import ABC, abstractmethod
from uuid import UUID

from src.core.entities import Entity, EntityRepository


class User(Entity):
    def __init__(self, ID: UUID, email: str, first_name: str, surname: str):
        super().__init__(ID)

        self.email = email
        self.first_name = first_name
        self.surname = surname


class UserRepository(EntityRepository, ABC):
    @abstractmethod
    def add(self, user: User, password: str) -> User:
        """
        Python will moan about the fact that this function changes the method signature of the parent class. Indeed it
        does, but that's because the add function for a user can't just take a user Entity, because entities don't
        contain a field for a password; repositories will need to know about passwords.
        """
        raise NotImplementedError
