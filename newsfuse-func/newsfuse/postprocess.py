from .types import IndexedSentences


def format_to_indexed_dict(
    processed_api_response: list[str],
    empty_token: str,
    opinionated_indices: list[int],
) -> IndexedSentences:
    """
    Formats the processed response from OpenAI API into a
    dictionary of sentences with their original indices.

    :param processed_api_response: list of sentences from OpenAI API
    :param empty_token: token to represent an empty sentence
    :param opinionated_indices: indices of opinionated sentences
    :return: dictionary of sentences with their original indices
    """
    processed = [
        sentence if sentence != empty_token else " "
        for sentence in map(str.strip, processed_api_response)
    ]
    return {
        index: new_sentence
        for index, new_sentence in zip(opinionated_indices, processed)
    }
