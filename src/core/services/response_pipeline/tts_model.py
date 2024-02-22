from abc import ABC, abstractmethod
from io import BytesIO
from openai import OpenAI


class TTSModel(ABC):
    @abstractmethod
    async def synthesise_speech(self, text: str) -> BytesIO:
        raise NotImplementedError


class OpenAITTS(TTSModel):
    def __init__(self, voice: str):
        self.voice = voice
        self.client = OpenAI()

    async def synthesise_speech(self, text: str) -> BytesIO:
        """
        Sends the text to OpenAI's TTS model and returns the audio.

        :param text: the text to synthesise.
        :return: the audio.
        """
        gpt_audio = self.client.audio.speech.create(model="tts-1", voice=self.voice, input=text)

        audio = BytesIO()
        audio.name = "audio.wav"

        for chunk in gpt_audio.iter_bytes(chunk_size=1024):
            audio.write(chunk)

        return audio