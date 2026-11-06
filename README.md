# 🌐 WEF-Aligned Multi-Agent Trend Intelligence & Newsletter Pipeline

An automated multi-agent AI framework that leverages the World Economic Forum (WEF) Global Risks Report taxonomy to monitor macro-trends [¹], scrape news across five core pillars, synthesize actionable insights, generate visualizations, and deliver executive email newsletters.

---

## 📌 Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Core Features](#core-features)
- [WEF Risk Pillars](#wef-risk-pillars)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Configuration Reference](#configuration-reference)
- [Roadmap](#roadmap)
- [License](#license)

---

## 🚀 Overview

The **WEF Trend Intelligence Pipeline** automates the workflow of macro-trend monitoring. Modeled around the annual **WEF Global Risks Report** structure, the system uses specialized AI agents to:

1. Map baseline trend categories to current real-world global dynamics.
2. Dynamically extract relevant news from credible sources.
3. Summarize complex news into executive-level key takeaways.
4. Convert data insights into dynamic visuals and charts.
5. Compile and send an HTML email newsletter to targeted subscribers.

---

## 🏗 System Architecture

The pipeline uses a **Multi-Agent Orchestration Architecture** (e.g., LangGraph, CrewAI, or AutoGen).

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

* **Python:** 3.10 or higher
* **API Keys:**
  * OpenAI API / Anthropic API (for LLM backend)
  * Tavily AI or NewsAPI key (for web scraping/search)
  * SendGrid / Mailgun API key (or SMTP credentials for sending emails)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-org/wef-trend-intelligence-agent.git
   cd wef-trend-intelligence-agent
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

### Configuration

Create a `.env` file in the root directory:

```env
# LLM Provider Setup
OPENAI_API_KEY=your_openai_api_key_here

# News & Scraping Services
TAVILY_API_KEY=your_tavily_api_key_here
NEWS_API_KEY=your_news_api_key_here

# Email Delivery Configuration
EMAIL_PROVIDER=sendgrid  # Options: sendgrid, smtp
SENDGRID_API_KEY=your_sendgrid_api_key
SENDER_EMAIL=newsletter@yourdomain.com

# SMTP Backup Settings (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

---

## 🚀 Usage

### 1. Run the Full Multi-Agent Pipeline

To trigger the complete workflow (Ingestion ➔ Scraping ➔ Summarization ➔ Charting ➔ Delivery):

```bash
python main.py --mode full --output email
```

### 2. Run Preview / Dry Run Mode (No Email Sent)

To preview the newsletter locally as an HTML file without triggering email distribution:

```bash
python main.py --mode preview --output-file dist/newsletter_preview.html
```

---

## 📁 Project Structure

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
├── .env.example
├── main.py                     # Pipeline Orchestrator Entrypoint
├── README.md
└── requirements.txt
```

---

## ⚙️ Configuration Reference (`taxonomy.yaml`)

You can customize the underlying focus topics for each pillar in `config/taxonomy.yaml`:

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
- [ ] Auto-scraping pipeline implementation (Tavily / NewsAPI)
- [ ] Automated HTML template compiler with Chart.js / QuickChart
- [ ] Subscriber management database integration
- [ ] Multi-language support (EN / DE)

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

[¹]: https://www.weforum.org/publications/global-risks-report-2026
