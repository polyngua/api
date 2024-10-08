import uuid
from uuid import UUID

import bcrypt

from src.core.entities.user import User, UserRepository
from src.persistence.repositories.base_repository import SessionManagerRepository
from src.persistence.database import models
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound


class SqlAlchemyUserRepository(UserRepository, SessionManagerRepository):

    def __init__(self, session: Session):
        self.session = session

    def commit(self):
        self.session.commit()

    def add(self, user: User, password: str) -> User:
        """
        Adds a new user to the database, hashing the given password to store in the database.
        """
        ID = uuid.uuid4()
        user.ID = ID

        hashed = self.hash(password)

        user_row = models.User(ID=user.ID, email=user.email, password=hashed, first_name=user.first_name, surname=user.surname)
        self.session.add(user_row)
        self.commit()

        return user

    def hash(self, password):
        bites = password.encode()
        DEVELOPMENT_SALT = "$2b$12$/ymyFM04I4BnHbvuHu2GSu"
        hashed = bcrypt.hashpw(bites, DEVELOPMENT_SALT.encode()).decode()  # TODO: CHANGE THIS SALT
        return hashed

    def get(self, ID: UUID) -> User:
        # TODO: Authenticate that the right password has been given somewhere.
        user_row = self._get_user_model(ID)

        return User(ID=user_row.ID, email=user_row.email, first_name=user_row.first_name, surname=user_row.surname)

    def get_by_email_and_password(self, email: str, password: str) -> User:

        hashed_password = self.hash(password)

        user_row = (self.session.query(models.User)
                    .filter(models.User.email == email)
                    .filter(models.User.password == hashed_password)
                    .one_or_none())

        if user_row is None:
            raise NoResultFound(f"Invalid email or password")

        return User(ID=user_row.ID, email=user_row.email, first_name=user_row.first_name, surname=user_row.surname)

    def create(self, email: str, first_name: str, surname: str, password: str) -> User:

        return self.add(User(None, email, first_name, surname), password)

    def update(self, user: User) -> User:
        user_row = self._get_user_model()

        user_row.email = user.email
        user_row.first_name = user.first_name
        user_row.surname = user.surname

        self.session.commit()

        return user

    def remove(self, ID: UUID) -> User:
        user = self.get(ID)
        user_row = self._get_user_model(ID)

        self.session.delete(user_row)
        self.session.commit()

        return user

    def _get_user_model(self, ID: UUID) -> models.User:
        """
        Gets the model associated with the row that has the given ID
        """
        user_row = self.session.query(models.User).filter(ID == models.User.ID).one_or_none()

        if user_row is None:
            raise NoResultFound(f"User with ID {ID} not found")

        return user_row



