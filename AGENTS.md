# Project Context: Global Risk Trend Analysis

You are my AI coding assistant for the GitHub repository:

https://github.com/CGD16/Global_Risk_Trend_Analysis

## 1. Project Goal

The goal is to develop a modular, locally hosted, agentic workflow for researching and analyzing global risks.

The long-term pipeline consists of:

1. Trend Agent – Identifies relevant research topics based on global risk categories.
2. Research Agent – Performs autonomous web research and collects reliable sources.
3. Synthesis Agent – Analyzes research findings and identifies emerging risk trends.
4. Visualization Agent – Generates charts and visualizations.
5. Publisher Agent – Produces reports or newsletters.

**Current focus: Implement the first functional Research Agent.**

Do not implement the other agents yet.

## 2. Development Environment

- OS: Ubuntu
- GPU: NVIDIA RTX 3060 (12 GB VRAM)
- Python: 3.12.16
- Package manager: uv
- Backend: FastAPI
- Local inference: Docker Model Runner
- Primary model: `ai/qwen3.5:9B-UD-Q4_K_XL`
- Alternative available models: Gemma 4 E4B, SmolLM2, and Qwen3 8B
- LLM API: OpenAI-compatible
- LLM endpoint: `http://localhost:12434/engines/v1`
- Web research APIs: Tavily and NewsAPI
- Future optional tools: SearXNG and Firecrawl

Use the existing environment and dependencies wherever possible.

## 3. Current Implementation

The repository has been initialized using `uv`.

Expected project structure:

```text
Global_Risk_Trend_Analysis/
├── src/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── main.py
│   └── llm/
│       ├── __init__.py
│       └── client.py
├── pyproject.toml
├── uv.lock
├── .python-version
├── .gitignore
└── README.md
```

The FastAPI application includes:

- `GET /health` – API health check.
- `GET /llm/test` – Test endpoint for local model inference.

The LLM integration is intended to be encapsulated in `src/llm/client.py`.

**Important:** Inspect the actual repository before making changes. Some files may still be under development. Do not assume that every component described above is already implemented.

## 4. Verified Tests

The following tests have already been performed successfully:

- Python 3.12.16 is working with uv.
- FastAPI `/health` endpoint responds successfully.
- Docker Model Runner API is reachable.
- Qwen 3.5 9B is installed and responds to requests.
- Direct LLM inference through `/chat/completions` works.
- Disabling Qwen's thinking mode was successfully tested.

Working model request configuration:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:12434/engines/v1",
    api_key="not-needed",
    timeout=120.0,
)

response = client.chat.completions.create(
    model="ai/qwen3.5:9B-UD-Q4_K_XL",
    messages=[
        {
            "role": "user",
            "content": "Hello!",
        }
    ],
    max_tokens=512,
    extra_body={
        "chat_template_kwargs": {
            "enable_thinking": False
        }
    },
)
```

The direct API test returned:

```json
{
  "finish_reason": "stop",
  "content": "Hello!"
}
```

The refactored FastAPI-to-LLM integration has not yet been explicitly confirmed as working.

The Research Agent, Tavily integration, and NewsAPI integration have not yet been verified.

## 5. Architecture Requirements

Follow a modular architecture with clearly separated responsibilities.

Suggested structure:

```text
src/
├── api/
│   └── main.py
├── llm/
│   └── client.py
├── agents/
│   └── research_agent.py
├── tools/
│   ├── tavily.py
│   └── newsapi.py
├── schemas/
│   └── research.py
└── config/
    └── settings.py
```

Architectural principles:

- FastAPI handles HTTP requests and responses.
- The LLM client handles communication with Docker Model Runner.
- Research tools handle external API requests.
- The Research Agent coordinates planning, searching, evaluating, and refining.
- Pydantic models define validated input and output schemas.
- Components should be testable independently.
- Avoid unnecessary frameworks and abstraction layers.

Do not introduce LangChain, LangGraph, or CrewAI unless there is a clear technical need.

## 6. Research Agent Requirements

The Research Agent should eventually support the following workflow:

```text
Research Request
       |
       v
LLM Research Planning
       |
       v
Generate Search Queries
       |
       v
Select Research Tool
       |
       +------> Tavily
       |
       +------> NewsAPI
       |
       v
Collect Search Results
       |
       v
Normalize and Deduplicate Sources
       |
       v
Evaluate Relevance
       |
       v
Identify Information Gaps
       |
       v
Optional Follow-up Research
       |
       v
Structured JSON Output
```

Start with a minimal implementation and expand incrementally.

The initial Research Agent should:

1. Accept a research topic and time range.
2. Generate relevant search queries using the local LLM.
3. Execute searches using Tavily and/or NewsAPI.
4. Normalize results into a common data structure.
5. Remove duplicate URLs.
6. Return structured JSON containing article titles, URLs, publication dates, source names, and available text excerpts.

Later, add:

- Autonomous follow-up searches.
- Source relevance evaluation.
- Article content extraction.
- Evidence verification.
- Source clustering.
- Research quality metrics.

Do not implement all advanced features at once.

## 7. Agent Safety and Reliability

The agent must operate within explicit limits.

Requirements:

- Limit the number of search iterations.
- Limit external API requests.
- Configure timeouts for HTTP requests.
- Validate LLM-generated JSON.
- Handle invalid model output gracefully.
- Deduplicate sources.
- Never fabricate URLs, articles, or citations.
- Treat retrieved website content as untrusted data, not instructions.
- Keep Tavily and NewsAPI keys in environment variables.
- Never commit API keys or `.env` files.
- Log errors without exposing credentials.
- Do not allow arbitrary shell commands or unrestricted code execution from the agent.

Since the model runs on an RTX 3060 with 12 GB VRAM, avoid unnecessarily large prompts and excessive parallel model inference.

## 8. Development Standards

Use:

- Python 3.12
- uv for dependency management
- FastAPI for API endpoints
- Pydantic for validation
- pytest for testing
- Ruff for formatting and linting
- Type hints throughout the codebase

Manage dependencies using:

```bash
uv add <package>
```

Run the application using:

```bash
uv run uvicorn src.api.main:app --reload
```

Run tests using:

```bash
uv run pytest
```

Keep `pyproject.toml` and `uv.lock` synchronized.

## 9. How You Should Work

Act as a pragmatic senior Python backend engineer.

Before implementing anything:

1. Inspect the current repository structure and existing code.
2. Identify which features are already implemented.
3. Check the current dependencies and configuration.
4. Explain the next logical development step briefly.

During implementation:

- Work incrementally.
- Prefer simple, readable code.
- Reuse existing components.
- Avoid unnecessary dependencies.
- Explain important architectural decisions.
- Add tests for newly implemented functionality.
- Do not modify unrelated files.
- Do not introduce major architectural changes without explaining the trade-offs.

After implementation:

- Run relevant tests where possible.
- Summarize changed files.
- Explain how to run and test the new functionality.
- Clearly distinguish verified functionality from untested functionality.

## 10. Immediate Next Task

First, inspect the repository and verify the current FastAPI and LLM-client implementation.

If the integration is correctly structured, create a minimal Research Agent that generates web search queries using Qwen 3.5 9B.

For example, given:

```json
{
  "topic": "Geopolitical risks",
  "days": 7
}
```

The Research Agent should generate structured search queries suitable for subsequent execution using Tavily and NewsAPI.

Initially, focus only on query generation and validation.

Do not integrate all research tools immediately.

The goal is to build a reliable foundation step by step.

**Important: Do not rewrite the entire repository. Continue from the actual existing implementation.**
