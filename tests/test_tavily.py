import json
from datetime import date
from io import BytesIO
from urllib.error import HTTPError

import pytest
from fastapi.testclient import TestClient

from src.agents import research_agent
from src.api.main import app
from src.tools import tavily
from src.tools.search import SearchToolError


def test_http_normalization_and_limits(monkeypatch):
    def fake_open(request, timeout):
        payload = json.loads(request.data)
        assert timeout == 30
        assert request.get_header("Authorization") == "Bearer test-secret"
        assert payload["start_date"] == "2026-11-04"
        assert payload["end_date"] == "2026-11-11"
        assert payload["max_results"] == 1
        assert payload["search_depth"] == "basic"
        return BytesIO(
            json.dumps(
                {
                    "results": [
                        {
                            "title": "Report",
                            "url": "https://example.com/report",
                            "published_date": "Tue, 10 Nov 2026 17:00:00 GMT",
                            "content": "Untrusted excerpt",
                        }
                    ]
                    * 2
                }
            ).encode()
        )

    monkeypatch.setattr(tavily, "urlopen", fake_open)
    results = tavily.TavilySearchTool("test-secret").search(
        tavily.SearchRequest(
            query="Global risks",
            start_date=date(2026, 11, 4),
            end_date=date(2026, 11, 11),
            max_results=1,
        )
    )
    assert len(results) == 1
    assert results[0].source == "example.com"
    assert results[0].published_date == date(2026, 11, 10)
    assert results[0].excerpt == "Untrusted excerpt"


@pytest.mark.parametrize(
    "body",
    [
        b"not json",
        b"{}",
        b'{"results":null}',
        b'{"results":[{"title":"x","url":"file:///tmp/x"}]}',
    ],
)
def test_invalid_response_is_sanitized(monkeypatch, body):
    monkeypatch.setattr(tavily, "urlopen", lambda *a, **k: BytesIO(body))
    with pytest.raises(SearchToolError, match="^Tavily search failed$"):
        tavily.TavilySearchTool("secret").search(
            tavily.SearchRequest(
                query="Global risks",
                start_date=date(2026, 11, 4),
                end_date=date(2026, 11, 11),
            )
        )


def test_missing_key_skips_model(monkeypatch):
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)
    monkeypatch.setattr(
        research_agent, "complete", lambda *a: pytest.fail("Model called")
    )
    with TestClient(app) as client:
        assert (
            client.post("/research/search", json={"topic": "Global risks"}).status_code
            == 503
        )


def test_timeout_is_sanitized_without_retry(monkeypatch):
    calls = []

    def fail(*args, **kwargs):
        calls.append(1)
        raise TimeoutError("private network details")

    monkeypatch.setattr(tavily, "urlopen", fail)
    with pytest.raises(SearchToolError, match="^Tavily search failed$"):
        tavily.TavilySearchTool("secret").search(
            tavily.SearchRequest(
                query="Global risks",
                start_date=date(2026, 11, 4),
                end_date=date(2026, 11, 11),
            )
        )
    assert len(calls) == 1


def test_endpoint_search_deduplication_and_failure(monkeypatch):
    monkeypatch.setenv("TAVILY_API_KEY", "test-secret")
    monkeypatch.setattr(
        research_agent,
        "complete",
        lambda *a: ('{"queries":["trade risks","conflict risks"]}', None),
    )
    calls = []

    def fake_open(request, timeout):
        calls.append(request)
        return BytesIO(
            b'{"results":[{"title":"Report","url":"https://example.com/report"}]}'
        )

    monkeypatch.setattr(tavily, "urlopen", fake_open)
    with TestClient(app) as client:
        response = client.post("/research/search", json={"topic": "Global risks"})
        assert response.status_code == 200
        assert len(calls) == 2
        assert len(response.json()["results"]) == 1
        assert response.json()["results"][0]["published_date"] is None

        def fail(*args, **kwargs):
            raise HTTPError("https://api.tavily.com", 401, "secret", {}, None)

        monkeypatch.setattr(tavily, "urlopen", fail)
        response = client.post("/research/search", json={"topic": "Global risks"})
        assert response.status_code == 502
        assert response.json() == {"detail": "Web search failed"}


@pytest.mark.parametrize("value", [None, "unknown", "2026-11-10T17:00:00Z"])
def test_optional_dates(value):
    assert tavily.publication_date(value) == (
        date(2026, 11, 10) if value and value.endswith("Z") else None
    )
