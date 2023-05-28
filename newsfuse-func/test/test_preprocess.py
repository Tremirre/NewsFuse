import pytest

from newsfuse import preprocess


@pytest.mark.parametrize(
    "text, expected",
    [
        ("This is a sentence.", ["This is a sentence."]),
        (
            "This is a sentence. This is another sentence.",
            ["This is a sentence.", "This is another sentence."],
        ),
        (
            "This is a sentence. This is another sentence. This is a third sentence.",
            [
                "This is a sentence.",
                "This is another sentence.",
                "This is a third sentence.",
            ],
        ),
        (
            "Hello to Washington, D.C.! We are thrilled to meet Mr. Cooper in the capitol.",
            [
                "Hello to Washington, D.C.!",
                "We are thrilled to meet Mr. Cooper in the capitol.",
            ],
        ),
    ],
)
def test_split_to_sentences_splits_correctly(text, expected):
    assert preprocess.split_to_sentences(text) == expected


@pytest.mark.parametrize(
    "indexed_sentences, total_length, expected",
    [
        (
            {
                0: "This is a sentence.",
                1: "This is another sentence.",
                2: "This is a third sentence.",
            },
            0,
            (
                {},
                {
                    0: "This is a sentence.",
                    1: "This is another sentence.",
                    2: "This is a third sentence.",
                },
            ),
        ),
        (
            {
                0: "This is a sentence.",
                1: "This is another sentence.",
                2: "This is a third sentence.",
            },
            18,
            (
                {},
                {
                    0: "This is a sentence.",
                    1: "This is another sentence.",
                    2: "This is a third sentence.",
                },
            ),
        ),
        (
            {
                0: "This is a sentence.",
                1: "This is another sentence.",
                2: "This is a third sentence.",
            },
            19,
            (
                {
                    0: "This is a sentence.",
                },
                {
                    1: "This is another sentence.",
                    2: "This is a third sentence.",
                },
            ),
        ),
        (
            {
                0: "This is a sentence.",
                1: "This is another sentence.",
                2: "This is a third sentence.",
            },
            30,
            (
                {
                    0: "This is a sentence.",
                    1: "This is another sentence.",
                    2: "This is a third sentence.",
                },
                {},
            ),
        ),
        (
            {
                0: "This is a sentence.",
                1: "",
                2: " ",
            },
            2,
            (
                {
                    1: "",
                    2: " ",
                },
                {
                    0: "This is a sentence.",
                },
            ),
        ),
    ],
)
def test_separate_by_total_length(indexed_sentences, total_length, expected):
    assert (
        preprocess.separate_by_total_length(indexed_sentences, total_length) == expected
    )


@pytest.mark.parametrize(
    "indexed_sentences, word_count, expected",
    [
        (
            {
                0: "This is a sentence.",
                1: "This is another sentence.",
                2: "This is a third sentence.",
            },
            0,
            (
                {},
                {
                    0: "This is a sentence.",
                    1: "This is another sentence.",
                    2: "This is a third sentence.",
                },
            ),
        ),
        (
            {
                0: "This is a sentence.",
                1: "This is another sentence.",
                2: "This is a third sentence.",
            },
            3,
            (
                {},
                {
                    0: "This is a sentence.",
                    1: "This is another sentence.",
                    2: "This is a third sentence.",
                },
            ),
        ),
        (
            {
                0: "This is a sentence.",
                1: "This is another sentence.",
                2: "This is a third sentence.",
            },
            4,
            (
                {
                    0: "This is a sentence.",
                    1: "This is another sentence.",
                },
                {
                    2: "This is a third sentence.",
                },
            ),
        ),
        (
            {
                0: "This is a sentence.",
                1: "This is another sentence.",
                2: "This is a third sentence.",
            },
            9,
            (
                {
                    0: "This is a sentence.",
                    1: "This is another sentence.",
                    2: "This is a third sentence.",
                },
                {},
            ),
        ),
        (
            {
                0: "This is a sentence.",
                1: "",
                2: " ",
            },
            1,
            (
                {
                    1: "",
                    2: " ",
                },
                {
                    0: "This is a sentence.",
                },
            ),
        ),
    ],
)
def test_separate_by_word_count(indexed_sentences, word_count, expected):
    assert preprocess.separate_by_word_count(indexed_sentences, word_count) == expected


@pytest.mark.parametrize(
    "corpus, invalid, valid, length_threshold, word_count_threshold",
    [
        (
            "This is a sentence.",
            {},
            {
                0: "This is a sentence.",
            },
            0,
            0,
        ),
        (
            "This is a sentence.",
            {
                0: "This is a sentence.",
            },
            {},
            0,
            4,
        ),
        (
            "This is a sentence.",
            {
                0: "This is a sentence.",
            },
            {},
            20,
            0,
        ),
        (
            "This is a sentence.",
            {
                0: "This is a sentence.",
            },
            {},
            20,
            4,
        ),
        (
            "This is a sentence. This is another sentence. And finally, this is a third sentence. I am very lols mate.",
            {
                0: "This is a sentence.",
                1: "This is another sentence.",
                3: "I am very lols mate.",
            },
            {
                2: "And finally, this is a third sentence.",
            },
            20,
            4,
        ),
    ],
)
def test_preprocess_corpus(
    corpus, invalid, valid, length_threshold, word_count_threshold
):
    assert preprocess.preprocess_corpus(
        corpus, length_threshold, word_count_threshold
    ) == (invalid, valid, invalid | valid)
