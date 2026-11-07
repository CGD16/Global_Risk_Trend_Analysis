from fastapi import FastAPI, HTTPException
from openai import OpenAI, OpenAIError

app = FastAPI(
    title="Global Risk Trend Analysis API",
    description="Agentic workflow for global risk research",
    version="0.1.0",
)

# Local Docker Model Runner
client = OpenAI(
    base_url="http://localhost:12434/engines/v1",
    api_key="not-needed",
    timeout=120.0,
)

MODEL = "ai/qwen3.5:9B-UD-Q4_K_XL"


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/llm/test")
def test_llm():
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a research assistant specializing in global risks.",
                },
                {
                    "role": "user",
                    "content": "What are geopolitical risks? Answer in one sentence.",
                },
            ],
            max_tokens=256,
            extra_body={
                "chat_template_kwargs": {
                    "enable_thinking": False
                }
            },
        )

        return {
            "model": MODEL,
            "response": response.choices[0].message.content,
            "tokens_used": response.usage.total_tokens if response.usage else None,
        }

    except OpenAIError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Local LLM request failed: {exc}",
        ) from exc
