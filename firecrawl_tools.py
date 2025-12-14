"""Firecrawl tools for web search and scraping using smolagents."""

import os
from smolagents import tool
from firecrawl import Firecrawl

_client: Firecrawl | None = None


def _get_client() -> Firecrawl:
    global _client
    if _client is None:
        api_key = os.environ.get("FIRECRAWL_API_KEY")
        if not api_key:
            raise ValueError("FIRECRAWL_API_KEY env var required")
        _client = Firecrawl(api_key=api_key)
    return _client


@tool
def search_web(query: str, limit: int = 5) -> str:
    """Search the web for information.

    Args:
        query: The search query.
        limit: Max number of results (default 5).
    """
    client = _get_client()
    results = client.search(query=query, limit=limit)

    # SearchData has .web, .news, .images attributes
    items = getattr(results, "web", None) or []
    if not items:
        return "No results found."

    output = []
    for item in items:
        title = item.title or "No title"
        url = item.url or ""
        markdown = getattr(item, "markdown", "") or ""
        if markdown:
            markdown = markdown[:500]
        description = getattr(item, "description", "") or ""
        output.append(f"## {title}\nURL: {url}\n{description}\n{markdown}\n")

    return "\n---\n".join(output)


@tool
def scrape_url(url: str) -> str:
    """Scrape a webpage and return its content as markdown.

    Args:
        url: The URL to scrape.
    """
    client = _get_client()
    result = client.scrape_url(url=url, formats=["markdown"])

    if not result or not result.markdown:
        return f"Failed to scrape {url}"

    content = result.markdown
    if len(content) > 10000:
        content = content[:10000] + "\n\n[Content truncated...]"

    return content
