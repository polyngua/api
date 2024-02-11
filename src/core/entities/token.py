from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from src.core.entities import Entity, EntityRepository


class Token(Entity):
    def __init__(self, ID: UUID, token: str, expiration: datetime, user_id: UUID):
        super().__init__(ID)
        self.token = token
        self.expiration = expiration
        self.user_id = user_id

    def has_expired(self) -> bool:
        """
        Returns a boolean indicating whether the token has expired.
        """
        return self.expiration < datetime.now()


class TokenRepository(EntityRepository, ABC):
    @abstractmethod
    def get_by_token_str(self, token: str) -> Token:
        raise NotImplementedError
