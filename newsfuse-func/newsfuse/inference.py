import nltk
import numpy as np

from typing import Callable


def predict_classes(
    text_corpus: str, inferer_func: Callable[[list[str]], np.ndarray]
) -> list[tuple[str, float]]:
    tokenized_text = nltk.sent_tokenize(text_corpus)
    inferred = inferer_func(tokenized_text)
    return list(zip(tokenized_text, inferred.flatten().tolist()))
