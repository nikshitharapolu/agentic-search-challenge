import httpx
from .config import settings

async def fetch_page(url: str) -> dict:
    """
    Fetches a web page and returns a simple dict:
    { "url": ..., "text": ... }
    Return: an empty text on errors so the pipeline can continue
    """
    headers = {"User-Agent": settings.user_agent}
    async with httpx.AsyncClient(follow_redirects=True, timeout=settings.timeout_seconds) as client:
        try:
            resp = await client.get(url, headers=headers)
        except httpx.RequestError:
            return {"url": url, "text": ""}
    if resp.status_code >= 400:
        return {"url": url, "text": ""}
    return {"url": url, "text": resp.text or ""}