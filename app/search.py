import httpx
from app.schemas import SearchResult
from app.config import settings
import requests

async def search_duckduckgo(query: str, count: int) -> list[SearchResult]:
    """
    Free search using DuckDuckGo Instant Answer API.
    Tries RelatedTopics first, then falls back to Results.
    """
    params = {
        "q": query,
        "format": "json",
        "no_html": 1,
        "skip_disambig": 1,
    }

    async with httpx.AsyncClient(timeout=settings.timeout_seconds) as client:
        r = await client.get("https://api.duckduckgo.com", params=params)
        r.raise_for_status()
        data = r.json()

    out: list[SearchResult] = []
    related = data.get("RelatedTopics", [])
    for item in related[:count]:
        url = item.get("FirstURL")
        text = item.get("Text", "")
        if not url:
            continue
        out.append(SearchResult(
            title=text[:100],
            url=url,
            snippet=text[:200],
        ))
    # If we didn't get enough, try Results as a fallback.
    if len(out) < count:
        for item in data.get("Results", [])[: count - len(out)]:
            url = item.get("FirstURL")
            text = item.get("Text", "")
            if not url:
                continue
            out.append(SearchResult(
                title=text[:100],
                url=url,
                snippet=text[:200],
            ))

    # print("DDG search hit count:", len(out))
    return out

def search_brave(query: str, count: int = None):
    if count is None:
        count = settings.top_k

    url = "https://api.search.brave.com/res/v1/web/search"
    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": settings.brave_api_key,
        "User-Agent": settings.user_agent,
    }
    params = {
        "q": query,
        "count": count,
        "country": "us",
        "search_lang": "en",
    }
    resp = requests.get(url, headers=headers, params=params, timeout=settings.timeout_seconds)
    resp.raise_for_status()
    data = resp.json()
    results = []
    for item in data.get("web", {}).get("results", []):
        results.append(
            {
                "title": item.get("title"),
                "url": item.get("url"),
                "snippet": item.get("description"),
            }
        )
    return results

async def search_web(query: str, count: int | None = None) -> list[SearchResult]:
    #Top-level search function used by the pipeline
    count = count or settings.top_k
    if settings.mode.lower() == "main":
        return search_brave(query, count)
    else:
        return await search_duckduckgo(query, count)