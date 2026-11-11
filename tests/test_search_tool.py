from datetime import date
from unittest.mock import Mock

import pytest
from pydantic import ValidationError

from src.agents import research_agent
from src.schemas.research import (
    ResearchQueries,
    ResearchRequest,
    SearchRequest,
    SearchResult,
)
from src.tools.search import SearchToolError


def test_bounded_search_and_deduplication(monkeypatch):
    plan = ResearchQueries(
        topic="Global risks",
        days=7,
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 8),
        queries=["Risk one", "Risk two", "Risk three", "Risk four"],
    )
    monkeypatch.setattr(research_agent, "generate_queries", lambda request: plan)
    tool = Mock()
    tool.search.return_value = [
        SearchResult(title="Report", url="https://example.com/report")
    ]
    result = research_agent.research(ResearchRequest(topic="Global risks"), tool)
    assert tool.search.call_count == 3
    assert len(result.results) == 1
    assert tool.search.call_args.args[0].start_date == plan.start_date
    tool.search.side_effect = SearchToolError("Search unavailable")
    with pytest.raises(SearchToolError):
        research_agent.research(ResearchRequest(topic="Global risks"), tool)


def test_search_request_rejects_reversed_dates():
    with pytest.raises(ValidationError):
        SearchRequest(
            query="Global risks", start_date=date(2026, 1, 8), end_date=date(2026, 1, 1)
        )


def test_search_result_rejects_non_web_url():
    with pytest.raises(ValidationError):
        SearchResult(title="Report", url="file:///etc/passwd")
