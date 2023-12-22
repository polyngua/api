import uuid
from io import BytesIO


class Message:
    def __init__(self, role: str, content: str, audio: BytesIO = None) -> None:
        self.identifier: str = str(uuid.uuid4())
        self.role: str = role
        self.content: str = content
        self.audio: BytesIO = audio
