from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional

class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str = ""

class Evidence(BaseModel):
    source_url: str
    source_title: str = ""
    evidence_text: str = ""
    confidence: Optional[float] = None

class EntityRow(BaseModel):
    entity_name: str
    entity_type: str = ""
    attributes: Dict[str, Any] = Field(default_factory=dict)
    provenance: List[Evidence] = Field(default_factory=list)

class QueryResponse(BaseModel):
    query: str
    results: List[EntityRow]
    sources: List[SearchResult] = Field(default_factory=list)
    # Warnings
    notes: List[str] = Field(default_factory=list)