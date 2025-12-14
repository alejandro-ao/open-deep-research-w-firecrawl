"""Firecrawl tools for web search and scraping using OpenAI Agents SDK."""

import os
from agents import function_tool
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


@function_tool
def search_web(query: str, limit: int = 5) -> str:
    """Search the web for information.

    Args:
        query: The search query.
        limit: Max number of results (default 5).
    """
    client = _get_client()
    results = client.search(query=query, limit=limit)

    if not results:
        return "No results found."

    items = results.web if hasattr(results, "web") and results.web else None

    if not items:
        return "No results found."

    output = []
    for item in items:
        # Handle both object and dict access
        if isinstance(item, dict):
            title = item.get("title", "No title")
            url = item.get("url", "")
            markdown = item.get("markdown", "")[:500] if item.get("markdown") else ""
            description = item.get("description", "")
        else:
            title = getattr(item, "title", "No title") or "No title"
            url = getattr(item, "url", "") or ""
            markdown = getattr(item, "markdown", "") or ""
            if markdown:
                markdown = markdown[:500]
            description = getattr(item, "description", "") or ""
        output.append(f"## {title}\nURL: {url}\n{description}\n{markdown}\n")

    return "\n---\n".join(output)


@function_tool
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
