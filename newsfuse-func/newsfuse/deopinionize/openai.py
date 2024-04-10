import os
import openai

from openai.types.chat.chat_completion import ChatCompletion

from .base import OpinionRemover


class OpenAIOpinionRemover(OpinionRemover):
    """
    Class for removing opinions from a text using OpenAI's API.
    """

    def __init__(
        self,
        task: str,
        model: str = "",
    ) -> None:
        """
        :param translation_key: key for OpenAI API
        :param task: detailed description of the task to be sent to OpenAI API
        :param model: selected model for generating deopinionized sentences,
            defaults to "gpt-3.5-turbo"
        """
        model = model or "gpt-3.5-turbo"
        super().__init__(task, model)

    def initialize_api(self) -> None:
        """
        Sets the API key for the opinion remover.

        :param api_key: API key to be used
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set.")
        openai.api_key = api_key

    def send_request(self, content: str) -> ChatCompletion:
        """
        Sends a deopnionize request to OpenAI API.

        :param content: text to be deopinionized sentence by sentence
        :return: raw response from OpenAI API
        """
        return openai.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": self.task,
                },
                {"role": "user", "content": content},
            ],
        )

    def process_api_response(self, response: ChatCompletion) -> list[str]:
        """
        Processes the raw response from the API into a list of sentences.

        :param response: raw response from the API
        :return: list of sentences
        """
        return [
            sentence
            for choice in response.choices
            for sentence in choice.message.content.split("\n")  # type: ignore
        ]
