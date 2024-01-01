"""
As the project develops, we should move some of this code into the core project, which these dependencies will depend upon.
But this will do, for now.
"""
from entities import Conversation, ConversationRepository


class GetConversationDependency:
    def __init__(self, repo: ConversationRepository):
        self.repo = repo

    def execute(self, conversation_id: int) -> Conversation:
        """
        Returns the conversation with the given ID, if it exists.

        :param id: the id of the conversation to get.
        :return: the conversation.
        """
        return self.repo.get(conversation_id)
