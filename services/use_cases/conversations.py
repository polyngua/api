from entities import Conversation, ConversationRepository
from services.data_transfer_objects import ConversationOut


class CreateConversationUseCase:
    def __init__(self, repository: ConversationRepository):
        self.repository = repository

    def execute(self, name: str) -> ConversationOut:
        conversation = Conversation(None, name, "You are an AI")

        with self.repository as repo:
            conversation = repo.add(conversation)

        conversation = ConversationOut.model_validate(conversation)  # No idea if this will work.

        return conversation
