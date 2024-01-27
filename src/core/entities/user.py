from abc import ABC
from uuid import UUID

from entity import Entity, EntityRepository


class User(Entity):

    def __init__(self, ID: UUID, email: str, first_name: str, surname: str, languages: list[str]):
        super().__init__(ID)
        self.email = email
        self.first_name = first_name
        self.surname = surname
        self.languages = languages


class UserRepository(EntityRepository, ABC):
    ...
