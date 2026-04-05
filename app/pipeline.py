from app.extract import _content_from_doc
from app.search import search_web
from app.extract import extract_entities
from app.utils import dedupe_entities
from app.schemas import QueryResponse, EntityRow, Evidence
from app.config import settings
from urllib.parse import urlparse
from .fetch import fetch_page


def is_duckduckgo(url: str) -> bool:
    return urlparse(url).netloc.lower().endswith("duckduckgo.com")

async def run_pipeline(query: str) -> QueryResponse:
    """
    End-to-end pipeline:
        search_web: Brave
        fetch_page: scrape pages
        extract_entities: Ollama/OpenAI 
        dedupe + bundle results with provenance
    """
    sources = await search_web(query)
    rows: list[EntityRow] = []
    notes: list[str] = []

    for src in sources[:settings.max_pages]:
    #for src in sources[: min(settings.max_pages, 2)]:
        url = src["url"]

        if is_duckduckgo(url):
            notes.append(f"Skipped {url} (duckduckgo internal)")
            continue
        try:
            doc = await fetch_page(url)
            text = _content_from_doc(doc)
            # print(f"DEBUG len(text) for {url}: {len(text)}")
            extraction = extract_entities(query, doc)
            # Attaching provenance to each entity
            for e in extraction.entities:
                rows.append(
                    EntityRow(
                        entity_name=e.entity_name,
                        entity_type=e.entity_type,
                        attributes=e.attributes,
                        provenance=[
                            Evidence(
                                source_url=e.source_url or url,
                                source_title=src["title"],
                                evidence_text=e.evidence,
                                confidence=e.confidence,
                            )
                        ],
                    )
                )
        except Exception as exc:
            notes.append(f"Failed {url}: {type(exc).__name__}")
    rows = dedupe_entities(rows)
    return QueryResponse(query=query, results=rows, sources=sources, notes=notes)