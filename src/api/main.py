import asyncio
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

DEVELOPMENT = True
DEVELOPMENT_USER_DETAILS = {
    "email": "connor@polyngua.com",
    "password": "password",
    "first_name": "Connor",
    "surname": "Keevill"
}

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


async def get_user_repository() -> UserRepository:
    """
    Dependency for getting the user repository. This can be configured to change the type of repo injected.
    """
    session = Session(bind=engine)

    return SqlAlchemyUserRepository(session)


async def get_token_repository() -> TokenRepository:
    """
    Dependency for getting the token repository. This can be configured to change the type of repo injected.
    """
    session = Session(bind=engine)

    return SqlAlchemyTokenRepository(session)


# This allows the user to log in
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

if DEVELOPMENT:
    oauth2_scheme = lambda: "token"


async def get_current_user(access_token: Annotated[str, Depends(oauth2_scheme)],
                           token_repo: Annotated[TokenRepository, Depends(get_token_repository)],
                           user_repo: Annotated[UserRepository, Depends(get_user_repository)]) -> User:
    """
    Dependency for validating a token and returning an instance of the user the token belongs to (should all validation
    checks pass).
    """
    if DEVELOPMENT:
        return GetUserUseCase(user_repo).execute(DEVELOPMENT_USER_DETAILS["email"],
                                                      DEVELOPMENT_USER_DETAILS["password"])

    return ValidateTokenAndGetUserUseCase(token_repo, user_repo).execute(access_token)


async def verify_user_and_get_conversation_aggregate_repository(
        transaction_user: Annotated[User, Depends(get_current_user)]
        ) -> ConversationAggregateRepository:
    """
    Dependency for getting the conversation aggregate root repository. Note that because these repos need a user, this
    dependency also validates the user's token to provide to the repository.
    """
    session = Session(bind=engine)

    return SqlAlchemyConversationAggregateRepository(transaction_user, session)


@app.post("/conversations")
async def create_conversation(
        current_user: Annotated[User, Depends(get_current_user)],
        repo: Annotated[ConversationAggregateRepository, Depends(verify_user_and_get_conversation_aggregate_repository)]
) -> ConversationOut:
    """
    Create a conversation with a unique ID and the given name.

    :param current_user: The logged in user.
    :param repo: The repository to give to the use case.
    :return: The newly created Conversation object.
    """
    new_conversation = CreateConversationUseCase(repo).execute(current_user.first_name)

    return ConversationOut(**new_conversation.as_dict())


@app.get("/conversations/{conversation_id}/messages/{message_id}/text")
async def get_text_conversation_message(
        conversation_id: UUID,
        message_id: UUID,
        repo: Annotated[ConversationAggregateRepository, Depends(verify_user_and_get_conversation_aggregate_repository)]
) -> MessageOut:
    """
    Returns the text associated with the given message.

    :param conversation_id: the conversation that the message is in. Note that this isn't used yet.
    :param message_id: the message whose text to return.
    :param repo: the repository for the use case. Note that this will verify the user.
    :return: the text.
    """
    text_message = GetTextMessageUseCase(repo, conversation_id).execute(message_id)

    return MessageOut(**text_message.as_dict())


@app.get("/conversations/{conversation_id}/messages/{message_id}/audio")
async def get_audio_conversation_message(
        conversation_id: UUID,
        message_id: UUID,
        repo: Annotated[ConversationAggregateRepository, Depends(verify_user_and_get_conversation_aggregate_repository)]
) -> StreamingResponse:
    """
    Gets the audio for the given message.

    :param conversation_id: the conversation that the message is in. Note that this is not currently used for anything.
    :param message_id: the id of the message whose audio we want to get.
    :param repo: the repository for the use case. Note that this dependency will also verify the user.
    :return: the audio as a streamed response.
    """
    audio = GetAudioMessageUseCase(repo, conversation_id).execute(message_id)
    audio.seek(0)

    return StreamingResponse(audio, media_type="audio/wav")


@app.post("/conversations/{conversation_id}/messages/text")
async def create_text_conversation_message(
        conversation_id: UUID,
        new_message: MessageIn,
        repo: Annotated[ConversationAggregateRepository, Depends(verify_user_and_get_conversation_aggregate_repository)]
) -> MessageOut:
    """
    Sends the given message to the given conversation and returns the response from GPT.

    :param conversation_id: the conversation to add the message to.
    :param new_message: the message being sent.
    :param repo: the repository for the use case. This also verifies the user.
    :return: the response from GPT.
    """
    sent_message = SendTextMessageToConversationUseCase(repo, conversation_id).execute(new_message.content)

    return MessageOut(**sent_message.as_dict())


@app.post("/conversations/{conversation_id}/messages/audio")
async def create_audio_conversation_message(
        conversation_id: UUID,
        recording: UploadFile,
        repo: Annotated[ConversationAggregateRepository, Depends(verify_user_and_get_conversation_aggregate_repository)]
) -> MessageOut:
    """
    Sends the given (audio) message to the given conversation and returns the (textual) response from GPT.

    :param conversation_id: the conversation to send the message to.
    :param recording: the audio recording of the message,
    :param repo: the repository for the use case. This also verifies the user
    :return: the textual response of the message.
    """
    if recording.content_type not in ["audio/wav", "audio/x-wav"]:
        raise HTTPException(status_code=415, detail="Unsupported audio format. Please upload a WAV file.")

    audio = BytesIO(await recording.read())
    audio.name = "audio.wav"

    text_response = SendAudioMessageToConversationUseCase(repo, conversation_id).execute(audio)

    return MessageOut(**text_response.as_dict())


@app.post("/users")
async def create_user(new_user: UserCreate,
                      repo: Annotated[UserRepository, Depends(get_user_repository)]) -> UserOut:
    """
    Creates a new user.
    """
    user_to_create = User(None, new_user.email,
                          new_user.first_name,
                          new_user.surname)

    created_user = CreateUserUseCase(repo).execute(user_to_create, new_user.password)

    return UserOut(**created_user.as_dict())


@app.post("/tokens")
async def create_token(login_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                       token_repository: Annotated[TokenRepository, Depends(get_token_repository)],
                       user_repository: Annotated[UserRepository, Depends(get_user_repository)]) -> TokenOut:
    """
    Authenticates the given user details (extracted from form data using the OAuth2PasswordRequestForm) and creates a
    new token for them.

    :param login_data: the login data, as per the OAuth2 standard.
    :param token_repository: the repo for accessing the tokens.
    :param user_repository: the repo for accessing the users.
    :return: the TokenOut response.
    """
    email = login_data.username
    password = login_data.password

    try:
        access_token = (AuthenticateUserAndCreateTokenUseCase(token_repository, user_repository)
                        .execute(email, password))
    except NoResultFound as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials")

    return TokenOut(access_token=access_token.token, token_type="bearer")


@app.get("/users/me")
async def get_logged_in_user(current_user: Annotated[User, Depends(get_current_user)]) -> UserOut:
    """
    Returns info about user sending the request (i.e., authenticates their token and gets some basic account info.

    :param current_user: the user sending the request, authenticated by the token.
    :return: the UserOut response.
    """
    return UserOut(ID=current_user.ID,
                   email=current_user.email,
                   first_name=current_user.first_name,
                   surname=current_user.surname)


if __name__ == "__main__":
    if DEVELOPMENT:
        # While testing we create an account (because there is no proper persistence yet).
        CreateUserUseCase(asyncio.run(get_user_repository())).execute(User(
            None,
            DEVELOPMENT_USER_DETAILS["email"],
            DEVELOPMENT_USER_DETAILS["first_name"],
            DEVELOPMENT_USER_DETAILS["surname"],
        ),
            DEVELOPMENT_USER_DETAILS["password"])

    uvicorn.run(app, host="127.0.0.1", port=8000)
