"""Bounded public-source research boundary for SUDO X."""

import os
from dataclasses import dataclass
from datetime import UTC, datetime

import httpx
from pydantic import BaseModel, ConfigDict, Field, HttpUrl

TAVILY_ENDPOINT = "https://api.tavily.com/search"
NIGERIA_QUERY = "Nigeria latest news today government economy security public sources"
MAX_RESULTS = 5
TIMEOUT_SECONDS = 10
MAX_RESPONSE_BYTES = 65536


class ResearchSource(BaseModel):
    model_config = ConfigDict(extra="ignore")

    title: str = Field(min_length=1, max_length=300)
    url: HttpUrl
    content: str = Field(default="", max_length=2000)
    published_date: str | None = Field(default=None, max_length=80)


class ResearchResult(BaseModel):
    query: str
    fetched_at: str
    answer: str | None = Field(default=None, max_length=4000)
    sources: list[ResearchSource] = Field(max_length=MAX_RESULTS)
    cloud_disclosure: dict[str, str]


@dataclass(frozen=True)
class TavilyResearch:
    api_key: str
    client_factory: object = httpx.Client

    def search_nigeria(self) -> ResearchResult:
        if not self.api_key.strip():
            raise ValueError("Tavily research is not configured for this session.")
        payload = {
            "api_key": self.api_key,
            "query": NIGERIA_QUERY,
            "topic": "news",
            "search_depth": "basic",
            "max_results": MAX_RESULTS,
            "include_answer": "advanced",
            "include_raw_content": False,
            "include_images": False,
        }
        try:
            with self.client_factory(
                timeout=TIMEOUT_SECONDS, follow_redirects=False, trust_env=False
            ) as client:
                response = client.post(TAVILY_ENDPOINT, json=payload)
            if response.status_code != 200:
                raise ValueError("Tavily rejected the research request.")
            if len(response.content) > MAX_RESPONSE_BYTES:
                raise ValueError("Tavily research response exceeded the allowed size.")
            body = response.json()
            sources = [ResearchSource.model_validate(item) for item in body.get("results", [])]
            return ResearchResult(
                query=NIGERIA_QUERY,
                fetched_at=datetime.now(UTC).isoformat(),
                answer=body.get("answer"),
                sources=sources,
                cloud_disclosure={
                    "provider": "Tavily",
                    "data_handling": (
                        "A fixed Nigeria news query was sent to Tavily; no local data was included."
                    ),
                },
            )
        except (httpx.HTTPError, TimeoutError, ValueError, TypeError, KeyError) as exc:
            raise ValueError("Tavily research failed validation or timed out.") from exc


def tavily_from_environment() -> TavilyResearch | None:
    key = os.environ.get("TAVILY_API_KEY", "").strip()
    return TavilyResearch(key) if key else None
