import json
import os

import vertexai
import vertexai.generative_models
import vertexai.language_models

from vertexai.generative_models import GenerationResponse

from .base import OpinionRemover


class GoogleOpinionRemover(OpinionRemover):
    """
    Class for removing opinions from a text using Google's API.
    """

    def __init__(self, task: str, model: str = "") -> None:
        """
        :param api_key: api key for the Google Gemini API
        :param task: task description to be sent to the API
        :param model: name of the model to be used, defaults to "gemini-pro"
        """
        model = model or "gemini-pro"
        super().__init__(task, model)
        self.initialized_model = vertexai.generative_models.GenerativeModel(
            model
        )

    def initialize_api(self) -> None:
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
