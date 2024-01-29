from abc import ABC
from uuid import UUID

from src.core.entities import Entity, EntityRepository


class User(Entity):
    def __init__(self, ID: UUID, email: str, first_name: str, surname: str):
        super().__init__(ID)

        self.email = email
        self.first_name = first_name
        self.surname = surname


class UserRepository(EntityRepository, ABC):
    ...
