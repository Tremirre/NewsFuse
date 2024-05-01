import re
import nltk  # type: ignore

from typing import Callable

from newsfuse.types import IndexedSentences


quote_pattern = re.compile(r"\"(.*?)\"")
styled_quote_pattern = re.compile(r"“(.*?)”")


def clean_corpus(corpus: str) -> str:
    """
    Cleans a corpus by removing quotes and stripping leading and trailing
    whitespace.

    :param corpus: corpus to be prepared
    :return: prepared corpus
    """
    corpus = quote_pattern.sub("", corpus)
    corpus = styled_quote_pattern.sub("", corpus)
    corpus = corpus.strip()
    return corpus


def split_to_sentences(text: str) -> list[str]:
    """
    Splits a text into sentences using NLTK.

    :param text: text corpus to be split
    :return: list of sentences
    """
    return nltk.sent_tokenize(text)


def separate_by_condition(
    sentences: IndexedSentences, invalidating_condition: Callable[[str], bool]
) -> tuple[IndexedSentences, IndexedSentences]:
    """
    Separates a dictionary of sentences into two dictionaries:
    one with sentences that satisfy the condition and one with sentences that
    do not.

    :param sentences: dictionary of indexed sentences
    :param invalidating_condition: condition to be satisfied
    :return: tuple of dictionaries of sentences that satisfy the condition and
        sentences that do not
    """
    valid_sentences = {
        key: sentences[key]
        for key, sentence in sentences.items()
        if invalidating_condition(sentence)
    }
    non_sentences = {
        key: sentences[key] for key in sentences if key not in valid_sentences
    }
    return non_sentences, valid_sentences


def separate_by_total_length(
    sentences: IndexedSentences, length: int
) -> tuple[IndexedSentences, IndexedSentences]:
    """
    Separates a dictionary of sentences into two dictionaries:
    one with sentences that have a total length greater than the given length
    and one with sentences that do not.

    :param sentences: dictionary of indexed sentences
    :param length: length to be compared against
    :return: tuple of dictionaries of sentences that satisfy the condition and
        sentences that do not
    """
    return separate_by_condition(
        sentences, lambda sentence: len(sentence) > length
    )


def separate_by_word_count(
    sentences: IndexedSentences, word_count: int
) -> tuple[IndexedSentences, IndexedSentences]:
    """
    Separates a dictionary of sentences into two dictionaries:
    one with sentences that have a word count greater than the given word count
    and one with sentences that do not.

    :param sentences: dictionary of indexed sentences
    :param word_count: word count to be compared against
    :return: tuple of dictionaries of sentences that satisfy the condition and
        sentences that do not
    """
    return separate_by_condition(
        sentences, lambda sentence: len(sentence.split()) > word_count
    )


def preprocess_corpus(
    corpus: str,
    length_threshold: int = 0,
    word_count_threshold: int = 0,
) -> tuple[IndexedSentences, IndexedSentences, IndexedSentences]:
    """
    Preprocesses a corpus by splitting it into sentences and separating
    them into invalid, valid, and all sentences based on length and word count.

    :param corpus: corpus to be preprocessed
    :param length_threshold: lower limit for sentence length, defaults to 0
    :param word_count_threshold: lower limit for sentence word count,
        defaults to 0
    :return: tuple of dictionaries of invalid, valid, and all sentences
    """
    all_sentences = dict(enumerate(split_to_sentences(corpus)))
    invalid, valid = separate_by_total_length(all_sentences, length_threshold)
    too_few_words, valid = separate_by_word_count(valid, word_count_threshold)
    invalid.update(too_few_words)
    return invalid, valid, all_sentences
