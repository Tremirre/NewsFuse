from itertools import chain

from .types import IndexedSentences


def process_api_response(response: dict) -> list[str]:
    contents = [
        choice["message"]["content"].split("\n") for choice in response["choices"]
    ]
    contents = [
        [sentence for sentence in choice if sentence.strip()] for choice in contents
    ]
    return list(chain.from_iterable(contents))


def format_to_indexed_dict(
    processed_api_response: list[str], empty_token: str, opinionated_indices: list[int]
) -> IndexedSentences:
    processed = [
        sentence if sentence != empty_token else " "
        for sentence in map(str.strip, processed_api_response)
    ]
    return {
        index: new_sentence
        for index, new_sentence in zip(opinionated_indices, processed)
    }
