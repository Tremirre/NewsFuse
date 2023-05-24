import azure.functions as func
import json
import logging
import pathlib

import numpy as np

from newsfuse.inference import predict_classes
from newsfuse.model import load_and_compile_from_path
from newsfuse.exceptions import FailedToLoadModelException

model_path = (pathlib.Path(__file__) / ".." / "models" / "small_bert_model").resolve()
predictor = lambda x: np.random.rand(len(x))
try:
    MODEL = load_and_compile_from_path(
        model_path,
        {
            "optimizer": "adam",
            "loss": "binary_crossentropy",
            "metrics": ["accuracy"],
        },
    )
    predictor = MODEL.predict
except FailedToLoadModelException as e:
    logging.error("Failed to load model: " + str(e) + ".\n Using random predictor.")


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
            {"error": "Invalid request body"},
            status_code=400,
            mimetype="application/json",
        )
    corpus = req_body.get("corpus")
    if not corpus:
        return func.HttpResponse(
            {"error": "Missing corpus in request body."},
            status_code=400,
            mimetype="application/json",
        )
    pred = predict_classes(corpus, predictor)
    return func.HttpResponse(json.dumps(pred), mimetype="application/json")
