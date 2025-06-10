import os
from functools import lru_cache

import google.generativeai as genai

DEFAULT_MODEL = os.environ.get("GEMINI_MODEL", "gemini-pro")

@lru_cache()
def _client(model_name: str = DEFAULT_MODEL) -> genai.GenerativeModel:
    """Return a configured GenerativeModel instance."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(model_name)


def generate(prompt: str, *, model_name: str = DEFAULT_MODEL, **kwargs) -> str:
    """Generate a text completion for the given prompt."""
    model = _client(model_name)
    response = model.generate_content(prompt, **kwargs)
    if hasattr(response, "text"):
        return response.text
    if getattr(response, "candidates", None):
        return response.candidates[0].text
    return str(response)
