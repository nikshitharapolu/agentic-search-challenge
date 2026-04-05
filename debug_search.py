import asyncio
from app.search import search_web
from app.config import settings

async def main():
    for query in ["python", "linux"]:
        results = await search_web(query)
        print("\nMODE:", settings.mode, "| Query:", query)
        print("Results from search_web:", len(results))
        for r in results:
            print("-", r["title"], "->", r["url"])

if __name__ == "__main__":
    asyncio.run(main())