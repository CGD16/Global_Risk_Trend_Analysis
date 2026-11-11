"""Plan research and execute a bounded sequence of configured searches."""

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

from pydantic import ValidationError

from src.llm.client import InvalidModelOutput, complete
from src.schemas.research import (
    QueryPlan,
    ResearchQueries,
    ResearchRequest,
    ResearchResults,
    SearchRequest,
    SearchResult,
)
from src.tools.search import SearchTool

PROMPT_PATH = Path(__file__).resolve().parents[2] / "prompts" / "research_queries.txt"

MAX_SEARCH_CALLS = 3


def research(request: ResearchRequest, tool: SearchTool) -> ResearchResults:
    """Use one model call and at most three tool calls; propagate tool failures."""
    plan = generate_queries(request)
    results: list[SearchResult] = []
    seen: set[str] = set()
    for query in plan.queries[:MAX_SEARCH_CALLS]:
        search_request = SearchRequest(
            query=query, start_date=plan.start_date, end_date=plan.end_date
        )
        for item in tool.search(search_request)[: search_request.max_results]:
            result = SearchResult.model_validate(item)
            url = str(result.url)
            if url not in seen:
                seen.add(url)
                results.append(result)
    return ResearchResults(**plan.model_dump(), results=results)


def generate_queries(request: ResearchRequest) -> ResearchQueries:
    end_date = datetime.now(UTC).date()
    start_date = end_date - timedelta(days=request.days)
    content, _ = complete(
        PROMPT_PATH.read_text(encoding="utf-8").strip(),
        json.dumps({"topic": request.topic}),
    )
    try:
        plan = QueryPlan.model_validate_json(content)
    except ValidationError as exc:
        raise InvalidModelOutput("Invalid research query JSON") from exc
    return ResearchQueries(
        **request.model_dump(),
        queries=plan.queries,
        start_date=start_date,
        end_date=end_date,
    )
