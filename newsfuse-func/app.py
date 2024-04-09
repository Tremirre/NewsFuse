import os
import logging
import pathlib

import numpy as np
import yaml
import dotenv
import fastapi

from newsfuse import preprocess, postprocess, deopinionize
from newsfuse.model import load_and_compile_from_path
from newsfuse.exceptions import FailedToLoadModelException

dotenv.load_dotenv()

logging.basicConfig(level=logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
logging.getLogger().addHandler(handler)

fixed_model_path = (
    pathlib.Path(__file__) / ".." / "models" / "small_bert_model"
).resolve()
MODEL_PATH = os.environ.get("MODEL_PATH", fixed_model_path)
DECISION_THRESHOLD = float(os.environ.get("DECISION_THRESHOLD", 0.5))
LENGTH_THRESHOLD = int(os.environ.get("LENGTH_THRESHOLD", 5))
WORD_COUNT_THRESHOLD = int(os.environ.get("WORD_COUNT_THRESHOLD", 2))
API_USED = os.environ["API_USED"]
API_KEY = os.environ.get("API_KEY", "")

assert API_USED in ["openai", "google"], "API_USED must be 'openai' or 'google'"

with open("config.yaml") as f:
    CONFIG = yaml.safe_load(f)

EMPTY_TOKEN = CONFIG["empty_token"]
TASK = CONFIG["task"].format(empty_token=EMPTY_TOKEN)


def predictor(x):
    return np.random.rand(len(x))


try:
    MODEL = load_and_compile_from_path(
        MODEL_PATH,
        {
            "optimizer": "adam",
            "loss": "binary_crossentropy",
            "metrics": ["accuracy"],
        },
    )
    predictor = MODEL.predict  # noqa: F811
    logging.info(f"Using model from {MODEL_PATH} for classification.")
except FailedToLoadModelException as e:
    logging.error(
        "Failed to load model: " + str(e) + ".\n Using random predictor."
    )

if API_USED == "openai":
    oppinion_remover = deopinionize.OpenAIOpinionRemover(API_KEY, TASK)
else:
    oppinion_remover = deopinionize.GoogleOpinionRemover(API_KEY, TASK)
logging.info(f"Using {API_USED} API for deopinionization.")
app = fastapi.FastAPI()


@app.post("/")
async def newsfusebackend(
    request: fastapi.Request, response: fastapi.Response
) -> dict:
    try:
        req_body = await request.json()
    except ValueError:
        response.status_code = 400
        return {"error": "Invalid request body"}
    corpus = req_body.get("corpus", "").strip()
    omit_rewrite = req_body.get("omitRewrite", False)
    if not corpus:
        response.status_code = 400
        return {"error": "Missing corpus in request body."}
    invalid, valid, all_sentences = preprocess.preprocess_corpus(
        corpus, LENGTH_THRESHOLD, WORD_COUNT_THRESHOLD
    )

    logging.info(f"Invalid sentences: {len(invalid)}")
    logging.info(f"Valid sentences: {len(valid)}")

    if not valid:
        response.status_code = 400
        return {"error": "No valid sentences in the corpus."}

    valid_sentences = list(valid.values())
    predictions = predictor(valid_sentences).flatten()
    opinionated = np.where(predictions > DECISION_THRESHOLD)[0]
    opinionated_sentences = [valid_sentences[index] for index in opinionated]

    classification = [0] * len(all_sentences)
    for index, prediction in zip(valid.keys(), predictions):
        classification[index] = prediction.item()

    deopinionated_indexed = {}
    if not omit_rewrite:
        deopinionated_sentences = oppinion_remover.remove_opinions(
            opinionated_sentences
        )
        if deopinionated_sentences:
            deopinionated_indexed = postprocess.format_to_indexed_dict(
                deopinionated_sentences, EMPTY_TOKEN, opinionated.tolist()
            )
    result = {
        "sentences": list(all_sentences.values()),
        "classification": classification,
        "translations": deopinionated_indexed,
    }
    return result
