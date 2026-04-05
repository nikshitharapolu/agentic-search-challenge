from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Mode: "local" uses DuckDuckGo + Ollama -for free development and testing purposes
    # "main" uses Brave + OpenAI for better quality results
    mode: str = "main"
    ollama_base_url: str = "http://localhost:11434/v1"
    ollama_model: str = "llama3.2"

    brave_api_key: str = ""
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"

    top_k: int = 5
    max_pages: int = 5
    timeout_seconds: int = 20
    user_agent: str = "AgenticSearchBot/1.0"
    api_url: str = "http://localhost:8000"

    class Config:
        env_file = ".env"
        extra = "ignore"
settings = Settings()