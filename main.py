from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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


class Conversation(BaseModel):
    id: str
    messages: list[dict]
    with_who: str


class Name(BaseModel):
    name: str


class Message(BaseModel):
    content: str



conversations: dict[str, Conversation] = {}
gpt = OpenAI(api_key=OPENAI_API_KEY)


@app.get("/conversations")
async def get_conversations():
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
async def get_conversation_messages(conversation_id: str):
    """
    Retrieve a list of messages from a conversation.

    :param conversation_id: The ID of the conversation.
    :return: A list of messages in the conversation.
    """
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found.")

    return conversations[conversation_id].messages


@app.get("/conversations/{conversation_id}/messages/{message_index}")
async def get_conversation_message(conversation_id: str, message_index: int):
    """
    Retrieves a specific message from a conversation.

    :param conversation_id: The ID of the conversation.
    :param message_index: The index of the message in the conversation.
    :return: The requested message.
    :raises HTTPException: If the conversation or message index is not found.
    """
    if conversation_id not in conversations:
        raise HTTPException(status_code=404, detail="Conversation not found.")

    conversation = conversations[conversation_id]

    if message_index > len(conversation.messages) + 1:
        raise HTTPException(status_code=404, detail="Message index out of range.")

    return conversation.messages[message_index]


@app.post("/conversations/{conversation_id}/messages")
async def create_conversation_message(conversation_id: str, message: Message):
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

    conversation.messages.append({"role": "user", "content": message.content})

    response = gpt.chat.completions.create(model="gpt-3.5-turbo", messages=conversation.messages)
    gpt_message = response.choices[0].message.content

    conversation.messages.append({"role": "assistant", "content": gpt_message})

    return {
        "conversation": conversation,
        "reply": gpt_message
    }


@app.get("/")
async def root():
    return {"message": "Hello World"}
