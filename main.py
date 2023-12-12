from io import BytesIO
from uuid import uuid4
from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from openai import OpenAI
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:63342"],  # List of allowed origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


# This is very temporary - just for quick movement with MVP.
OPENAI_API_KEY = "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"


class MessageOut(BaseModel):
    id: str
    role: str
    content: str


class MessageIn(BaseModel):
    content: str

recordings: dict[str, BytesIO] = {}

class Conversation(BaseModel):
    id: str
    messages: list[MessageOut]
    with_who: str

    def __contains__(self, item) -> bool:
        return item in [message.id for message in self.messages]

    def get_message(self, message_id):
        if message_id not in self:
            raise ValueError(f"Message with ID {message_id} does not exist.")

        for message in self.messages:
            if message.id == message_id:
                return message


class Name(BaseModel):
    name: str


conversations: dict[str, Conversation] = {}
gpt = OpenAI(api_key=OPENAI_API_KEY)


@app.get("/conversations")
async def get_conversations() -> dict[str, Conversation]:
    """
    Get all conversations.

    :return: A list of conversations.
    """
    return conversations


@app.get("/conversations/{id}", response_model=Conversation)
async def get_conversation(id: str):
    """
    :param id: The unique identifier of the conversation.
    :return: The conversation with the specified ID.
    """
    if id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found.")

    return conversations[id]


@app.post("/conversations", response_model=Conversation)
async def create_conversation(name: Name):
    """
    Create a conversation with a unique ID and the given name.

    :param name: The name of the conversation.
    :return: The newly created Conversation object.
    """
    print("Creating a conversation with name", name.name)

    conversation_id = str(uuid4())

    # If this ever happens then it's a remarkable think. Odds are so low.
    while conversation_id in conversations:
        conversation_id = str(uuid4())

    new_conversation = Conversation(id=conversation_id, messages=[], with_who=name.name)
    conversations[conversation_id] = new_conversation

    return new_conversation


@app.get("/conversations/{conversation_id}/messages", response_model=list)
async def get_all_conversation_messages(conversation_id: str):
    """
    Retrieve a list of messages from a conversation.

    :param conversation_id: The ID of the conversation.
    :return: A list of messages in the conversation.
    """
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found.")

    return conversations[conversation_id].messages


@app.get("/conversations/{conversation_id}/messages/{message_id}/text")
async def get_text_conversation_message(conversation_id: str, message_id: str):
    """
    Retrieves a specific message from a conversation.

    :param conversation_id: The ID of the conversation.
    :param message_id: The ID of the message in the conversation.
    :return: The requested message.
    :raises HTTPException: If the conversation or message index is not found.
    """
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found.")

    conversation = conversations[conversation_id]

    if message_id not in conversation:
        raise HTTPException(status_code=404, detail="Message not found")

    return conversation.get_message(message_id)


@app.get("/conversations/{conversation_id}/messages/{message_id}/audio")
async def get_audio_conversation_message(conversation_id: str, message_id: str) -> StreamingResponse:
    """
    Retrieves the audio associated with a specific message from a conversation

    :param conversation_id: the ID of the conversation of interest.
    :param message_id: the ID of the message of interest.
    :return: the audio of this message.
    """
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found.")

    conversation = conversations[conversation_id]

    if message_id not in recordings:
        raise HTTPException(status_code=404, detail="Message audio not found")

    audio_bytes = recordings[message_id]
    audio_bytes.seek(0)

    return StreamingResponse(audio_bytes, media_type="audio/wav")


@app.post("/conversations/{conversation_id}/messages/text")
async def create_text_conversation_message(conversation_id: str, message: MessageIn) -> MessageOut:
    """
    Stores the given message in the conversation, submits the message to GPT, also stores the response in the
    conversation, and returns a response with the whole conversation history, as well as the individual message.

    :param conversation_id: A string representing the ID of the conversation.
    :param message: A string representing the message to be added to the conversation.
    :return: A dictionary containing the conversation object and the generated reply message.
    """
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found.")

    conversation: Conversation = conversations[conversation_id]

    userMessage = MessageOut(
        id=str(uuid4()),
        role="user",
        content=message.content
    )

    gpt_message = get_gpt_reply(conversation, message)

    conversation.messages.append(userMessage)
    conversation.messages.append(gpt_message)

    return gpt_message


@app.post("/conversations/{conversation_id}/messages/audio")
async def create_audio_conversation_message(conversation_id: str, recording: UploadFile) -> MessageOut:
    if recording.content_type not in ["audio/wav", "audio/x-wav"]:
        raise HTTPException(status_code=415, detail="Unsupported audio format. Please upload a WAV file.")

    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found.")

    conversation: Conversation = conversations[conversation_id]

    audio = await recording.read()
    audio = BytesIO(audio)
    audio.name = "audio.wav"

    transcript = gpt.audio.transcriptions.create(model="whisper-1", file=audio)
    print("transcript:", transcript)

    message = get_gpt_reply(conversation, transcript)

    audio = gpt.audio.speech.create(model="tts-1", voice="echo", input=message.content)

    conversation.messages.append(message)

    audio_store = BytesIO()
    audio_store.name = message.id + "mp3"

    for chunk in audio.iter_bytes(chunk_size=1024):
        audio_store.write(chunk)

    audio_store.seek(0)
    recordings[message.id] = audio_store

    return message


def get_gpt_reply(conversation, user_message) -> MessageOut:
    """
    Adds the given message to the conversation and gets a response from GPT.

    :param conversation: the conversation.
    :param user_message: The message to get the reply for.
    :return: the (textual) reply from GPT.
    """
    conversation.messages.append({"role": "user", "content": user_message.text})
    response = gpt.chat.completions.create(model="gpt-3.5-turbo", messages=conversation.messages)
    gpt_message = response.choices[0].message.content
    conversation.messages.append({"role": "assistant", "content": gpt_message})

    gpt_message = MessageOut(
        id=str(uuid4()),
        role="assistant",
        content=gpt_message
    )

    return gpt_message


@app.get("/")
async def root():
    return {"message": "Hello World"}
