from fastapi import FastAPI

app = FastAPI(
    title="Global Risk Trend Analysis API",
    description="Agentic workflow for global risk research",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "global-risk-trend-analysis",
    }
