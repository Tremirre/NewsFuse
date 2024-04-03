import pytest

from newsfuse import postprocess


@pytest.mark.parametrize(
    "input, empty_token, opinionated_indices, expected",
    [
        (
            [
                "This is another test",
                "Leftover message",
            ],
            "<empty>",
            [2, 3],
            {2: "This is another test", 3: "Leftover message"},
        ),
        (
            [
                "This is a test",
                "<empty>",
                "Leftover message",
                "And another one",
            ],
            "<empty>",
            [1, 2, 3, 4],
            {
                1: "This is a test",
                2: " ",
                3: "Leftover message",
                4: "And another one",
            },
        ),
        (
            [
                "This is a test",
            ],
            "<empty>",
            [1],
            {1: "This is a test"},
        ),
        (
            [
                "  <empty>  ",
            ],
            "<empty>",
            [1],
            {1: " "},
        ),
    ],
)
def test_format_to_indexed_dict(
    input, empty_token, opinionated_indices, expected
):
    assert (
        postprocess.format_to_indexed_dict(
            input, empty_token, opinionated_indices
        )
        == expected
    )
