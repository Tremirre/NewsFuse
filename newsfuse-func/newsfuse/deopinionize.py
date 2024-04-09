import abc
import logging
import typing
import os
import json

import openai
from openai.types.chat.chat_completion import ChatCompletion

import vertexai
import vertexai.generative_models
import vertexai.language_models
from vertexai.generative_models import GenerationResponse


def merge_sentences(sentences: list[str]) -> str:
    """
    Merges a list of sentences into a single string.
    Uses a newline character as a separator.

    :param sentences: List of sentences to merge
    :return: Merged sentences
    """
    return "\n".join(sentences)


class OpinionRemover(abc.ABC):
    """
    Abstract class for removing opinions from a text.
    """

    def __init__(self, api_key: str, task: str, model: str) -> None:
        """
        :param api_key: API key to be used for the opinion remover
        :param task: task description to be sent to the API
        :param model: selected model for generating deopinionized sentences
        """
        self.task = task
        self.model = model
        self.use_api_key(api_key)

    @abc.abstractmethod
    def use_api_key(self, api_key: str) -> None:
        """
        Sets the API key for the opinion remover.

        :param api_key: API key to be used
        """
        pass

    def remove_opinions(self, sentences: list[str]) -> list[str]:
        """
        Removes opinions from a list of sentences.
        If the request fails, returns an empty list.

        :param sentences: List of sentences to remove opinions from
        :return: Deopinionized sentences
        """
        if not sentences:
            return []
        corpus = merge_sentences(sentences)
        try:
            response = self.send_request(corpus)
            return self.process_api_response(response)
        except Exception as e:
            logging.error("Failed to send request to API consumer: " + str(e))
            return []

    @abc.abstractmethod
    def send_request(self, content: str) -> typing.Any:
        """
        Sends a deopnionize request to the API.

        :param content: text to be deopinionized sentence by sentence
        :return: raw response from the API
        """
        pass

    @abc.abstractmethod
    def process_api_response(self, response: typing.Any) -> list[str]:
        """
        Processes the raw response from the API into a list of sentences.

        :param response: raw response from the API
        :return: list of sentences
        """
        pass


class GoogleOpinionRemover(OpinionRemover):
    """
    Class for removing opinions from a text using Google's API.
    """

    def __init__(
        self, api_key: str, task: str, model: str = "gemini-pro"
    ) -> None:
        """
        :param api_key: api key for the Google Gemini API
        :param task: task description to be sent to the API
        :param model: name of the model to be used, defaults to "gemini-pro"
        """
        super().__init__(api_key, task, model)
        self.initialized_model = vertexai.generative_models.GenerativeModel(
            model
        )

    def use_api_key(self, _: str) -> None:
        """
        Initializes the Google Gemini API with the credentials from the
        GOOGLE_APPLICATION_CREDENTIALS environment variable.

        :param _: unused API key
        """
        app_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if not app_credentials:
            raise ValueError("GOOGLE_APPLICATION_CREDENTIALS is not set.")
        with open(app_credentials) as f:
            credentials = json.load(f)

        vertexai.init(
            project=credentials["project_id"],
            location=os.environ["GOOGLE_LOCATION"],
        )

    def send_request(self, content: str) -> GenerationResponse:
        """
        Sends a deopnionize request to Google's API.

        :param content: text to be deopinionized sentence by sentence
        :return: raw response from Google's API
        """
        src_content = self.task + "\n\n" + content
        response = self.initialized_model.generate_content(src_content)
        return response  # type: ignore

    def process_api_response(self, response: GenerationResponse) -> list[str]:
        """
        Processes the raw response from the API into a list of sentences.

        :param response: raw response from the API
        :return: list of sentences
        """
        return [sentence for sentence in response.text.split("\n")]


class OpenAIOpinionRemover(OpinionRemover):
    """
    Class for removing opinions from a text using OpenAI's API.
    """

    def __init__(
        self,
        translation_key: str,
        task: str,
        model: str = "gpt-3.5-turbo",
    ) -> None:
        """
        :param translation_key: key for OpenAI API
        :param task: detailed description of the task to be sent to OpenAI API
        :param model: selected model for generating deopinionized sentences,
            defaults to "gpt-3.5-turbo"
        """
        super().__init__(translation_key, task, model)

    def use_api_key(self, api_key: str) -> None:
        """
        Sets the API key for the opinion remover.

        :param api_key: API key to be used
        """
        if not openai.api_key:
            raise ValueError("OpenAI API key is not set.")
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
