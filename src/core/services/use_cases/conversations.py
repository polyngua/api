from uuid import UUID

from src.core.entities import Conversation, Message, ConversationAggregateRepository
from src.core.services.data_transfer_objects import ConversationOut, MessageOut
from src.core.services.use_cases.gpt_helper import get_gpt_reply, transcribe_audio, text_to_speech
from io import BytesIO


class CreateConversationUseCase:
    """
    Create a new conversation and return to the user.
    """
    def __init__(self, repository: ConversationAggregateRepository):
        self.repository = repository

    def execute(self, name: str) -> ConversationOut:
        with self.repository as repo:
            conversation = repo.create(name, "You are an AI")

        conversation = ConversationOut(**conversation.as_dict())

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

    def execute(self, text: str) -> MessageOut:
        # Message is created this way so that the returned message has an ID.
        self.repository.create_message_in_conversation(Message(None, "user", text, None), self.conversation_id)

        conversation = self.repository.get(self.conversation_id)

        assistant_response = self.repository.create_message_in_conversation(
            get_gpt_reply(conversation),  # Note that this is the message created by GPT that we are adding here.
            self.conversation_id)

        return MessageOut(**assistant_response.as_dict())


class SendAudioMessageToConversationUseCase:
    def __init__(self,
                 repository: ConversationAggregateRepository,
                 conversation_id: UUID):
        self.repository = repository
        self.conversation_id = conversation_id

    def execute(self, audio: BytesIO) -> MessageOut:
        # TODO: eventually this will need to be made more performant; perhaps the audio can be streamed and transcribed
        #  on the fly, as the user speaks, and then the GPT response can be generated earlier, and then the response
        #  from GPT can be streamed in and TTS can happen on a per-sentence level, instead of waiting the whole time.
        #  and then even perhaps we can stream audio while GPT is still running or TTS is still running.
        transcription = transcribe_audio(audio)

        # Add the user's message to the conversation.
        self.repository.create_message_in_conversation(Message(None, "user", transcription, audio), self.conversation_id)
        conversation = self.repository.get(self.conversation_id)

        # Get GPT's response, audio, and add to the conversation.
        assistant_response = get_gpt_reply(conversation)
        assistant_audio = text_to_speech(assistant_response.content)
        assistant_response.audio = assistant_audio
        assistant_response = self.repository.create_message_in_conversation(assistant_response, self.conversation_id)

        return MessageOut(**assistant_response.as_dict())


class GetTextMessageUseCase:
    def __init__(self, repository: ConversationAggregateRepository, conversation_id: UUID):
        self.repository = repository
        self.conversation_id = conversation_id

    def execute(self, message_id: UUID) -> MessageOut:
        # TODO: This will need some authentication at some point. For now though we just assume that the user has
        #  access. In particular we should check that the message is in a certain conversation and that users have
        #  access ot that very message / conversation.
        return MessageOut(**self.repository.get_message_from_conversation(message_id, self.conversation_id).as_dict())


class GetAudioMessageUseCase:
    def __init__(self, repository: ConversationAggregateRepository, conversation_id: UUID):
        self.repository = repository
        self.conversation_id = conversation_id

    def execute(self, message_id: UUID) -> BytesIO:
        # TODO: This will also need some authentication at some point. Again, for now we'll just assume that the user
        #  has the perimissions needed.
        return self.repository.get_message_from_conversation(message_id, self.conversation_id).audio
