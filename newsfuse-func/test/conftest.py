import pathlib

import pytest


@pytest.fixture
def test_model_path():
    return pathlib.Path(__file__).parent / "mock_data" / "test_model"
