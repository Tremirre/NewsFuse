import tensorflow as tf
import tensorflow_text as tf_text

from pathlib import Path
from typing import Any

from .exceptions import FailedToLoadModelException


def load_and_compile_from_path(
    path: Path | str, compile_config: dict[str, Any]
) -> tf.keras.Model:
    try:
        model: tf.keras.Model = tf.keras.models.load_model(path)
    except OSError:
        raise FailedToLoadModelException("model at " + str(path) + " does not exist")
    except tf.errors.NotFoundError:
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
