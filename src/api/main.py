import logging

from fastapi import FastAPI, HTTPException
from openai import OpenAIError

from src.agents.research_agent import generate_queries
from src.llm.client import MODEL, InvalidModelOutput, complete
from src.schemas.research import ResearchQueries, ResearchRequest

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Global Risk Trend Analysis API",
    description="Agentic workflow for global risk research",
    version="0.1.0",
)


def model_error(exc: Exception) -> HTTPException:
    # Do not log prompts, response bodies, URLs, or exception messages.
    logger.warning("Local LLM request failed (%s)", type(exc).__name__)
    return HTTPException(
        status_code=502, detail="Local LLM failed to return a valid response"
    )


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/llm/test")
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


@app.post("/research/queries", response_model=ResearchQueries)
def research_queries(request: ResearchRequest) -> ResearchQueries:
    try:
        return generate_queries(request)
    except (OpenAIError, InvalidModelOutput) as exc:
        raise model_error(exc) from exc
