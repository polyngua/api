import uvicorn
from io import BytesIO
from uuid import uuid4
from fastapi import FastAPI, HTTPException, UploadFile, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from typing import Annotated
from services.data_transfer_objects import MessageIn, ConversationOut, ConversationIn
from services.use_cases import *
from dependencies import *

import persistence

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # List of allowed origins. Todo: this is currently allowing all. That's just for dev purposes.
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.post("/conversations")
async def create_conversation(name: ConversationIn) -> ConversationOut:
    """
    Create a conversation with a unique ID and the given name.

    :param name: The name of the conversation.
    :return: The newly created Conversation object.
    """
    return CreateConversationUseCase(persistence.repositories.MemoryConversationRepository()).execute(name.name)


@app.get("/conversations/{conversation_id}/messages/{message_id}/text")
async def get_text_conversation_message(conversation_id: int, message_id: int) -> MessageOut:
    """
    Returns the text associated with the given message.

    :param conversation_id: the conversation that the message is in. Note that this isn't used yet.
    :param message_id: the message whose text to return.
    :return: the text.
    """

    # TODO: Note that this doesn't perform any verification that the message is in the conversation or (eventually) that
    #  the user has access to see this message / conversation.
    return GetTextMessageUseCase(persistence.MemoryMessageRepository()).execute(message_id)

    # TODO: Keeping the below because of the error handling it supports. That will be needed eventually.
    # """
    # Retrieves a specific message from a conversation.
    #
    # :param conversation_id: The ID of the conversation.
    # :param message_id: The ID of the message in the conversation.
    # :return: The requested message.
    # :raises HTTPException: If the conversation or message index is not found.
    # """
    # if conversation_id not in conversations:
    #     raise HTTPException(status_code=404, detail="Conversation not found.")
    #
    # conversation = conversations[conversation_id]
    #
    # if message_id not in conversation:
    #     raise HTTPException(status_code=404, detail="Message not found")
    #
    # return conversation.get_message(message_id)


@app.get("/conversations/{conversation_id}/messages/{message_id}/audio")
async def get_audio_conversation_message(conversation_id: int, message_id: int) -> StreamingResponse:
    """
    Gets the audio for the given message.

    :param conversation_id: the conversation that the message is in. Note that this is not currently used for anything.
    :param message_id: the id of the message whose audio we want to get.
    :return: the audio as a streamed response.
    """
    audio = GetAudioMessageUseCase(persistence.MemoryMessageRepository()).execute(message_id)
    audio.seek(0)

    return StreamingResponse(audio, media_type="audio/wav")

    # TODO: Again, this is only being kept due to the error handling it contains
    #
    # """
    # Retrieves the audio associated with a specific message from a conversation
    #
    # :param conversation_id: the ID of the conversation of interest.
    # :param message_id: the ID of the message of interest.
    # :return: the audio of this message.
    # """
    # if conversation_id not in conversations:
    #     raise HTTPException(status_code=404, detail="Conversation not found.")
    #
    # conversation = conversations[conversation_id]
    #
    # if message_id not in recordings:
    #     raise HTTPException(status_code=404, detail="Message audio not found")
    #
    # audio_bytes = recordings[message_id]
    # audio_bytes.seek(0)
    #
    # return StreamingResponse(audio_bytes, media_type="audio/wav")


@app.post("/conversations/{conversation_id}/messages/text")
async def create_text_conversation_message(
        conversation: Annotated[Conversation, Depends(GetConversationDependency(persistence.MemoryConversationRepository()).execute)],
        message: MessageIn) -> MessageOut:
    """
    Sends the given message to the given conversation and returns the response from GPT.

    :param conversation: the conversation to add the message to.
    :param message: the message being sent.
    :return: the response from GPT.
    """
    return (SendTextMessageToConversationUseCase(
        persistence.MemoryConversationRepository(),
        persistence.MemoryMessageRepository(),
        conversation)
            .execute(message.content))

@app.post("/conversations/{conversation_id}/messages/audio")
async def create_audio_conversation_message(
        conversation: Annotated[Conversation, Depends(GetConversationDependency(persistence.MemoryConversationRepository()).execute)],
        recording: UploadFile) -> MessageOut:
    """
    Sends the given (audio) message to the given conversation and returns the (textual) response from GPT.

    :param conversation: the conversation to send the message to.
    :param recording: the audio recording of the message,
    :return: the textual response of the message.
    """

    audio = BytesIO(await recording.read())
    audio.name = "audio.wav"

    return SendAudioMessageToConversationUseCase(
        persistence.MemoryConversationRepository(),
        persistence.MemoryMessageRepository(),
        conversation).execute(audio)

    # TODO: Once again this is being keps because it has error handling which needs to be implemented again in the use
    #  case
    # if recording.content_type not in ["audio/wav", "audio/x-wav"]:
    #     raise HTTPException(status_code=415, detail="Unsupported audio format. Please upload a WAV file.")
    #
    # if conversation_id not in conversations:
    #     raise HTTPException(status_code=404, detail="Conversation not found.")
    #
    # conversation: Conversation = conversations[conversation_id]
    #
    # audio = await recording.read()
    # audio = BytesIO(audio)
    # audio.name = "audio.wav"
    #
    # transcript = gpt.audio.transcriptions.create(model="whisper-1", file=audio)
    # print("transcript:", transcript)
    #
    # message = get_gpt_reply(conversation, transcript)
    #
    # gpt_audio = gpt.audio.speech.create(model="tts-1", voice="echo", input=message.content)
    #
    # conversation.messages.append(message)
    #
    # audio_store = BytesIO()
    # audio_store.name = message.id + "mp3"
    #
    # for chunk in gpt_audio.iter_bytes(chunk_size=1024):
    #     audio_store.write(chunk)
    #
    # audio_store.seek(0)
    # recordings[message.id] = audio_store
    #
    # return message


@app.get("/")
async def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
