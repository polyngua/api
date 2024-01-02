"""
This file is a temporary helpers file for now. A more permanent solution will see the AI stuff moved closer to the
entities and tidied up, but I haven't decided on an interface for that yet.
"""

from openai import OpenAI
from entities import Message, Conversation
from io import BytesIO

# This is very temporary - just for quick movement with MVP.
OPENAI_API_KEY = "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"
OPENAI_MODEL = "gpt-3.5-turbo"


gpt = OpenAI(api_key=OPENAI_API_KEY)


def message_to_dict(message: Message) -> dict[str, str]:
    """
    Converts a message to the dictionary format that OpenAI expects to receive messages in.

    :param message: the message to convert.
    :return: the converted message.
    """
    return {"role": message.role, "content": message.content}


def conversation_to_message_list(conversation: Conversation) -> list[dict[str, str]]:
    """
    Converts a conversation into a list of dicts which are in the format that OpenAI expects to receive messages in.

    :param conversation: the conversation to convert.
    :return: the converted conversation.
    """
    return [message_to_dict(message) for message in conversation.messages.values()]


def get_gpt_reply(conversation: Conversation) -> Message:
    """
    Sends the given conversation to OpenAI, returns the response as a Message entity.

    :param conversation: the conversation so far.
    :return: the response from GPT.
    """
    messages = conversation_to_message_list(conversation)

    response = gpt.chat.completions.create(model=OPENAI_MODEL, messages=messages)
    gpt_message = response.choices[0].message.content

    return Message(None, "assistant", gpt_message)


def transcribe_audio(audio: BytesIO) -> str:
    return gpt.audio.transcriptions.create(model="whisper-1", file=audio)


def text_to_speech(text: str) -> BytesIO:
    return gpt.audio.speech.create(model="tts-1", voice="echo", input=text)