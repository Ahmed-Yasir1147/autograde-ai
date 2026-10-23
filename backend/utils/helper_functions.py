"""Collection of reuseable helper functions for the backend."""

import copy
from core.config import GEMINI_STANDARD_MODEL_CODE, GEMINI_FALLBACK_MODEL_CODE, logger
from google.genai.errors import APIError
import time
from core.exceptions import ModelLimitReachedError, ModelAPIBaseError

def inline_schema(model, property_name="subquestions", depth=4):
        """Generates an inline JSON schema for a given Pydantic model, resolving nested references up to a specified depth."""
        schema = model.model_json_schema()
        defs = schema.pop("$defs", {})
        def resolve(node, d):
            if isinstance(node, dict):
                if "$ref" in node:
                    target = copy.deepcopy(defs[node["$ref"].split("/")[-1]])
                    if d <= 1:  # last level: no further nesting
                        target.get("properties", {}).pop(property_name, None)
                    return resolve(target, d - 1)
                return {k: resolve(v, d) for k, v in node.items()}
            if isinstance(node, list):
                return [resolve(i, d) for i in node]
            return node

        return resolve(schema, depth)

def retry_gemini_requests(function, filename="", max_retries=3):
    """Retries a function call with exponential backoff in case of exceptions."""
    model_code = GEMINI_STANDARD_MODEL_CODE
    while True:
        try_count = 0
        try:
            return function(model_code=model_code)
        except APIError as e:
            logger.warning(f"Rate limit reached. Retrying in {try_count * 2} seconds...")
            time.sleep(try_count * 2) 
            model_code = GEMINI_FALLBACK_MODEL_CODE 
            try_count += 1
            # Max retry: 3
            if try_count > 3:
                logger.error(f"Exceeded maximum retry attempts due to rate limit for {filename} {function.__name__}.")
                raise ModelLimitReachedError(model_name="Gemini")# Re-raise other non-rate-limit API errors
        except Exception as e:
            logger.error(f"An error occurred while executing the function {filename} {function.__name__}: {e}")
            raise ModelAPIBaseError(f"An error occurred while executing the function {filename} {function.__name__}: {e}")

def singleton(cls):
    """Decorator to create a single instance of a class."""
    instances = {}
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance
