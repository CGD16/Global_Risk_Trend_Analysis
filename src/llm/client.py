"""Bounded communication with the local model (Docker Model Runner or Ollama).

Each pipeline role (query, curate, synthesis, visual, newsletter) can use its own
model. Roles without their own LLM_MODEL_<ROLE> variable fall back to LLM_MODEL,
so existing setups keep working unchanged.
"""

import os
from functools import lru_cache

from openai import OpenAI

MODEL = os.getenv("LLM_MODEL_4090", "LLM_MODEL_3060")
BASE_URL = os.getenv("LLM_BASE_URL_ollama", "LLM_BASE_URL_docker")
BACKEND = os.getenv("LLM_BACKEND_ollama", "LLM_BACKEND_docker")

# Docker Model Runner and Ollama switch thinking off differently.
THINKING_OFF = (
    {"reasoning_effort": "none"}
    if BACKEND == "ollama"
    else {"chat_template_kwargs": {"enable_thinking": False}}
)

# Role -> model. Unset LLM_MODEL_<ROLE> falls back to LLM_MODEL.
ROLE_MODELS = {
    "query": os.getenv("LLM_MODEL_QUERY", MODEL),
    "curate": os.getenv("LLM_MODEL_CURATE", MODEL),
    "synthesis": os.getenv("LLM_MODEL_SYNTHESIS", MODEL),
    "visual": os.getenv("LLM_MODEL_VISUAL", MODEL),
    "newsletter": os.getenv("LLM_MODEL_NEWSLETTER", MODEL),
}

# Per-role request timeout in seconds. Larger models and long inputs need more.
ROLE_TIMEOUTS = {
    "query": 120.0,
    "curate": 120.0,
    "synthesis": 600.0,
    "visual": 180.0,
    "newsletter": 300.0,
}


class InvalidModelOutput(ValueError):
    """The model did not return a complete, usable response."""


def thinking_params(thinking: bool) -> dict:
    """Backend-specific request options for switching thinking on or off."""
    if not thinking:
        return THINKING_OFF
    if BACKEND == "ollama":
        return {}  # Ollama thinks by default when reasoning_effort is not "none"
    return {"chat_template_kwargs": {"enable_thinking": True}}


@lru_cache
def get_client() -> OpenAI:
    return OpenAI(
        base_url=BASE_URL,
        api_key="not-needed",
        timeout=120.0,
        max_retries=0,
    )


def complete(
    system: str,
    prompt: str,
    max_tokens: int = 512,
    *,
    role: str = "query",
    thinking: bool = False,
) -> tuple[str, int | None]:
    if role not in ROLE_MODELS:
        raise ValueError(f"Unknown role {role!r}; expected one of {sorted(ROLE_MODELS)}")

    response = get_client().chat.completions.create(
        model=ROLE_MODELS[role],
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        max_tokens=max_tokens,
        timeout=ROLE_TIMEOUTS[role],
        extra_body=thinking_params(thinking),
    )
    if not response.choices:
        raise InvalidModelOutput("Missing response choices")
    choice = response.choices[0]
    if choice.finish_reason != "stop" or not choice.message.content:
        raise InvalidModelOutput("Incomplete or empty model response")
    return (
        choice.message.content,
        response.usage.total_tokens if response.usage else None,
    )