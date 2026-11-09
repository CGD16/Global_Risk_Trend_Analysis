from fastapi import APIRouter
from openai import OpenAIError

from src.agents.research_agent import generate_queries
from src.api.routes.errors import model_error
from src.llm.client import InvalidModelOutput
from src.schemas.research import ResearchQueries, ResearchRequest

router = APIRouter()


@router.post("/research/queries", response_model=ResearchQueries)
def research_queries(request: ResearchRequest) -> ResearchQueries:
    try:
        return generate_queries(request)
    except (OpenAIError, InvalidModelOutput) as exc:
        raise model_error(exc) from exc
