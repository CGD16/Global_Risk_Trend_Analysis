"""Validated contracts for research query planning."""

from datetime import date
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

Query = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=3, max_length=200)
]


class ResearchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    topic: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=3, max_length=300)
    ]
    days: int = Field(default=7, ge=1, le=365, strict=True)


class QueryPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    queries: list[Query] = Field(min_length=1, max_length=5)

    @field_validator("queries")
    @classmethod
    def unique_queries(cls, queries: list[str]) -> list[str]:
        seen: set[str] = set()
        result = []
        for query in queries:
            key = " ".join(query.casefold().split())
            if key not in seen:
                seen.add(key)
                result.append(query)
        return result


class ResearchQueries(QueryPlan):
    topic: str
    days: int
    start_date: date
    end_date: date
