"""One bounded Tavily HTTP request per search, without retries."""

import json
import os
from datetime import date, datetime
from email.utils import parsedate_to_datetime
from urllib.error import URLError
from urllib.request import Request, urlopen

from src.schemas.research import SearchRequest, SearchResult
from src.tools.search import SearchToolError


def publication_date(value: str | None) -> date | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value).date()
    except ValueError:
        try:
            return parsedate_to_datetime(value).date()
        except (ValueError, TypeError, OverflowError):
            return None


class TavilySearchTool:
    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    @classmethod
    def from_environment(cls) -> "TavilySearchTool":
        key = os.environ.get("TAVILY_API_KEY", "").strip()
        if not key:
            raise ValueError("Tavily is not configured")
        return cls(key)

    def search(self, request: SearchRequest) -> list[SearchResult]:
        payload = {
            "query": request.query,
            "start_date": request.start_date.isoformat(),
            "end_date": request.end_date.isoformat(),
            "max_results": request.max_results,
            "search_depth": "basic",
            "topic": "general",
            "include_published_date": True,
            "include_answer": False,
            "include_raw_content": False,
            "auto_parameters": False,
        }
        http_request = Request(
            "https://api.tavily.com/search",
            data=json.dumps(payload).encode(),
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urlopen(http_request, timeout=30) as response:
                # Bound response memory as well as the number of results.
                raw = response.read(2_000_001)
            if len(raw) > 2_000_000:
                raise ValueError("Response too large")
            body = json.loads(raw)
            items = body["results"]
            if not isinstance(items, list):
                raise TypeError("Invalid results")
            results = []
            for item in items[: request.max_results]:
                if not isinstance(item, dict):
                    raise TypeError("Invalid search result")
                result = SearchResult(
                    title=item["title"],
                    url=item["url"],
                    published_date=publication_date(item.get("published_date")),
                    excerpt=item.get("content"),
                )
                result.source = result.url.host
                results.append(result)
            return results
        except (URLError, OSError, ValueError, TypeError, KeyError):
            raise SearchToolError("Tavily search failed") from None
