import uuid
from uuid import UUID

from src.core import entities
from src.core.entities import User
from src.persistence.database import models
from src.persistence.repositories.base_repository import SessionManagerRepository
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound


class SqlAlchemyConversationAggregateRepository(entities.ConversationAggregateRepository, SessionManagerRepository):
    def __init__(self, user: User, session: Session):
        super().__init__(user)

        self.session = session

    def commit(self):
        self.session.commit()

    def get(self, ID: UUID) -> entities.Conversation:
        conversation_row = self._get_conversation_model(ID)

        messages = [entities.Message(m.ID, m.role, m.content) for m in conversation_row.messages]
        conversation = entities.Conversation(ID, self.user, conversation_row.system_prompt)

        for message in messages:
            conversation.give_message(message)

        return conversation

    def add(self, conversation: entities.Conversation) -> entities.Conversation:
        ID = uuid.uuid4()
        conversation.ID = ID

        new_conversation_row = models.Conversation(ID=conversation.ID,
                                                   user_id=conversation.user.ID,  # TODO: Consider whether we need to check that user exists here.
                                                   system_prompt=conversation.get_system_prompt().content,
                                                   messages=self._messageEntitiesToModels(conversation.get_all_messages(), conversation.ID))

        self.session.add(new_conversation_row)

        return conversation

    def create(self, system_prompt: str) -> entities.Conversation:
        conversation = entities.Conversation(None, self.user, system_prompt)

        return self.add(conversation)

    def update(self, conversation: entities.Conversation) -> entities.Conversation:
        conversation_row = self._get_conversation_model(conversation.ID)

        # Quite an ugly and large conditional but by checking the current values we hope to avoid overwriting what we
        # don't need to.
        if conversation_row.user_id != conversation.user.ID:
            ...
        if conversation_row.system_prompt != conversation.get_system_prompt():
            conversation.system_prompt = conversation.system_prompt
        if conversation_row.messages != self._messageEntitiesToModels(conversation.get_all_messages(), conversation.ID):
            conversation.messages = self._messageEntitiesToModels(conversation.get_all_messages(), conversation.ID)

        # Commit the changes to the database
        self.session.commit()

        return conversation

    def remove(self, ID: UUID) -> entities.Conversation:
        conversation = self.get(ID)
        conversation_row = self._get_conversation_model(ID)

        self.session.delete(conversation_row)  # No need to remove the messages as they will cascade.
        self.session.commit()

        return conversation

    def create_message_in_conversation(self, message: entities.Message, conversation_id: UUID) -> entities.Message:
        ID = uuid.uuid4()
        message.ID = ID

        message_row = models.Message(ID=ID, conversation_id=conversation_id, role=message.role, content=message.content) # TODO: Handle audio.

        self.session.add(message_row)
        self.session.commit()

        return message

    def get_message_from_conversation(self, message_id: UUID, conversation_id: UUID) -> entities.Message:
        message_row = (self.session.query(models.Message).filter(
            models.Message.id == message_id,
            models.Message.conversation_id == conversation_id)
                       .one_or_none())

        if message_row is None:
            raise NoResultFound(f"Message with ID {message_id} either doesn't exist or is not in conversation with ID "
                                f"{conversation_id}")

        return self._messageEntityFromModel(message_row)

    def remove_message_from_conversation(self, message_id: UUID, conversation_id: UUID) -> entities.Message:
        message = self.get_message_from_conversation(message_id, conversation_id)
        message_row = self.session.query(models.Message).filter()

        self.session.delete(message_row)
        self.session.commit()

        return message

    def _get_conversation_model(self, ID):
        """
        A utility method that retrieves a Conversation model instance by its ID using pure SQLAlchemy.
        Raises a NoResultFound exception if no conversation with the given ID is found.

        :param ID: The ID of the Conversation to retrieve.
        :return: The Conversation model instance.
        """
        conversation_row = (self.session.query(models.Conversation).filter(models.Conversation.ID == ID)
                            .filter(models.Conversation.user_id == self.user.ID)
                            .one_or_none())

        if conversation_row is None:
            raise NoResultFound(f"Conversation with ID {ID} not found")

        return conversation_row

    def _messageEntityToModel(self, message: entities.Message, conversation_id: UUID) -> models.Message:
        """
        A utility method that converts a Message entity into a Message model.
        """
        return models.Message(ID=message.ID, conversation_id=conversation_id, content=message.content, role=message.role)

    def _messageEntitiesToModels(self,
                                 messages: dict[UUID, entities.Message],
                                 conversation_id: UUID) -> list[models.Message]:
        """
        Utility method that converts a dictionary of Message entities into a list of Message models (so that they can be
        committed to the database, for example).
        """
        return [self._messageEntityToModel(message, conversation_id) for message in messages.values()]

    def _messageEntityFromModel(self, message: models.Message) -> entities.Message:
        """
        Creates a Message entity from a Message model.

        The inverse of _messageEntityToModel().
        """
        return entities.Message(message.ID, message.role, message.content)

    def _messageEntitiesFromModels(self, messages: list[models.Message]) -> list[entities.Message]:
        """
        Utility methods that creates a list of Message entities from a list of Message models.
        """
        return [self._messageEntityFromModel(message) for message in messages]

