from uuid import UUID

from src.core.entities import Conversation, Message, ConversationAggregateRepository
from src.core.services.response_pipeline import ResponsePipeline, WhisperAPI, OpenAILLM, OpenAITTS
from io import BytesIO


class CreateConversationUseCase:
    """
    Create a new conversation and return to the user.
    """
    def __init__(self, repository: ConversationAggregateRepository):
        self.repository = repository

    def execute(self, name: str) -> Conversation:
        with self.repository as repo:
            conversation = repo.create(name, "You are an AI")

        return conversation


class SendTextMessageToConversationUseCase:
    """
    Sends a textual message to the conversation and returns a response from GPT.
    """
    def __init__(self,
                 repository: ConversationAggregateRepository,
                 conversation_id: UUID):
        self.repository = repository
        self.conversation_id = conversation_id

    async def execute(self, text: str) -> Message:
        conversation = self.repository.get(self.conversation_id)

        pipeline = ResponsePipeline(
            conversation,
            WhisperAPI(),
            OpenAILLM("gpt-3.5-turbo"),
            OpenAITTS("alloy")
        )

        assistant_response = await pipeline.get_response(text, include_audio=False)

        self.repository.create_message_in_conversation(Message(None, "user", text, None), self.conversation_id)
        self.repository.create_message_in_conversation(assistant_response, self.conversation_id)

        return assistant_response


class SendAudioMessageToConversationUseCase:
    def __init__(self,
                 repository: ConversationAggregateRepository,
                 conversation_id: UUID):
        self.repository = repository
        self.conversation_id = conversation_id

    async def execute(self, audio: BytesIO) -> Message:
        # TODO: eventually this will need to be made more performant; perhaps the audio can be streamed and transcribed
        #  on the fly, as the user speaks, and then the GPT response can be generated earlier, and then the response
        #  from GPT can be streamed in and TTS can happen on a per-sentence level, instead of waiting the whole time.
        #  and then even perhaps we can stream audio while GPT is still running or TTS is still running.
        conversation = self.repository.get(self.conversation_id)

        pipeline = ResponsePipeline(
            conversation,
            WhisperAPI(),
            OpenAILLM("gpt-3.5-turbo"),
            OpenAITTS("alloy")
        )

        assistant_response = await pipeline.get_response(audio)

        self.repository.create_message_in_conversation(Message(None, "user", pipeline.transcription, audio), self.conversation_id)
        self.repository.create_message_in_conversation(assistant_response, self.conversation_id)

        return assistant_response


class GetTextMessageUseCase:
    def __init__(self, repository: ConversationAggregateRepository, conversation_id: UUID):
        self.repository = repository
        self.conversation_id = conversation_id

    def execute(self, message_id: UUID) -> Message:
        # TODO: This will need some authentication at some point. For now though we just assume that the user has
        #  access. In particular we should check that the message is in a certain conversation and that users have
        #  access ot that very message / conversation.
        return self.repository.get_message_from_conversation(message_id, self.conversation_id)


class GetAudioMessageUseCase:
    def __init__(self, repository: ConversationAggregateRepository, conversation_id: UUID):
        self.repository = repository
        self.conversation_id = conversation_id

    def execute(self, message_id: UUID) -> BytesIO:
        # TODO: This will also need some authentication at some point. Again, for now we'll just assume that the user
        #  has the perimissions needed.
        return self.repository.get_message_from_conversation(message_id, self.conversation_id).audio
