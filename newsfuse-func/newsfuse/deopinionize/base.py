import abc
import logging
import typing


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

    def __init__(self, task: str, model: str) -> None:
        """
        :param api_key: API key to be used for the opinion remover
        :param task: task description to be sent to the API
        :param model: selected model for generating deopinionized sentences
        """
        self.task = task
        self.model = model
        self.initialize_api()

    @abc.abstractmethod
    def initialize_api(self) -> None:
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
