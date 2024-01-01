from entities import Conversation, ConversationRepository, Message, MessageRepository
from services.data_transfer_objects import ConversationOut, MessageOut
from services.use_cases.gpt_helper import get_gpt_reply


class CreateConversationUseCase:
    """
    Create a new conversation and return to the user.
    """
    def __init__(self, repository: ConversationRepository):
        self.repository = repository

    def execute(self, name: str) -> ConversationOut:
        conversation = Conversation(None, name, "You are an AI")

        with self.repository as repo:
            conversation = repo.add(conversation)

        conversation = ConversationOut(**conversation.as_dict())

        return conversation


class SendTextMessageToConversationUseCase:
    """
    Sends a textual message to the conversation and returns a response from GPT.
    """
    def __init__(self,
                 conversation_repository: ConversationRepository,
                 message_repository: MessageRepository,
                 conversation: Conversation):
        self.conversation_repository = conversation_repository
        self.message_repository = message_repository
        self.conversation = conversation

    def execute(self, text: str) -> MessageOut:
        # Message is created this way so that the returned message has an ID.
        message = self.message_repository.add(Message(None, "user", text, None))

        # Add the message to the conversation
        self.conversation.give_message(message)
        self.conversation_repository.update(self.conversation)

        assistant_response = get_gpt_reply(self.conversation)
        assistant_response = self.message_repository.add(assistant_response)

        self.conversation.give_message(assistant_response)
        self.conversation_repository.update(self.conversation)

        return MessageOut(**assistant_response.as_dict())


class SendAudioMessageToConversationUseCase:
    pass


class GetTextMessageUseCase:
    def __init__(self, repository: MessageRepository):
        self.repository = repository

    def execute(self, id: int) -> MessageOut:
        # TODO: This will need some authentication at some point. For now though we just assume that the user has
        #  access. In particular we should check that the message is in a certain conversation and that users have
        # access ot that very message / conversation.
        return MessageOut(**self.repository.get(id).as_dict())


class GetAudioMessageUseCase:
    pass


