import pytest

from newsfuse import postprocess


@pytest.mark.parametrize(
    "input, expected",
    [
        (
            {
                "choices": [
                    {"message": {"content": "This is a test"}},
                    {
                        "message": {
                            "content": "This is another test\nLeftover message\nAnd another one"
                        }
                    },
                ]
            },
            [
                "This is a test",
                "This is another test",
                "Leftover message",
                "And another one",
            ],
        ),
        (
            {
                "choices": [
                    {"message": {"content": "\nThis is a test\n"}},
                    {
                        "message": {
                            "content": "This is another test\nLeftover message\nAnd another one\n"
                        }
                    },
                ]
            },
            [
                "This is a test",
                "This is another test",
                "Leftover message",
                "And another one",
            ],
        ),
        (
            {
                "choices": [
                    {"message": {"content": "Lonely message"}},
                ],
                "empty": "This is a test",
                "something else": "This is another test",
            },
            ["Lonely message"],
        ),
        ({"choices": []}, []),
    ],
)
def test_postprocess(input, expected):
    assert postprocess.process_api_response(input) == expected


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
            {1: "This is a test", 2: " ", 3: "Leftover message", 4: "And another one"},
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
def test_format_to_indexed_dict(input, empty_token, opinionated_indices, expected):
    assert (
        postprocess.format_to_indexed_dict(input, empty_token, opinionated_indices)
        == expected
    )
