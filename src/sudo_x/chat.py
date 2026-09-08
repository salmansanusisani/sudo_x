"""Bounded conversational Nebius boundary with no tools or machine context."""

import os
from dataclasses import dataclass

import httpx
from pydantic import BaseModel, ConfigDict, Field

CHAT_TIMEOUT_SECONDS = 15
CHAT_MAX_TOKENS = 512
CHAT_MAX_RESPONSE_BYTES = 32768


class ChatInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    message: str = Field(min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    model: str
    message: str = Field(min_length=1, max_length=8000)
    cloud_disclosure: dict[str, str]
    execution: str = "unavailable"


@dataclass(frozen=True)
class NebiusChat:
    model: str
    base_url: str
    api_key: str
    client_factory: object = httpx.Client

    def respond(self, message: str) -> ChatResponse:
        if not self.api_key.strip():
            raise ValueError("Nebius chat is not configured for this session.")
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are SUDO X in conversation mode. Answer the user's message helpfully "
                        "and concisely. You have no tools, no shell, no files, no machine access, "
                        "and no live task execution. Never claim you performed an action. Do not "
                        "invent current facts. If the user asks for an action, explain that you "
                        "can discuss or preview it but cannot execute it. Do not reveal private "
                        "reasoning."
                    ),
                },
                {"role": "user", "content": message},
            ],
            "max_completion_tokens": CHAT_MAX_TOKENS,
            "temperature": 0.4,
            "stream": False,
            "n": 1,
            "store": False,
        }
        try:
            with self.client_factory(
                timeout=CHAT_TIMEOUT_SECONDS, follow_redirects=False, trust_env=False
            ) as client:
                response = client.post(
                    f"{self.base_url.rstrip('/')}/chat/completions",
                    json=payload,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                )
            if response.status_code != 200 or len(response.content) > CHAT_MAX_RESPONSE_BYTES:
                raise ValueError("Nebius chat request failed or exceeded its response limit.")
            body = response.json()
            choices = body["choices"]
            if len(choices) != 1 or choices[0]["finish_reason"] != "stop":
                raise ValueError("Nebius chat did not return one complete response.")
            assistant = choices[0]["message"]
            if assistant.get("tool_calls") or assistant.get("function_call"):
                raise ValueError("Tools are unavailable in conversation mode.")
            result = ChatResponse(
                model=self.model,
                message=assistant["content"],
                cloud_disclosure={
                    "provider": "Nebius Token Factory",
                    "data_handling": (
                        "Your conversation message was sent to Nebius. No machine data, files, "
                        "task history, screen data, or tools were included."
                    ),
                },
            )
            return result
        except (httpx.HTTPError, TimeoutError, ValueError, KeyError, IndexError, TypeError) as exc:
            raise ValueError("Nebius chat failed validation or timed out.") from exc


def chat_from_environment(model: str, base_url: str) -> NebiusChat | None:
    key = os.environ.get("NEBIUS_API_KEY", "").strip()
    return NebiusChat(model, base_url, key) if key else None
