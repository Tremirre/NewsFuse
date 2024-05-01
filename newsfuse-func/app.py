import os
import re
import logging

import numpy as np
import yaml
import dotenv
import fastapi
import fastapi.middleware.cors

from newsfuse import preprocess, postprocess, deopinionize
from newsfuse.model import load_and_compile_from_path
from newsfuse.exceptions import FailedToLoadModelException

dotenv.load_dotenv()

logging.basicConfig(level=logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
logging.getLogger().addHandler(handler)


MODEL_PATH = os.environ.get("MODEL_PATH", "")
DECISION_THRESHOLD = float(os.environ.get("DECISION_THRESHOLD", 0.5))
LENGTH_THRESHOLD = int(os.environ.get("LENGTH_THRESHOLD", 5))
WORD_COUNT_THRESHOLD = int(os.environ.get("WORD_COUNT_THRESHOLD", 2))
API_USED = os.environ["API_USED"]
API_MODEL = os.environ.get("API_MODEL", "")

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

opinion_remover = deopinionize.resolve_opinion_remover(
    API_USED,
    TASK,
    API_MODEL,
)

logging.info(f"Using {API_USED} API for deopinionization.")
app = fastapi.FastAPI()
origins = os.environ.get("CORS_ORIGINS", "")
if not origins:
    logging.warning(
        "CORS_ORIGINS environment variable not set, allowing all origins."
    )
    origins = ["*"]
else:
    origins = origins.split(",")
    logging.info(f"Allowed origins: {origins}")

app.add_middleware(
    fastapi.middleware.cors.CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/")
async def newsfusebackend(
    request: fastapi.Request, response: fastapi.Response
) -> dict:
    try:
        req_body = await request.json()
    except ValueError:
        response.status_code = 400
        return {"error": "Invalid request body"}
    corpus = req_body.get("corpus", "")
    corpus = preprocess.clean_corpus(corpus)
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
        deopinionated_sentences = opinion_remover.remove_opinions(
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
