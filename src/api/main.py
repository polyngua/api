from typing import Annotated

import uvicorn
from fastapi import FastAPI, UploadFile, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy import create_engine
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import sessionmaker
from starlette import status

from src.api.schemas import *
from src.api.schemas.token import TokenOut
from src.core.services.use_cases import *
from src.persistence.database.models import Base
from src.persistence.repositories.sql_alchemy_repository.conversation_aggregate_repository import \
    SqlAlchemyConversationAggregateRepository
from src.persistence.repositories.sql_alchemy_repository.token_repository import SqlAlchemyTokenRepository
from src.persistence.repositories.sql_alchemy_repository.user_repository import SqlAlchemyUserRepository

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # List of allowed origins. Todo: this is currently allowing all. That's just for dev purposes.
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

engine = create_engine("sqlite://")
Session = sessionmaker(bind=engine)

Base.metadata.create_all(bind=engine)


def get_conversation_aggregate_repository(transaction_user: User) -> ConversationAggregateRepository:
    session = Session(bind=engine)

    return SqlAlchemyConversationAggregateRepository(transaction_user, session)


def get_user_repository() -> UserRepository:
    session = Session(bind=engine)

    return SqlAlchemyUserRepository(session)


def get_token_repository() -> TokenRepository:
    session = Session(bind=engine)

    return SqlAlchemyTokenRepository(session)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(access_token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    return ValidateTokenAndGetUserUseCase(get_token_repository(), get_user_repository()).execute(access_token)


@app.post("/conversations")
async def create_conversation(current_user: Annotated[User, Depends(get_current_user)]) -> ConversationOut:
    """
    Create a conversation with a unique ID and the given name.

    :param current_user: The logged in user.
    :return: The newly created Conversation object.
    """
    new_conversation = CreateConversationUseCase(get_conversation_aggregate_repository(current_user)).execute(current_user.first_name)

    return ConversationOut(**new_conversation.as_dict())


@app.get("/conversations/{conversation_id}/messages/{message_id}/text")
async def get_text_conversation_message(conversation_id: UUID, message_id: UUID, current_user: Annotated[User, Depends(get_current_user)]) -> MessageOut:
    """
    Returns the text associated with the given message.

    :param conversation_id: the conversation that the message is in. Note that this isn't used yet.
    :param message_id: the message whose text to return.
    :param current_user: the logged in user.
    :return: the text.
    """
    text_message = GetTextMessageUseCase(get_conversation_aggregate_repository(current_user), conversation_id).execute(message_id)

    return MessageOut(**text_message.as_dict())


@app.get("/conversations/{conversation_id}/messages/{message_id}/audio")
async def get_audio_conversation_message(conversation_id: UUID, message_id: UUID, current_user: Annotated[User, Depends(get_current_user)]) -> StreamingResponse:
    """
    Gets the audio for the given message.

    :param conversation_id: the conversation that the message is in. Note that this is not currently used for anything.
    :param message_id: the id of the message whose audio we want to get.
    :param current_user: the logged in user.
    :return: the audio as a streamed response.
    """
    audio = GetAudioMessageUseCase(get_conversation_aggregate_repository(current_user), conversation_id).execute(message_id)
    audio.seek(0)

    return StreamingResponse(audio, media_type="audio/wav")


@app.post("/conversations/{conversation_id}/messages/text")
async def create_text_conversation_message(conversation_id: UUID, new_message: MessageIn, current_user: Annotated[User, Depends(get_current_user)]) -> MessageOut:
    """
    Sends the given message to the given conversation and returns the response from GPT.

    :param conversation_id: the conversation to add the message to.
    :param new_message: the message being sent.
    :return: the response from GPT.
    """
    sent_message = SendTextMessageToConversationUseCase(get_conversation_aggregate_repository(current_user),
                                                        conversation_id).execute(new_message.content)

    return MessageOut(**sent_message.as_dict())


@app.post("/conversations/{conversation_id}/messages/audio")
async def create_audio_conversation_message(conversation_id: UUID, recording: UploadFile, current_user: Annotated[User, Depends(get_current_user)]) -> MessageOut:
    """
    Sends the given (audio) message to the given conversation and returns the (textual) response from GPT.

    :param conversation_id: the conversation to send the message to.
    :param recording: the audio recording of the message,
    :return: the textual response of the message.
    """
    if recording.content_type not in ["audio/wav", "audio/x-wav"]:
        raise HTTPException(status_code=415, detail="Unsupported audio format. Please upload a WAV file.")

    audio = BytesIO(await recording.read())
    audio.name = "audio.wav"

    text_response = SendAudioMessageToConversationUseCase(get_conversation_aggregate_repository(current_user),
                                                          conversation_id).execute(audio)

    return MessageOut(**text_response.as_dict())


@app.post("/users")
async def create_user(new_user: UserCreate) -> UserOut:
    """
    Creates a new user.
    """
    user_to_create = User(None, new_user.email,
                          new_user.first_name,
                          new_user.surname)

    created_user = CreateUserUseCase(get_user_repository()).execute(user_to_create, new_user.password)

    return UserOut(**created_user.as_dict())


@app.post("/tokens")
async def create_token(login_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> TokenOut:
    email = login_data.username
    password = login_data.password

    try:
        access_token = (AuthenticateUserAndCreateTokenUseCase(SqlAlchemyTokenRepository(Session(bind=engine)), get_user_repository())
                        .execute(email, password))
    except NoResultFound as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials")

    return TokenOut(access_token=access_token.token, token_type="bearer")


@app.get("/users/me")
async def get_logged_in_user(current_user: Annotated[User, Depends(get_current_user)]) -> UserOut:
    return UserOut(ID=current_user.ID,
                   email=current_user.email,
                   first_name=current_user.first_name,
                   surname=current_user.surname)


@app.get("/")
async def root():
    return {"message": "Hello World"}


if __name__ == "__main__":

    # While testing we create an account (because there is no proper persistence yet).
    CreateUserUseCase(get_user_repository()).execute(User(
        None,
        "connor@polyngua.com",
        "Connor",
        "Keevill"
    ),
        "password")

    uvicorn.run(app, host="127.0.0.1", port=8000)
