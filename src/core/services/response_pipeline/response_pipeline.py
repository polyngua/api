from io import BytesIO
from src.core.services.response_pipeline.transcription_model import TranscriptionModel
from src.core.services.response_pipeline.language_model import LanguageModel
from src.core.services.response_pipeline.tts_model import TTSModel

import multimethod

from src.core.entities import Conversation, Message


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
    async def get_response(self, audio: BytesIO, include_audio: bool = True) -> Message:
        """
        Runs the three stage pipeline to get a response from the langauge model:

        1. Transcribe the audio.
        2. Generate a response from the language model.
        3. Run TTS on the response to get the audio (if audio is required - yes by default).

        :param audio: the audio of the incoming message.
        :param include_audio: boolean indicating whether the output message should include audio. Defaults to True.
        :return: the response message.
        """
        transcription = await self.transcriber.transcribe_audio(audio)

        return await self._get_response(include_audio, transcription)

    @multimethod
    async def get_response(self, text: str, include_audio: bool = True) -> Message:
        """
        Overload for the above method which takes text instead of audio, skipping the transcription step.

        :param text: the incoming text.
        :param include_audio: boolean indicating whether the output message should include audio. Defaults to True.
        :return: the response message.
        """
        return await self._get_response(include_audio, text)

    async def _get_response(self, text: str, include_audio: bool) -> Message:
        """
        Private message which consolidates the shared pipeline stages for the two public methods.

        :param text: the text of the message; either transcribed or directly input.
        :param include_audio: indicates whether to perform TTS.
        :return: the response.
        """
        # Creating a message here to add to the conversation, to give to the language model.
        input_message = Message(None, "user", text)
        langauge_model_response = await self.language_model.generate_message(
            self.conversation.get_all_messages().append(input_message)
        )

        if include_audio:
            audio = await self.tts_model.synthesise_speech(langauge_model_response)
        else:
            audio = None

        return Message(None, "assistant", langauge_model_response, audio)

