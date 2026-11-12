"""Bounded communication with the local Docker Model Runner."""

from functools import lru_cache

from openai import OpenAI

MODEL = "ai/qwen3.5:9B-UD-Q4_K_XL"


class InvalidModelOutput(ValueError):
    """The model did not return a complete, usable response."""


@lru_cache
def get_client() -> OpenAI:
    return OpenAI(
        base_url="http://localhost:12434/engines/v1",
        api_key="not-needed",
        timeout=120.0,
        max_retries=0,
    )


def complete(system: str, prompt: str, max_tokens: int = 512) -> tuple[str, int | None]:
    response = get_client().chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        max_tokens=max_tokens,
        extra_body={"chat_template_kwargs": {"enable_thinking": False}},
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
