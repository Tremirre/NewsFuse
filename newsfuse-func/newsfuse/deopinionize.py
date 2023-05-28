import logging

import openai


def merge_sentences(sentences: list[str]) -> str:
    return "\n".join(sentences)


class OpinionRemover:
    def __init__(self, translation_key: str, model: str = "gpt-3.5-turbo") -> None:
        self.model = model
        openai.api_key = translation_key

    def remove_opinions(self, sentences: list[str]) -> list[str]:
        corpus = merge_sentences(sentences)
        try:
            response = self.send_request(corpus)
        except openai.OpenAIError as e:
            logging.error("Failed to send request to OpenAI: " + str(e))
            return []
        return [message["text"] for message in response["choices"]]

    def send_request(self, content: str) -> dict:
        return openai.ChatCompletion.create(  # type: ignore
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert in objective, unopinionated writing. Rewrite each of the following sentences to remove any opinions.",
                },
                {"role": "user", "content": content},
            ],
        )
