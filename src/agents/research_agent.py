"""Plan research and execute a bounded sequence of configured searches."""

import json
from datetime import UTC, datetime, timedelta
from time import gmtime, strftime
from pathlib import Path

from pydantic import ValidationError, TypeAdapter

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
RUN_DIR = Path(__file__).resolve().parents[2] / "dist" / "runs"
REAL_TIME = strftime("%Y_%m_%d_%a_%H_%M_%S", gmtime())

MAX_SEARCH_CALLS = 3



def generate_queries(request: ResearchRequest) -> ResearchQueries:
    end_date = datetime.now(UTC).date()
    start_date = end_date - timedelta(days=request.days)
    # content, _ = complete(PROMPT_PATH.read_text(encoding="utf-8").strip(), json.dumps({"topic": request.topic}),)
    content, _ = complete(
        PROMPT_PATH.read_text(encoding="utf-8").strip(),
        json.dumps({"topic": request.topic}),
        max_tokens=1024)

    debug_model_path = RUN_DIR / "models" / f"{REAL_TIME}_model_output.txt"
    debug_model_path.parent.mkdir(parents=True, exist_ok=True)
    debug_model_path.write_text(content, encoding="utf-8")

    debug_research_plan_path = RUN_DIR / "research" / f"{REAL_TIME}_research_output.json"
    debug_research_plan_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        plan = QueryPlan.model_validate_json(content)
        plan_json = plan.model_dump_json(indent=2)
        debug_research_plan_path.write_text(plan_json, encoding="utf-8")
        
    except ValidationError as exc:
        error_payload = {
            "content": content,
            "error": str(exc),
            "errors": exc.errors(),
        }
        debug_research_plan_path.write_text(
            json.dumps(error_payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        raise InvalidModelOutput("Invalid research query JSON") from exc

    return ResearchQueries(
        **request.model_dump(),
        queries=plan.queries,
        start_date=start_date,
        end_date=end_date,
    )


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

    debug_query_results_path = RUN_DIR / "models" / f"{REAL_TIME}_query_results.txt"
    debug_query_results_path.parent.mkdir(parents=True, exist_ok=True)
    debug_query_results_path.write_text(
        TypeAdapter(list[SearchResult]).dump_json(results, indent=2).decode("utf-8"),
        encoding="utf-8",
    )
    
    return ResearchResults(**plan.model_dump(), results=results)


