import uuid
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, declarative_base, relationship

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
    user_id: Mapped[UUID] = mapped_column(ForeignKey(User.ID))
    system_prompt: Mapped[str] = mapped_column()

    messages: Mapped[list["Message"]] = relationship("Message", back_populates="conversation")
    user: Mapped[User] = relationship(User)


class Message(Base):
    __tablename__ = "messages"

    ID: Mapped[UUID] = mapped_column(primary_key=True)
    conversation_id: Mapped[UUID] = mapped_column(ForeignKey(Conversation.ID))
    role: Mapped[str] = mapped_column()  # TODO: This is revealing an implementation detail of the underlying OpenAI API
    content: Mapped[str] = mapped_column()
    audio_filepath: Mapped[Optional[str]] = mapped_column()

    conversation: Mapped[Conversation] = relationship(Conversation, back_populates="messages")


class Token(Base):
    __tablename__ = "tokens"

    ID: Mapped[UUID] = mapped_column(primary_key=True)
    token: Mapped[str] = mapped_column()
    user_id: Mapped[UUID] = mapped_column(ForeignKey(User.ID))
    expires: Mapped[datetime] = mapped_column()

    user: Mapped[User] = relationship(User)
