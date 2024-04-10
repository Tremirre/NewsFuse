from .base import OpinionRemover

AVAILABLE_APIS = ["google", "openai"]


def resolve_opinion_remover(api: str, task: str, model: str) -> OpinionRemover:
    """
    Resolves the appropriate opinion remover class based on the API key.

    :param api: API to be used for the opinion remover
    :param task: task description to be sent to the API
    :param model: selected model for generating deopinionized sentences
    :return: OpinionRemover class
    """
    if api not in AVAILABLE_APIS:
        raise ValueError(f"API {api} is not available.")
    if api == "google":
        from .google import GoogleOpinionRemover

        return GoogleOpinionRemover(task, model)
    if api == "openai":
        from .openai import OpenAIOpinionRemover

        return OpenAIOpinionRemover(task, model)
    raise ValueError(f"API {api} is not available.")
