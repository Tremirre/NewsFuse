import os
import json
import pathlib

import numpy as np

from .inference import predict_classes
from .exceptions import FailedToLoadModelException
from .model import load_and_compile_from_path

# model_path = pathlib.Path(os.environ["MODEL_PATH"])
model_path = (
    pathlib.Path(__file__) / ".." / ".." / "models" / "small_bert_model"
).resolve()
MODEL = load_and_compile_from_path(
    model_path,
    {
        "optimizer": "adam",
        "loss": "binary_crossentropy",
        "metrics": ["accuracy"],
    },
)
