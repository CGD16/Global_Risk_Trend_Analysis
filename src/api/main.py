from fastapi import FastAPI

from src.api.routes import health, llm, research

app = FastAPI(
    title="Global Risk Trend Analysis API",
    description="Agentic workflow for global risk research",
    version="0.1.0",
)

app.include_router(health.router)
app.include_router(llm.router)
app.include_router(research.router)
