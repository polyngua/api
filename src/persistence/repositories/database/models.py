import uuid
from uuid import UUID

from sqlalchemy import create_engine, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship, sessionmaker, declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    ID: Mapped[UUID] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(60))
    password: Mapped[str] = mapped_column()
    first_name: Mapped[str] = mapped_column()
    surname: Mapped[str] = mapped_column()

    def __repr__(self) -> str:
        return f"{self.first_name} {self.surname}"



class Conversation(Base):
    __tablename__ = "conversations"

    ID: Mapped[UUID] = mapped_column(primary_key=True)


class Message(Base):
    __tablename__ = "messages"

    ID: Mapped[UUID] = mapped_column(primary_key=True)
    conversation_id: Mapped[UUID] = mapped_column(ForeignKey(Conversation.ID))
    role: Mapped[str] = mapped_column()  # TODO: This is revealing an implementation detail of the underlying OpenAI API
    content: Mapped[str] = mapped_column()

