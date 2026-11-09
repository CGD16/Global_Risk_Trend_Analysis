"""Generate queries only; no search tools or retrieved content are executed."""

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

from pydantic import ValidationError

from src.llm.client import InvalidModelOutput, complete
from src.schemas.research import QueryPlan, ResearchQueries, ResearchRequest

PROMPT_PATH = Path(__file__).resolve().parents[2] / "prompts" / "research_queries.txt"


def generate_queries(request: ResearchRequest) -> ResearchQueries:
    end_date = datetime.now(UTC).date()
    start_date = end_date - timedelta(days=request.days)
    content, _ = complete(
        PROMPT_PATH.read_text(encoding="utf-8").strip(),
        json.dumps(
            {
                "topic": request.topic,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            }
        ),
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
