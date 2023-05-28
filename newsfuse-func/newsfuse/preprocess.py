import nltk

from typing import Callable

from newsfuse.types import IndexedSentences


def split_to_sentences(text: str) -> list[str]:
    return nltk.sent_tokenize(text)


def separate_by_condition(
    sentences: IndexedSentences, invalidating_condition: Callable[[str], bool]
) -> tuple[IndexedSentences, IndexedSentences]:
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
    return separate_by_condition(sentences, lambda sentence: len(sentence) > length)


def separate_by_word_count(
    sentences: IndexedSentences, word_count: int
) -> tuple[IndexedSentences, IndexedSentences]:
    return separate_by_condition(
        sentences, lambda sentence: len(sentence.split()) > word_count
    )


def preprocess_corpus(
    corpus: str,
    length_threshold: int = 0,
    word_count_threshold: int = 0,
) -> tuple[IndexedSentences, IndexedSentences, IndexedSentences]:
    all_sentences = dict(enumerate(split_to_sentences(corpus)))
    invalid, valid = separate_by_total_length(all_sentences, length_threshold)
    too_few_words, valid = separate_by_word_count(valid, word_count_threshold)
    invalid.update(too_few_words)
    return invalid, valid, all_sentences
