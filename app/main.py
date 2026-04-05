from fastapi import FastAPI, Query
from app.pipeline import run_pipeline
from app.config import settings
# print("DEBUG MODE:", settings.mode)
# print("DEBUG BRAVE_API_KEY set:", bool(settings.brave_api_key))
# print("DEBUG OPENAI_API_KEY set:", bool(settings.openai_api_key))
app = FastAPI(title="Agentic Search", version="1.0")


@app.get("/search")
async def search(q: str = Query(..., min_length=2)):
    return await run_pipeline(q)