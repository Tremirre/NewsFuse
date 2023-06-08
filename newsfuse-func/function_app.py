import os
import azure.functions as func
import json
import logging
import pathlib

import numpy as np
import yaml
import dotenv

from newsfuse import preprocess, postprocess
from newsfuse.model import load_and_compile_from_path
from newsfuse.exceptions import FailedToLoadModelException
from newsfuse.deopinionize import OpinionRemover

dotenv.load_dotenv()

fixed_model_path = (
    pathlib.Path(__file__) / ".." / "models" / "small_bert_model"
).resolve()
MODEL_PATH = os.environ.get("MODEL_PATH", fixed_model_path)
DECISION_THRESHOLD = float(os.environ.get("DECISION_THRESHOLD", 0.5))
LENGTH_THRESHOLD = int(os.environ.get("LENGTH_THRESHOLD", 5))
WORD_COUNT_THRESHOLD = int(os.environ.get("WORD_COUNT_THRESHOLD", 2))
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

with open("config.yaml") as f:
    CONFIG = yaml.safe_load(f)

EMPTY_TOKEN = CONFIG["empty_token"]
TASK = CONFIG["task"].format(empty_token=EMPTY_TOKEN)

predictor = lambda x: np.random.rand(len(x))
try:
    MODEL = load_and_compile_from_path(
        MODEL_PATH,
        {
            "optimizer": "adam",
            "loss": "binary_crossentropy",
            "metrics": ["accuracy"],
        },
    )
    predictor = MODEL.predict
except FailedToLoadModelException as e:
    logging.error("Failed to load model: " + str(e) + ".\n Using random predictor.")

oppinion_remover = OpinionRemover(OPENAI_API_KEY, TASK)
app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


@app.route(route="newsfusebackend")
def newsfusebackend(req: func.HttpRequest) -> func.HttpResponse:
    if req.method != "POST":
        return func.HttpResponse(
            "Only POST requests are allowed", status_code=405  # Method Not Allowed
        )
    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "Invalid request body"}),
            status_code=400,
            mimetype="application/json",
        )
    corpus = req_body.get("corpus", "").strip()
    omit_rewrite = req_body.get("omitRewrite", False)
    if not corpus:
        return func.HttpResponse(
            json.dumps({"error": "Missing corpus in request body."}),
            status_code=400,
            mimetype="application/json",
        )
    invalid, valid, all_sentences = preprocess.preprocess_corpus(
        corpus, LENGTH_THRESHOLD, WORD_COUNT_THRESHOLD
    )

    logging.info(f"Invalid sentences: {len(invalid)}")
    logging.info(f"Valid sentences: {len(valid)}")

    if not valid:
        return func.HttpResponse(
            json.dumps({"error": "No valid sentences found."}),
            status_code=400,
            mimetype="application/json",
        )

    valid_sentences = list(valid.values())
    predictions = predictor(valid_sentences).flatten()
    opinionated = np.where(predictions > DECISION_THRESHOLD)[0]
    opinionated_sentences = [valid_sentences[index] for index in opinionated]

    classification = [0] * len(all_sentences)
    for index, prediction in zip(valid.keys(), predictions):
        classification[index] = prediction.item()

    deopinionated_indexed = {}
    if not omit_rewrite:
        api_response = oppinion_remover.remove_opinions(opinionated_sentences)
        logging.info(f"Used tokens: {api_response['usage']['total_tokens']}")
        if api_response:
            deopinionated_sentences = postprocess.process_api_response(api_response)
            deopinionated_indexed = postprocess.format_to_indexed_dict(
                deopinionated_sentences, EMPTY_TOKEN, opinionated.tolist()
            )
    result = {
        "sentences": list(all_sentences.values()),
        "classification": classification,
        "translations": deopinionated_indexed,
    }
    return func.HttpResponse(
        json.dumps(result),
        mimetype="application/json",
    )
