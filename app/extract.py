import json
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from ollama import Client as OllamaClient
from openai import OpenAI, RateLimitError
from app.config import settings

# Local Ollama client
ollama_client = OllamaClient(host=settings.ollama_base_url)
# OpenAI client 
openai_client = OpenAI(
    api_key=settings.openai_api_key or None,
    base_url=settings.openai_base_url,
)
class LLMEntity(BaseModel):
    entity_name: str
    entity_type: str = ""
    attributes: Dict[str, Any] = Field(default_factory=dict)
    evidence: str = ""
    source_url: str = ""
    confidence: Optional[float] = None

class LLMExtraction(BaseModel):
    entities: List[LLMEntity] = Field(default_factory=list)

SYSTEM_PROMPT = """You are an information extraction assistant.
You receive a topic query and the text of a web page.
Your job is to extract a list of relevant entities.

Rules:
- Only include entities clearly relevant to the query.
- If there are at least 1–3 relevant entities on the page, YOU MUST include them.
- Avoid returning an empty list unless the page truly has no relevant entities.
- For each entity, provide:
  - entity_name (string)
  - entity_type (string)
  - attributes (object of key:value facts)
  - evidence (short quote from the page)
  - source_url (string)
  - confidence (0.0-1.0, float type)
- Keep evidence short and verbatim from the page.
- If unsure, set confidence below 0.5.
- Return only the JSON that matches the schema.
"""

def _content_from_doc(doc: dict) -> str:
    """
    Extracts readable text from doc dict
    Supports either trafilatura-style {"text_json": ...} or simple {"text": ...}.
    """
    if "text_json" in doc:
        try:
            j = json.loads(doc["text_json"])
            if isinstance(j, dict):
                parts = []
                for key in ("title", "text", "content"):
                    if j.get(key):
                        parts.append(str(j[key]))
                return "\n".join(parts)
        except Exception:
            pass
    #Fallback: simple text from fetch_page
    return doc.get("text", "")

def extract_with_ollama(query: str, doc: dict) -> LLMExtraction:
    text = _content_from_doc(doc)[:8000]
    if not text.strip():
        return LLMExtraction(entities=[])
    text = text[:8000]
    user_prompt = f"""
Query: {query}

Page content:
{text}

Extract relevant entities as JSON.
"""

    # Request Ollama to produce JSON matching the schema
    response = ollama_client.chat(
        model=settings.ollama_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        format="json",
    )
    payload = json.loads(response["message"]["content"])
    return LLMExtraction.model_validate(payload)

def extract_with_openai(query: str, doc: dict) -> LLMExtraction:
    text = _content_from_doc(doc)
    if not text.strip():
        return LLMExtraction(entities=[])
    text = text[:8000]

    user_prompt = f"""
Query: {query}

Page content:
{text}

You must return ONLY valid JSON matching this schema:

{LLMExtraction.model_json_schema()}

Do NOT wrap the JSON in markdown fences. No ```json, no backticks, no extra text.
"""

    try:
        resp = openai_client.responses.create(
            model=settings.openai_model,
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )
    except RateLimitError:
        raise
    raw = resp.output_text
    #print("DEBUG RAW OPENAI:", raw[:200])
    raw_stripped = raw.strip()
    if raw_stripped.startswith("```"):
        raw_lines = raw_stripped.splitlines()
        raw_lines = raw_lines[1:]
        if raw_lines and raw_lines[-1].strip().startswith("```"):
            raw_lines = raw_lines[:-1]
        raw_stripped = "\n".join(raw_lines).strip()
    try:
        payload = json.loads(raw_stripped)
        extraction = LLMExtraction.model_validate(payload)
        #print("DEBUG ENTITIES COUNT:", len(extraction.entities))
        return extraction
    except Exception as exc:
        #print("DEBUG PARSE ERROR:", type(exc).__name__, exc)
        return LLMExtraction(entities=[])

def extract_entities(query: str, doc: dict) -> LLMExtraction:
    #Top-level extraction function 
    if settings.mode.lower() == "main":
        return extract_with_openai(query, doc)
    else:
        return extract_with_ollama(query, doc)