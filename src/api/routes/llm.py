from fastapi import APIRouter
from openai import OpenAIError

from src.api.routes.errors import model_error
from src.llm.client import MODEL, InvalidModelOutput, complete

router = APIRouter()


@router.get("/llm/test")
def test_llm() -> dict[str, str | int | None]:
    try:
        content, tokens = complete(
            "You are a research assistant specializing in global risks.",
            "What are geopolitical risks? Answer in one sentence.",
            max_tokens=256,
        )
        return {"model": MODEL, "response": content, "tokens_used": tokens}
    except (OpenAIError, InvalidModelOutput) as exc:
        raise model_error(exc) from exc
