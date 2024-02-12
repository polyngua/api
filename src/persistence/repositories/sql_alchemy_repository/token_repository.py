import uuid
from uuid import UUID
from datetime import datetime

from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session
from sqlalchemy import select, delete, update

from src.core.entities.token import Token, TokenRepository
from src.persistence.database import models


class SqlAlchemyTokenRepository(TokenRepository):
    def __init__(self, session: Session) -> None:
        """
        Create the class by storing the session.
        """
        super().__init__()

        self.session = session

    def add(self, token: Token) -> Token:
        """
        Add the given token to the database, assuming no ID has been given to the token (i.e., the token is not already
        in the database).
        """
        ID = uuid.uuid4()
        token.ID = ID

        token_row = models.Token(
            ID=ID,
            token=token.token,
            expires=token.expiration,
            user_id=token.user_id
        )

        self.session.add(token_row)
        self.session.commit()

        return token

    def create(self, token: str, expiration: datetime, user_id: UUID) -> Token:
        """
        Creates a token using the given parameters, adds it to the database, and returns the newly created token.
        """
        return self.add(Token(
            None,
            token,
            expiration,
            user_id  # TODO: It might be important to check that this user does indeed exists; although if the user
                     #  doesn't, it won't really do any harm will it?
        ))

    def get(self, ID: UUID) -> Token:
        """
        Returns the token with the given ID, raising an error if it does not exist.
        """
        result = self.get_token_row(ID)

        return Token(ID, result.token, result.expires, result.user_id)

    def get_token_row(self, ID) -> models.Token:
        """
        Utility function which returns the model for the token with the given ID.
        """
        stmt = select(models.Token).where(models.Token.ID == ID).limit(1)
        result = self.session.execute(stmt).scalars().one_or_none()
        if result is None:
            raise NoResultFound(f"Token with ID {ID} does not exist.")
        return result

    def get_by_token_string(self, token_string: str) -> Token:
        """
        Returns the token object with the given token, raising an error if it does not exist.
        """
        stmt = select(models.Token).where(models.Token.token == token_string).limit(1)
        result = self.session.execute(stmt).scalars().one_or_none()

        if result is None:
            raise NoResultFound(f"Token with string {token_string} does not exist.")

        return Token(result.ID, result.token, result.expires, result.user_id)

    def remove(self, ID: UUID) -> Token:
        """
        Deletes the token with the given ID, raising an error if it does not exist.
        """
        output_object = self.get(ID)
        stmt = delete(models.Token).where(models.Token.ID == ID)
        self.session.execute(stmt)
        self.session.commit()

        return output_object

    def update(self, token: Token) -> Token:
        """
        Updates the given token in the database. Note that we match the tokens using the ID of the given token.

        Other changed fields are updated, apart from the user_id. There is no way to change the user that is
        authenticated by a given token.
        """
        self.get_token_row(token.ID)  # THis value is not used, but this function does check that the token exists.

        stmt = (update(models.Token)
                .where(models.Token.ID == token.ID)
                .values(token=token.token,
                        expires=token.expiration))  # Note that it's deliberate that we don't update the user_id. There
                                                    # should not be any easy way of changing the user who is
                                                    # authenticated by a token.

        self.session.execute(stmt)
        self.session.commit()

        return self.get(token.ID)

