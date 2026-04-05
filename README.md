# Agentic Search


This project is an agentic web search system that uses web search APIs to find relevant pages. It fetches and parses those pages into text and calls an LLM to extract structured entities. It also deduplicates entities across pages and attaches provenance (source URLs, evidences, etc.) and exposes everything via a FastAPI backend and Streamlit UI.


It basically has two modes- local and main. Local mode is designed for development stage and testing purposes at a smaller range initially. The main mode uses Brave Search API and OpenAI for high quality results and real-world behaviour.


## Tech Stack


- FastAPI: It is a modern async python web framework with automatice OpenAPI docs at /docs.
- Uvicorn: It is an ASGI server for running FastAPI and it supports async I/O and dev reloads.
- Streamlit: It is a lightweight UI layer for interactive querying and visualizing the retrieved results.
- Brave Search API: It is an AI-oriented web search with global results and it is a simple JSON API.
- DuckDuckGo: It is a keyless search option used in development stage so that the project can run without any external API keys.
- OpenAI (gpt-4o-mini): It is a strong but smaller model with good support for JSON-style structured outputs which is used for reliable extraction.
- Ollama: It is a local LLM runtime used so that the full pipeline can run without network dependencies inspired by common local-agent setups.
- Pydantic / pydantic‑settings: It is a strong typing and validation for entities, responses, and configuration. Schema- LLMEntity, LLMExtraction, QueryResponse
- httpx / requests: HTTP clients for Brave search and page fetching; httpx used in async contexts.


## Project Structure:


```text
agentic-search-challenge/
  app/
    __init__.py
    main.py           # FastAPI app and /search endpoint
    config.py         # Settings (env → Settings class)
    search.py         # DuckDuckGo + Brave search clients
    fetch.py          # Async page fetcher returning {url, text}
    extract.py        # Ollama + OpenAI clients and extraction logic
    pipeline.py       # End-to-end flow (search → fetch → extract → dedupe)
    schemas.py        # Pydantic models: QueryResponse, EntityRow, Evidence, LLMEntity
    utils.py          # dedupe_entities and helper utilities
  ui/
    app.py            # Streamlit UI
  tests/
    test_pipeline.py  # Unit test for dedupe_entities
  .env.example        # Example config
  requirements.txt
  README.md
```



## Instructions to run


1. Clone the repo and install the requirements using


```bash
pip install -r requirements.txt
```


2. Configure environment


Copy the example env file:


```bash
cp .env.example .env
```


And then edit .env file and add your Brave Search API key "BRAVE_API_KEY" and OpenAI key "OPENAI_API_KEY"


3. Running the system


i. From the project root, open the terminal and run:


```bash
uvicorn app.main:app --reload
```



OpenAPI docs are at:


[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)



ii. The code can be run in two ways


Open the above link and you should be able to see a search engine. Click on 'Try it out' button and enter the query in the text field provided. Click on 'Execute' button.


You should be able to view the results in the response body.


Or to run on Streamlit,


In a different terminal, run:


```bash
streamlit run ui/app.py
```


Your browser opens up and you should be able to see the frontend page with a text field and search button.


Enter your query and hit search.


The response typically looks like this:


    sources – the top search results (from Brave or DuckDuckGo).


    results – deduped, structured entities with attributes and provenance.


    notes – log of skipped or failed pages (e.g., paywalled, rate limits, etc.).



## Behavior and Approach


End-to-end flow
1. Search (search_web)


In local mode: uses DuckDuckGo’s keyless API.


In main mode: calls Brave Search API at [https://api.search.brave.com/res/v1/web/search](https://api.search.brave.com/res/v1/web/search) with Subscription-Token.


2. Fetch (fetch_page)


Uses httpx.AsyncClient with appropriate headers and timeouts.


Follows redirects and returns a dict: {"url": ..., "text": ...}.


On 400/500 or network errors, returns empty text rather than crashing the pipeline.


3. Extract (extract_entities)


MODE=local: extract_with_ollama calls a local Ollama model configured for JSON output.


MODE=main: extract_with_openai calls OpenAI gpt-4o-mini via the Responses API with a JSON schema‑style prompt.


Both produce LLMExtraction with a list of LLMEntity objects:


```python
class LLMEntity(BaseModel):
    entity_name: str
    entity_type: str
    attributes: Dict[str, Any]
    evidence: str
    source_url: str
    confidence: Optional[float]
```


4. Dedupe (dedupe_entities)


Normalizes entity names and merges attributes/provenance when two entities are the same (e.g., “Apollo Health” vs “apollo health”) so you don’t see duplicates from multiple pages.


5. Response (run_pipeline)


Orchestrates the steps above, builds a QueryResponse, and returns it through /search.



This is not a full knowledge base, but it is accurate enough to support quick research or as a first step before deeper human review. The provenance fields (URL, title, short evidence snippet, and confidence) make it easy to manually verify any entity and attribute.


## Latency and cost


Each query triggers:


One Brave Search API call + up to MAX_PAGES page fetches.


Up to MAX_PAGES OpenAI calls.


With MAX_PAGES=2–3, latency is a few seconds per query and affordable under typical gpt-4o-mini; this is acceptable for user‑facing tools or dashboards, and can be further tuned.


## Design choices


1. Search provider choice


Brave Search API explicitly supports AI agents and offers a simple token‑based API with clear pricing and ongoing support.



2. Simpler fetching vs heavy scraping


Full scraping frameworks add complexity and often fail on modern web anti‑bot setups. So a minimal async fetcher is used which uses a custom User‑Agent, follows redirects and returns empty text instead of raising on errors.



3. Structured outputs
LLM outputs are free‑form, but the pipeline needs stable structured entities. So Pydantic schemas are used for LLMEntity and LLMExtraction, and JSON parsing logic that handles markdown fences (```json) and guards against parse errors with fallbacks.


## Limitations


- Rate limits: OpenAI and Brave both have rate limits; MAX_PAGES should be kept modest on low‑tier accounts. Rate limit errors are captured in notes.


- Partial coverage: Some sites (paywalled, highly dynamic or heavily protected) may return little or no usable text.


- Extraction quality: While generally good, the LLM can miss entities or mislabel things. Provenance is included so we can double‑check.


- No persistent storage: This prototype doesn’t cache search results or entities so every query is fresh.



## Conclusion


This project implements a multi‑step agentic pipeline (search → retrieval → LLM extraction → dedupe → provenance) instead of just prompting an LLM with a single search result. 


It provides a clean programmatic API (/search) for integration and a UI suitable for non‑technical users or quick evaluations.


## Future work 


- Adding more search APIs (SerpAPI, Tavily, OpenRouter search tools). 


- Adding caching layers or persistence for entities.


- Experimenting with richer entity schemas (events, relationships) or more powerful models.

## Sample Outputs

<img width="912" height="1080" alt="image" src="https://github.com/user-attachments/assets/aafae1f8-b6d3-4559-abe3-29a0aa2c3b55" />

<img width="901" height="1080" alt="image" src="https://github.com/user-attachments/assets/d818ca57-09c9-4e51-bb9b-81b0f3f7276f" />

<img width="871" height="1080" alt="image" src="https://github.com/user-attachments/assets/32bdbca9-7ae1-46ff-bed4-ad5fd82a776b" />



