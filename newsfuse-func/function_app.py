import os
import azure.functions as func
import json
import logging
import pathlib

import numpy as np
import dotenv

from newsfuse import preprocess
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

oppinion_remover = OpinionRemover(OPENAI_API_KEY)
app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


@app.route(route="newsfusebackend")
def newsfusebackend(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")
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
    corpus = req_body.get("corpus")
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

    deopinionated_sentences = oppinion_remover.remove_opinions(opinionated_sentences)
    deopinionated_indexed = {
        index: new_sentence
        for index, new_sentence in zip(valid.keys(), deopinionated_sentences)
    }
    result = {
        "sentences": list(all_sentences.values()),
        "classification": classification,
        "translations": deopinionated_indexed,
    }
    return func.HttpResponse(
        json.dumps(result),
        mimetype="application/json",
    )
