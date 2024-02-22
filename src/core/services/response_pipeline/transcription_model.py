from abc import ABC, abstractmethod
from openai import OpenAI
from io import BytesIO


class TranscriptionModel(ABC):
    @abstractmethod
    async def transcribe_audio(self, audio: BytesIO) -> str:
        raise NotImplementedError


class WhisperAPI(TranscriptionModel):
    def __init__(self):
        self.client = OpenAI()

    async def transcribe_audio(self, audio: BytesIO) -> str:
        """
        Sends the audio to OpenAI's Whisper model and returns the transcription.

        :param audio:
        :return:
        """
        return self.client.audio.transcriptions.create(model="whisper-1", file=audio).text
