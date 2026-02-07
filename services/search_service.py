from __future__ import annotations

import os
import requests
from typing import Any


class SearchService:
    SEARCH_URL = "https://ydc-index.io/v1/search"
    AGENT_URL = "https://api.you.com/v1/agents/runs"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("YOU_API_KEY")
        if not self.api_key:
            raise ValueError("YOU_API_KEY not set. Pass it directly or add it to .env")

    def search(
        self,
        query: str,
        count: int = 50,
        language: str = "EN",
        offset: int = 0,
    ) -> dict[str, Any]:
        """Simple search via You.com search API."""
        params = {
            "query": query,
            "count": min(count, 50),
            "language": language,
            "offset": offset,
        }
        headers = {
            "Accept": "application/json",
            "X-API-Key": self.api_key,
        }
        response = requests.get(self.SEARCH_URL, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()

    def advanced_search(
        self,
        query: str,
        agent: str = "advanced",
        stream: bool = False,
        tools: list[dict] | None = None,
        verbosity: str = "medium",
        max_workflow_steps: int = 5,
    ) -> dict[str, Any]:
        """Advanced agent search via You.com agents API."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
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
        response = requests.post(self.AGENT_URL, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        return response.json()
