import httpx
import trafilatura
from app.config import settings

async def fetch_page(url: str) -> dict:
    """
    Downloads a page and extracts clean text
    return: a dict with the original HTML and either a JSON text block or plain text
    """
    headers = {"User-Agent": settings.user_agent}
    async with httpx.AsyncClient(
        timeout=settings.timeout_seconds,
        follow_redirects=True,
        headers=headers,
    ) as client:
        # To fetch the HTML content
        r = await client.get(url)
        r.raise_for_status()
        html = r.text

    # Requesting trafilatura for a structured JSON 
    extracted_json = trafilatura.extract(
        html,
        include_comments=False,
        include_tables=True,
        output_format="json",
    )
    if extracted_json:
        return {"url": url, "html": html, "text_json": extracted_json}

    #Fallback to plain text extraction
    text = trafilatura.extract(html) or ""
    return {"url": url, "html": html, "text": text}