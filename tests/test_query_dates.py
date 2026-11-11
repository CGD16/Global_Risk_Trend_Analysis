import pytest
from pydantic import ValidationError

from src.schemas.research import QueryPlan


@pytest.mark.parametrize(
    "query",
    [
        "geopolitical risks November 2026",
        "trade risks 2026-11-11",
        "conflict updates 11.11.2026",
        "conflict updates 11/11",
        "trade risks NOVEMBER",
        "Handelsrisiken März",
        "trade risks 2026",
    ],
)
def test_rejects_calendar_dates(query):
    with pytest.raises(ValidationError, match="calendar dates"):
        QueryPlan(queries=[query])


def test_preserves_non_date_numbers_and_deduplication():
    plan = QueryPlan(queries=["G7 trade risks", " G7 TRADE risks ", "5G security"])
    assert plan.queries == ["G7 trade risks", "5G security"]
