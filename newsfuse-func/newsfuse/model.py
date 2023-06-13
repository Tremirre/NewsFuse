import tensorflow as tf  # type: ignore

# required for loading model
import tensorflow_text as tf_text  # type: ignore

from pathlib import Path
from typing import Any

from .exceptions import FailedToLoadModelException


def load_and_compile_from_path(
    path: Path | str, compile_config: dict[str, Any]
) -> tf.keras.Model:
    try:
        model: tf.keras.Model = tf.keras.models.load_model(path, compile=False)  # type: ignore
    except OSError:
        raise FailedToLoadModelException("model at " + str(path) + " does not exist")
    except tf.errors.NotFoundError:  # type: ignore
        raise FailedToLoadModelException(
            "model at " + str(path) + " is not a valid model"
        )
    except tf.errors.InvalidArgumentError:
        raise FailedToLoadModelException(
            "model at " + str(path) + " is not a valid model"
        )
    except Exception as e:
        raise FailedToLoadModelException(
            "model at " + str(path) + " failed to load with error: " + str(e)
        )
    model.compile(**compile_config)
    return model
