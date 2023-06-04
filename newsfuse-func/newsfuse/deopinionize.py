import logging

import openai


def merge_sentences(sentences: list[str]) -> str:
    return "\n".join(sentences)


class OpinionRemover:
    def __init__(
        self,
        translation_key: str,
        task: str,
        model: str = "gpt-3.5-turbo",
    ) -> None:
        self.model = model
        self.task = task
        openai.api_key = translation_key

    def remove_opinions(self, sentences: list[str]) -> dict | None:
        if not sentences:
            return []
        corpus = merge_sentences(sentences)
        try:
            return self.send_request(corpus)
        except openai.OpenAIError as e:
            logging.error("Failed to send request to OpenAI: " + str(e))
            return []

    def send_request(self, content: str) -> dict:
        return openai.ChatCompletion.create(  # type: ignore
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": self.task,
                },
                {"role": "user", "content": content},
            ],
        )
