import pytest

import tensorflow as tf
import numpy as np

from unittest.mock import Mock

from newsfuse.model import load_and_compile_from_path
from newsfuse.exceptions import FailedToLoadModelException


def test_load_and_compile_compiles_model_on_successful_load(monkeypatch):
    mock_model = Mock()
    copile_spec = {"optimizer": "adam", "loss": "binary_crossentropy"}
    monkeypatch.setattr(
        "tensorflow.keras.models.load_model",
        Mock(return_value=mock_model),
    )
    model = load_and_compile_from_path("path", copile_spec)
    mock_model.compile.assert_called_once_with(**copile_spec)

    assert model is not None


class CustomException(Exception):
    def __init__(self):
        super().__init__("CustomException")


@pytest.mark.parametrize(
    "exception, expected_message",
    [
        (OSError, "Failed to load model: model at path does not exist"),
        (
            CustomException,
            "Failed to load model: model at path failed to load with error: CustomException",
        ),
    ],
)
def test_load_and_compile_raises_exception_on_error(
    exception, expected_message, monkeypatch
):
    monkeypatch.setattr(
        "tensorflow.keras.models.load_model",
        Mock(side_effect=exception),
    )
    with pytest.raises(FailedToLoadModelException) as e:
        load_and_compile_from_path("path", {})
    assert str(e.value).startswith(expected_message)
