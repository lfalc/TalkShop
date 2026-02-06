import os
import requests
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()


def search_you_com(
        query: str,
        api_key: str | None = None,
        count: int = 50,
        language: str = "EN",
        offset: int = 0
) -> Dict[str, Any]:
    """
    Simple search via You.com search API.

    Args:
        query: Search query string
        api_key: Your You.com API key (falls back to YOU_API_KEY env var)
        count: Number of results to return (max 50)
        language: Language code (default: EN)
        offset: Pagination offset (default: 0)

    Returns:
        Dictionary containing search results
    """
    api_key = api_key or os.getenv("YOU_API_KEY")
    if not api_key:
        raise ValueError("YOU_API_KEY not set. Pass it directly or add it to .env")

    url = "https://ydc-index.io/v1/search"

    params = {
        "query": query,
        "count": min(count, 50),
        "language": language,
        "offset": offset
    }

    headers = {
        "Accept": "application/json",
        "X-API-Key": api_key
    }

    response = requests.get(url, params=params, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()


def advanced_search_you_com(
        query: str,
        api_key: str | None = None,
        agent: str = "advanced",
        stream: bool = False,
        tools: list[dict] | None = None,
        verbosity: str = "medium",
        max_workflow_steps: int = 5,
) -> Dict[str, Any]:
    """
    Advanced agent search via You.com agents API.

    Args:
        query: Input prompt for the agent
        api_key: Your You.com API key (falls back to YOU_API_KEY env var)
        agent: Agent type (default: "advanced")
        stream: Whether to stream the response
        tools: List of tools (default: research + compute)
        verbosity: Response verbosity level
        max_workflow_steps: Max workflow steps for the agent

    Returns:
        Dictionary containing agent response
    """
    api_key = api_key or os.getenv("YOU_API_KEY")
    if not api_key:
        raise ValueError("YOU_API_KEY not set. Pass it directly or add it to .env")

    url = "https://api.you.com/v1/agents/runs"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "agent": agent,
        "input": query,
        "stream": stream,
        "tools": tools or [{"type": "research"}, {"type": "compute"}],
        "verbosity": verbosity,
        "workflow_config": {"max_workflow_steps": max_workflow_steps},
    }

    response = requests.post(url, headers=headers, json=payload, timeout=120)
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    print("=== Simple Search ===")
    results = search_you_com("shoe size 10 men nike", count=10)
    for idx, hit in enumerate(results.get("results", {}).get("web", [])[:5], 1):
        print(f"{idx}. {hit.get('title', 'N/A')}")
        print(f"   {hit.get('url', 'N/A')}\n")
