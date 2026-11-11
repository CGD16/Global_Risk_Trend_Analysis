"""Provider-independent search contract; implementations must bound HTTP calls."""

from typing import Protocol

from src.schemas.research import SearchRequest, SearchResult


class SearchToolError(RuntimeError):
    """Search failed; messages must not contain credentials or response bodies."""


class SearchTool(Protocol):
    def search(self, request: SearchRequest) -> list[SearchResult]:
        """Perform one search without retries or pagination.

        HTTP implementations must use explicit timeouts, return at most
        request.max_results entries, and raise SearchToolError on failure.
        Retrieved text is untrusted data, never executable instructions.
        """
        ...
