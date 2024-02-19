from abc import ABC, abstractmethod
from io import BytesIO

import multimethod

from src.core.entities import Conversation, Message


class TranscriptionModel(ABC):
    @abstractmethod
    def transcribe_audio(self, audio: BytesIO) -> str:
        raise NotImplementedError


class LanguageModel(ABC):
    @abstractmethod
    def generate_message(self, conversation_history: list[Message]) -> str:
        raise NotImplementedError


class TTSModel(ABC):
    @abstractmethod
    def synthesise_speech(self, text: str) -> BytesIO:
        raise NotImplementedError


class ResponsePipeline:
    def __init__(self,
                 conversation: Conversation,
                 transcriber: TranscriptionModel,
                 language_model: LanguageModel,
                 tts_model: TTSModel):
        self.conversation = conversation
        self.transcriber = transcriber
        self.language_model = language_model
        self.tts_model = tts_model

    @multimethod
    def get_response(self, audio: BytesIO, include_audio: bool = True) -> Message:
        pass

    @multimethod
    def get_response(self, text, include_audio: bool = True):
        pass
