import tensorflow as tf  # type: ignore

# required for loading model
import tensorflow_text as tf_text  # type: ignore

import tensorflow_hub as tf_hub  # type: ignore

from pathlib import Path
from typing import Any

from .exceptions import FailedToLoadModelException

assert tf_text  # silence unused import warning


def load_and_compile_from_path(
    path: Path | str, compile_config: dict[str, Any]
) -> tf.keras.Model:
    """
    Loads a model from a path and compiles it with the given config.

    :param path: path to the model
    :param compile_config: config to compile the model with
    :raises FailedToLoadModelException: if the model fails to load
    :return: the loaded and compiled model
    """
    try:
        model: tf.keras.Model = tf.keras.models.load_model(
            path,
            custom_objects={"KerasLayer": tf_hub.KerasLayer},
            compile=False,
        )  # type: ignore
    except OSError:
        raise FailedToLoadModelException(
            "model at " + str(path) + " does not exist"
        )
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
