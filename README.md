# Global Risk Trend Analysis — current implementation

The working scope is a FastAPI API and a minimal Research Agent that generates
validated search queries using local Docker Model Runner. It does not search the
web or produce research findings yet. The pipeline design below is a future vision.

## Run and test

Use Python 3.12 and uv. Start Docker Model Runner with
`ai/qwen3.5:9B-UD-Q4_K_XL` available at
`http://localhost:12434/engines/v1`, then run:

```bash
uv sync
uv run uvicorn src.api.main:app --reload
```

Endpoints:

- `GET /health`: API process health; does not check model availability.
- `GET /llm/test`: tests the API-to-model connection.
- `POST /research/queries`: generates search queries without executing searches.

The endpoint definitions live in `src/api/routes/`:

| File | Endpoint |
| --- | --- |
| `src/api/routes/health.py` | `GET /health` |
| `src/api/routes/llm.py` | `GET /llm/test` |
| `src/api/routes/research.py` | `POST /research/queries` |

Each module defines an `APIRouter`. `src/api/main.py` imports these modules and
registers their routers using `app.include_router(...)`. This folder structure is
a project convention; FastAPI does not require it. The route module
`src/api/routes/llm.py` handles HTTP requests, while `src/llm/client.py` handles
communication with the local model.

Open http://127.0.0.1:8000/docs to view and test the endpoints interactively.
There is currently no endpoint defined for `/`, so the base URL returns `404`.

```bash
curl -X POST http://localhost:8000/research/queries   -H 'Content-Type: application/json'   -d '{"topic":"Geopolitical risks","days":7}'
```

The response contains `topic`, `days`, `start_date`, `end_date`, and `queries`.
Dates are calculated by the application in UTC: end is today and start is
today minus `days`. Future search adapters must apply these date bounds separately.
Queries are plain search terms usable by Tavily or NewsAPI, rather than claims
about existing articles.

Topics must contain 3–300 characters after trimming; days must be an integer
from 1–365 (default 7). The model returns 1–5 queries of 3–200 characters.
Case and whitespace equivalent queries are deduplicated. Each request makes one
model call, with a 120-second timeout, no retries, a 512-token output limit, and
thinking disabled. Invalid JSON, empty or truncated output, and upstream errors
return a sanitized `502`; invalid request bodies return `422`.

```bash
uv run pytest
uv run ruff check src tests
uv run ruff format --check src tests
```

Implementation: `src/api/main.py` creates the app and registers the routers in
`src/api/routes/` (health, LLM test, research). `src/llm/client.py` handles model
communication, `src/agents/research_agent.py` coordinates query generation, and
`src/schemas/research.py` validates input and output. The research system prompt
lives in `prompts/research_queries.txt` and is loaded relative to the module,
independently of the working directory. Keep the `prompts/` directory alongside
`src/` when deploying. Tests use mocked model responses and require no running
model or external API keys.


## Current project structure

```text
src/
├── api/
│   ├── main.py
│   └── routes/          # Health, LLM test, and research endpoints
├── llm/                 # Central local model client
├── agents/              # Research query generation
├── schemas/             # Validated requests and responses
└── utils/               # Placeholder for shared helpers
prompts/                 # Research prompt files
tests/                   # Tests with mocked model responses
dist/                    # Placeholder for generated reports and newsletters
```

`src/utils/` and `dist/` contain `.gitkeep` placeholder files so Git preserves
these directories. Generated files in `dist/` are ignored.

---

## Future pipeline design (not implemented)

The following original design notes describe planned features. Their setup,
commands, and file layout do not describe the current implementation.

# 🌐 WEF-Aligned Multi-Agent Trend Intelligence & Newsletter Pipeline

An automated multi-agent AI framework that leverages the World Economic Forum (WEF) Global Risks Report taxonomy to monitor macro-trends [¹], scrape news across five core pillars, synthesize actionable insights, generate visualizations, and deliver executive email newsletters.

> **Status:** Early development. The FastAPI backend and local LLM connection are working; the agents, scraping, charting and email delivery described below are planned (see [Roadmap](#-roadmap)).

---

## 📌 Table of Contents

- [Overview](#-overview)
- [System Architecture](#-system-architecture)
- [Core Features](#-core-features)
- [WEF Risk Pillars](#-wef-risk-pillars)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [LLM Setup](#llm-setup)
  - [Configuration](#configuration)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Configuration Reference](#-configuration-reference-taxonomyyaml-planned)
- [Roadmap](#-roadmap)
- [License](#-license)

---

## 🚀 Overview

The **WEF Trend Intelligence Pipeline** automates the workflow of macro-trend monitoring. Modeled around the annual **WEF Global Risks Report** structure, the system uses specialized AI agents to:

1. Map baseline trend categories to current real-world global dynamics.
2. Dynamically extract relevant news from credible sources.
3. Summarize complex news into executive-level key takeaways.
4. Convert data insights into dynamic visuals and charts.
5. Compile and send an HTML email newsletter to targeted subscribers.

The agents are exposed through a **FastAPI** service, so they can be orchestrated uniformly via API endpoints.

---

## 🏗 System Architecture

The pipeline uses a **Multi-Agent Orchestration Architecture** (e.g., LangGraph, CrewAI, or AutoGen), served through a FastAPI interface.

```
   ┌───────────────────────────────────────────────────────────┐
   │ 1. Trend Ingestion Agent (WEF Taxonomy & Keyword Generator)│
   └─────────────────────────────┬─────────────────────────────┘
                                 │
                                 ▼
   ┌───────────────────────────────────────────────────────────┐
   │ 2. News Scraping & Curation Agent (Search & Filtering)    │
   └─────────────────────────────┬─────────────────────────────┘
                                 │
                                 ▼
   ┌───────────────────────────────────────────────────────────┐
   │ 3. Synthesis & Summarization Agent (Macro-Analyst)       │
   └─────────────────────────────┬─────────────────────────────┘
                                 │
                                 ▼
   ┌───────────────────────────────────────────────────────────┐
   │ 4. Data Visualization & Media Agent (Charts & Infographics)│
   └─────────────────────────────┬─────────────────────────────┘
                                 │
                                 ▼
   ┌───────────────────────────────────────────────────────────┐
   │ 5. Newsletter & Email Dispatcher Agent (HTML / SMTP API)   │
   └───────────────────────────────────────────────────────────┘
```

---

## ✨ Core Features

* **WEF Taxonomy Alignment:** Structured around 5 core macro categories (Economic, Environmental, Geopolitical, Societal, Technological).
* **Automated Web Scraping & Curation:** Ingests live news via Tavily, NewsAPI, RSS feeds, or custom scrapers with deduplication and source-credibility scoring.
* **Smart Summarization:** Extracts macro implications, key bullet points, and "Why It Matters" sections without hallucinations.
* **Automated Chart Generation:** Generates responsive visual charts (e.g., QuickChart API, Chart.js) visualizing trend scores, news volume, or risk heatmaps.
* **Responsive HTML Newsletter:** Assembles modern, mobile-ready email templates ready for automated distribution via SendGrid, Mailgun, or SMTP.
* **Local or Cloud LLMs:** Works with any OpenAI-compatible endpoint (Ollama, Docker Model Runner, OpenAI).

---

## 🏛 WEF Risk Pillars

The multi-agent system categorizes all analysis into five predefined domains:

| Pillar | Focus Areas |
| :--- | :--- |
| **📈 Economic** | Inflation, geoeconomic confrontation, public debt, supply chain disruption |
| **🌍 Environmental** | Extreme weather, Earth system tipping points, biodiversity loss, resource scarcity |
| **⚔️ Geopolitical** | Interstate conflict, cyber warfare, global governance breakdown |
| **👥 Societal** | Social polarization, misinformation/disinformation, cost of living, public health |
| **🤖 Technological** | AI governance risks, cybersecurity vulnerabilities, digital inequality |

---

## 🛠 Getting Started

### Prerequisites

* **[uv](https://docs.astral.sh/uv/):** Python package and environment manager (replaces `pip`, `venv` and `requirements.txt`). It also downloads Python 3.12 automatically if it is missing.
  ```bash
  # macOS / Linux
  curl -LsSf https://astral.sh/uv/install.sh | sh
  # Windows (PowerShell)
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```
* **An LLM backend** (one of):
  * a local model via Ollama or Docker Model Runner (no API key needed), or
  * an OpenAI API key.
* **Optional (planned features):** Tavily or NewsAPI key for news search.

### Installation

```bash
git clone https://github.com/CGD16/Global_Risk_Trend_Analysis.git
cd Global_Risk_Trend_Analysis
uv sync
```

`uv sync` creates a project-local virtual environment (`.venv`) and installs all dependencies from `pyproject.toml` / `uv.lock`. You do not need to create or activate an environment manually.

Add new packages with `uv add <package>` (not `pip install`).

### LLM Setup

The app talks to a local model through the OpenAI-compatible API. Choose **one** option.

**Option A: Docker Model Runner**

Requires Docker with the Model Runner plugin and host-side TCP support enabled (port 12434).

```bash
docker model pull ai/qwen3.5:9B-UD-Q4_K_XL
```

In `src/api/main.py`:

```python
client = OpenAI(
    base_url="http://localhost:12434/engines/v1",
    api_key="not-needed",
    timeout=120.0,
)
MODEL = "ai/qwen3.5:9B-UD-Q4_K_XL"
```

**Option B: Ollama**

```bash
curl -fsSL https://ollama.com/install.sh | sh     # Linux; other OS: https://ollama.com
ollama pull hf.co/unsloth/Qwen3.5-9B-GGUF:UD-Q4_K_XL
ollama list                                       # shows the exact model name
```

In `src/api/main.py`:

```python
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="not-needed",
    timeout=120.0,
)
MODEL = "hf.co/unsloth/Qwen3.5-9B-GGUF:UD-Q4_K_XL"
```

> A 9B model in Q4 needs roughly 6–8 GB of free RAM/VRAM. Qwen3.5 is a reasoning model, so the first request can be slow; raise `timeout` (e.g. to `300.0`) if requests time out.

### Configuration

Create a `.env` file in the project root (it is git-ignored):

```env
# Only needed if you use OpenAI instead of a local model
OPENAI_API_KEY=REPLACE_WITH_YOUR_API_KEY

# News & scraping services (planned features)
TAVILY_API_KEY=your_tavily_api_key_here
NEWS_API_KEY=your_news_api_key_here
```

---

## 🚀 Usage

Start the API in development mode:

```bash
uv run fastapi dev src/api/main.py
```

* API: http://127.0.0.1:8000
* Interactive docs: http://127.0.0.1:8000/docs
* Health check: `curl http://127.0.0.1:8000/health`

If the `fastapi` command complains about a missing `fastapi[standard]`, either add it permanently with `uv add "fastapi[standard]"` or run once with:

```bash
uv run --with "fastapi[standard]" fastapi dev src/api/main.py
```

Alternatively, start with uvicorn directly:

```bash
uv run uvicorn src.api.main:app --reload
```

### Planned CLI

Once the agents are implemented, the full pipeline and a dry-run preview mode are planned:

```bash
# Full run: Ingestion ➔ Scraping ➔ Summarization ➔ Charting ➔ Delivery
uv run python main.py --mode full --output email

# Preview without sending email
uv run python main.py --mode preview --output-file dist/newsletter_preview.html
```

---

## 📁 Project Structure

### Current

```text
├── src/
│   └── api/
│       └── main.py             # FastAPI app (health check + LLM endpoint)
├── .gitignore                  # ignores .env and .venv
├── .python-version             # Python 3.12
├── Development_list.txt
├── pyproject.toml              # Dependencies (managed by uv)
├── uv.lock                     # Locked dependency versions
├── recommendation.md
└── README.md
```

### Planned

```text
├── config/
│   ├── taxonomy.yaml           # WEF pillars, keywords, and domain weightings
│   └── newsletter_template.html # Responsive HTML email template
├── src/
│   ├── agents/
│   │   ├── trend_agent.py      # Agent 1: Trend & Keyword Generator
│   │   ├── scraper_agent.py    # Agent 2: Scraping & Curation
│   │   ├── synthesis_agent.py  # Agent 3: Summarization Engine
│   │   ├── visualization_agent.py # Agent 4: Chart/Image Generator
│   │   └── publisher_agent.py  # Agent 5: Newsletter & Email Sender
│   ├── tools/
│   │   ├── news_api.py         # Scraping utilities
│   │   └── chart_builder.py    # QuickChart / Chart.js integration
│   └── utils/
│       └── logger.py
├── tests/
└── .env.example
```

---

## ⚙️ Configuration Reference (`taxonomy.yaml`, planned)

You will be able to customize the focus topics for each pillar in `config/taxonomy.yaml`:

```yaml
pillars:
  economic:
    keywords: ["inflation", "supply chain", "geoeconomic sanctions", "debt crisis"]
    sources: ["ft.com", "bloomberg.com", "reuters.com"]
  environmental:
    keywords: ["extreme weather", "decarbonization", "biodiversity loss", "climate failure"]
    sources: ["nature.com", "reuters.com", "theguardian.com"]
  geopolitical:
    keywords: ["cyber conflict", "trade warfare", "state breakdown"]
    sources: ["foreignaffairs.com", "bbc.com", "apnews.com"]
  societal:
    keywords: ["misinformation", "social polarization", "cost of living"]
    sources: ["reuters.com", "dw.com"]
  technological:
    keywords: ["AI safety", "cybersecurity vulnerabilities", "quantum risks"]
    sources: ["techcrunch.com", "wired.com", "mit.edu"]
```

---

## 🗺 Roadmap

- [x] Initial Multi-Agent Architecture Design
- [x] WEF Risk Taxonomy Mapping
- [x] Dependency management with uv
- [x] FastAPI backend with local LLM connection (Docker Model Runner / Ollama)
- [ ] Move LLM URL and model name into `.env` (`LLM_BASE_URL`, `LLM_MODEL`)
- [ ] Auto-scraping pipeline implementation (Tavily / NewsAPI)
- [ ] Automated HTML template compiler with Chart.js / QuickChart
- [ ] Subscriber management database integration
- [ ] Multi-language support (EN / DE)

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

[¹]: https://www.weforum.org/publications/global-risks-report-2026
