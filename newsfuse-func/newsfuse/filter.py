def get_opinionated_indices(
    predictions: list[tuple[str, float]], threshold: float
) -> list[int]:
    return [
        i for i, (_, probability) in enumerate(predictions) if probability > threshold
    ]
