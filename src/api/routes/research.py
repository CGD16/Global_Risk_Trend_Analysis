from fastapi import APIRouter, HTTPException
from openai import OpenAIError

from src.agents.research_agent import generate_queries, research
from src.api.routes.errors import model_error
from src.llm.client import InvalidModelOutput
from src.schemas.research import ResearchQueries, ResearchRequest, ResearchResults
from src.tools.search import SearchToolError
from src.tools.tavily import TavilySearchTool

router = APIRouter()


@router.post("/research/queries", response_model=ResearchQueries)
def research_queries(request: ResearchRequest) -> ResearchQueries:
    try:
        return generate_queries(request)
    except (OpenAIError, InvalidModelOutput) as exc:
        raise model_error(exc) from exc


@router.post("/research/search", response_model=ResearchResults)
def research_search(request: ResearchRequest) -> ResearchResults:
    try:
        tool = TavilySearchTool.from_environment()
    except ValueError:
        raise HTTPException(
            status_code=503, detail="Tavily is not configured"
        ) from None
    try:
        return research(request, tool)
    except (OpenAIError, InvalidModelOutput) as exc:
        raise model_error(exc) from exc
    except SearchToolError:
        raise HTTPException(status_code=502, detail="Web search failed") from None
