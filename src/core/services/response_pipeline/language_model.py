from abc import ABC, abstractmethod
from src.core.entities import Message
from openai import OpenAI


class LanguageModel(ABC):
    @abstractmethod
    async def generate_message(self, conversation_history: list[Message]) -> str:
        raise NotImplementedError


class OpenAILLM(LanguageModel):
    def __init__(self, model_generation: str):
        self.model_generation = model_generation
        self.client = OpenAI()

    async def generate_message(self, conversation_history: list[Message]) -> str:
        """
        Generates a response from the OpenAI language model.

        :param conversation_history: the conversation history.
        :return: the generated response.
        """
        messages = [self.message_to_dict(message) for message in conversation_history]
        response = self.client.chat.completion.create(model=self.model_generation, messages=messages)
        return response.choices[0].message.content

    def message_to_dict(self, message: Message) -> dict[str, str]:
        """
        Converts a message to the dictionary format that OpenAI expects to receive messages in.

        :param message: the message to convert.
        :return: the converted message.
        """
        return {"role": message.role, "content": message.content}
