from typing import Union

from fastapi.encoders import jsonable_encoder

from inference.core.devices.utils import GLOBAL_INFERENCE_SERVER_ID
from inference.core.entities.requests.inference import InferenceRequest
from inference.core.entities.responses.inference import InferenceResponse
from inference.core.env import TINY_CACHE
from inference.core.logger import logger
from inference.core.version import __version__


def to_cachable_inference_item(
    infer_request: InferenceRequest,
    infer_response: Union[InferenceResponse, list[InferenceResponse]],
) -> dict:
    if not TINY_CACHE:
        return {
            "inference_id": infer_request.id,
            "inference_server_version": __version__,
            "inference_server_id": GLOBAL_INFERENCE_SERVER_ID,
            "request": jsonable_encoder(infer_request),
            "response": jsonable_encoder(infer_response),
        }

    included_request_fields = {"api_key", "confidence", "model_id", "model_type"}
    request = infer_request.dict(include=included_request_fields)
    response = build_condensed_response(infer_response)

    return {
        "inference_id": infer_request.id,
        "inference_server_version": __version__,
        "inference_server_id": GLOBAL_INFERENCE_SERVER_ID,
        "request": jsonable_encoder(request),
        "response": jsonable_encoder(response),
    }


def build_condensed_response(responses):
    if not isinstance(responses, list):
        responses = [responses]

    formatted_responses = []
    for response in responses:
        if not getattr(response, "predictions", None):
            continue
        try:
            predictions = [
                {"confidence": pred.confidence, "class": pred.class_name}
                for pred in response.predictions
            ]
            formatted_responses.append(
                {
                    "predictions": predictions,
                    "time": response.time,
                }
            )
        except Exception as e:
            logger.warning(f"Error formatting response, skipping caching: {e}")

    return formatted_responses
