from abc import ABC
import uuid
from io import BytesIO

from entity import *


class Message(Entity):
    def __init__(self, id: int, role: str, content: str, audio: BytesIO = None) -> None:
        super().__init__(id)

        self.identifier: str = str(uuid.uuid4())
        self.role: str = role
        self.content: str = content
        self.audio: BytesIO = audio


class MessageRepository(EntityRepository, ABC):
    pass
