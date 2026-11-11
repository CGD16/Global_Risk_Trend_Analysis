"""Validated contracts for research query planning."""

import re
from datetime import date
from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    StringConstraints,
    field_validator,
    model_validator,
)

Query = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=3, max_length=200)
]

QUERY_DATE = re.compile(
    r"\b(?:19|20)\d{2}\b"
    r"|\b\d{1,2}[./-]\d{1,2}(?:[./-]\d{2,4})?\b"
    r"|\b(?:january|february|march|april|may|june|july|august|september|"
    r"october|november|december|januar|februar|märz|mai|juni|juli|"
    r"oktober|dezember)\b",
    re.IGNORECASE,
)


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
            if QUERY_DATE.search(query):
                raise ValueError("Queries must not contain calendar dates")
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


class SearchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    query: Query
    start_date: date
    end_date: date
    max_results: int = Field(default=5, ge=1, le=5, strict=True)

    @model_validator(mode="after")
    def ordered_dates(self) -> "SearchRequest":
        if self.start_date > self.end_date:
            raise ValueError("start_date must not exceed end_date")
        return self


class SearchResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    url: HttpUrl
    published_date: date | None = None
    source: str | None = None
    excerpt: str | None = None


class ResearchResults(ResearchQueries):
    results: list[SearchResult]
