"""Provider boundary: model access is explicit, typed, and disabled by default."""

import os
from dataclasses import dataclass
from typing import Literal, Protocol

import httpx
from pydantic import BaseModel, ConfigDict, Field, field_validator

from sudo_x.models import CloudDisclosure

ProviderKind = Literal["not_configured", "mock", "nebius"]
PlanAction = Literal["blocked", "propose"]


class PlanEnvelope(BaseModel):
    """Validated data from a planner; it has no execution method by design."""

    model_config = ConfigDict(extra="forbid", strict=True)

    version: Literal["1"] = "1"
    capability_id: str = Field(min_length=1, max_length=80, pattern=r"^[a-z][a-z0-9._-]*$")
    action: PlanAction
    arguments: dict[str, str | int | float | bool | list[str]] = Field(default_factory=dict)
    rationale: str = Field(min_length=1, max_length=500)

    @field_validator("arguments")
    @classmethod
    def reject_execution_fields(cls, value):
        forbidden = {"command", "argv", "shell", "exec", "script", "target", "url"}
        if forbidden.intersection(value):
            raise ValueError("Execution or destination fields are not accepted by a plan envelope.")
        return value


@dataclass(frozen=True)
class ProviderConfig:
    kind: ProviderKind
    model: str | None = None
    base_url: str | None = None
    timeout_seconds: float = 5.0
    max_tokens: int = 256


@dataclass(frozen=True)
class Budget:
    timeout_seconds: float
    max_tokens: int


@dataclass(frozen=True)
class ProviderPlan:
    """A model proposal. It is data only; it cannot execute a tool."""

    provider: ProviderKind
    model: str | None
    action: Literal["blocked", "answer"]
    message: str
    envelope: PlanEnvelope | None = None
    cloud_disclosure: CloudDisclosure | None = None


class Planner(Protocol):
    def plan(self, prompt: str) -> ProviderPlan:
        """Return a non-executable proposal for a validated prompt."""


def provider_config(environ: dict[str, str] | None = None) -> ProviderConfig:
    """Read non-secret provider selection without returning or logging credentials."""
    values = os.environ if environ is None else environ
    kind = values.get("SUDOX_PROVIDER", "not_configured").strip().lower()
    if kind not in {"not_configured", "mock", "nebius"}:
        raise ValueError("SUDOX_PROVIDER must be not_configured, mock, or nebius.")
    if kind == "not_configured":
        return ProviderConfig(kind="not_configured")
    if kind == "mock":
        return ProviderConfig(kind="mock", model="sudo-x/mock-planner")

    model = values.get("SUDOX_MODEL_PRIMARY", "").strip()
    base_url = values.get("NEBIUS_BASE_URL", "https://api.tokenfactory.nebius.com/v1/").strip()
    if not model:
        raise ValueError("SUDOX_MODEL_PRIMARY is required when SUDOX_PROVIDER=nebius.")
    if not base_url.startswith("https://"):
        raise ValueError("NEBIUS_BASE_URL must use HTTPS.")
    if not values.get("NEBIUS_API_KEY", "").strip():
        raise ValueError("NEBIUS_API_KEY is required when SUDOX_PROVIDER=nebius.")
    try:
        timeout_seconds = float(values.get("SUDOX_PROVIDER_TIMEOUT_SECONDS", "5"))
        max_tokens = int(values.get("SUDOX_PROVIDER_MAX_TOKENS", "256"))
    except ValueError as exc:
        raise ValueError("Provider timeout and token budgets must be numeric.") from exc
    if not 0.1 <= timeout_seconds <= 30:
        raise ValueError("SUDOX_PROVIDER_TIMEOUT_SECONDS must be between 0.1 and 30.")
    if not 1 <= max_tokens <= 4096:
        raise ValueError("SUDOX_PROVIDER_MAX_TOKENS must be between 1 and 4096.")
    return ProviderConfig(
        kind="nebius", model=model, base_url=base_url,
        timeout_seconds=timeout_seconds, max_tokens=max_tokens,
    )


class MockPlanner:
    """A deterministic test double; deliberately has no tools or network access."""

    def __init__(self, config: ProviderConfig):
        if config.kind != "mock":
            raise ValueError("MockPlanner requires mock provider configuration.")
        self.config = config

    def plan(self, prompt: str) -> ProviderPlan:
        if not prompt.strip():
            raise ValueError("A planner prompt cannot be blank.")
        return ProviderPlan(
            provider="mock",
            model=self.config.model,
            action="blocked",
            message=(
                "Mock provider received the request but cannot execute tools or access the "
                "machine. No external request was made."
            ),
            envelope=PlanEnvelope(
                capability_id="request",
                action="blocked",
                rationale="Mock provider cannot execute.",
            ),
        )


class NebiusPlanner:
    """Bounded real planner; model output remains validated data without tools."""

    def __init__(self, config: ProviderConfig, client_factory=None):
        if config.kind != "nebius" or not config.model or not config.base_url:
            raise ValueError("NebiusPlanner requires complete Nebius configuration.")
        self.config = config
        self.budget = Budget(config.timeout_seconds, config.max_tokens)
        self.client_factory = client_factory or httpx.Client

    def plan(self, prompt: str) -> ProviderPlan:
        if not prompt.strip():
            raise ValueError("A planner prompt cannot be blank.")
        payload = {
            "model": self.config.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        'You are a planning component, not an executor. Return only compact JSON '
                        'matching this exact shape: {"version":"1","capability_id":"system",'
                        '"action":"propose","arguments":{},"rationale":"..."}. The version '
                        'must be the string "1", not the number 1. Never include command, argv, '
                        'shell, exec, script, target, url, or tool calls. Do not include private '
                        "reasoning."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "max_completion_tokens": self.budget.max_tokens,
            "temperature": 0,
            "stream": False,
            "n": 1,
            "store": False,
        }
        try:
            with self.client_factory(
                timeout=self.budget.timeout_seconds, follow_redirects=False, trust_env=False
            ) as client:
                response = client.post(
                    f"{self.config.base_url.rstrip('/')}/chat/completions",
                    json=payload,
                    headers={"Authorization": f"Bearer {os.environ['NEBIUS_API_KEY']}"},
                )
            if response.status_code != 200:
                raise ValueError("Nebius rejected the planner preview.")
            if len(response.content) > 32768:
                raise ValueError("Nebius planner response exceeded the allowed size.")
            body = response.json()
            if body.get("model") != self.config.model:
                raise ValueError("Nebius returned an unexpected planner model.")
            choices = body["choices"]
            if len(choices) != 1 or choices[0]["finish_reason"] != "stop":
                raise ValueError("Nebius did not return one complete planner response.")
            message = choices[0]["message"]
            if message.get("tool_calls") or message.get("function_call"):
                raise ValueError("Tool calls are not accepted by the planner preview.")
            envelope = PlanEnvelope.model_validate_json(message["content"])
        except (httpx.HTTPError, TimeoutError, ValueError, KeyError, IndexError, TypeError) as exc:
            raise ValueError("Nebius planner preview failed validation or timed out.") from exc
        return ProviderPlan(
            provider="nebius", model=self.config.model, action="answer",
            message=(
                "Nebius returned a validated non-executable plan. No tool, file, network, "
                "or machine action was performed."
            ),
            envelope=envelope,
            cloud_disclosure=CloudDisclosure(
                provider="Nebius Token Factory",
                model=self.config.model,
                base_url=self.config.base_url,
                data_handling=(
                    "This planner prompt was sent to Nebius. No machine snapshot, files, task "
                    "history, screen data, or API key was included."
                ),
            ),
        )


def planner_for(config: ProviderConfig) -> Planner | None:
    if config.kind == "mock":
        return MockPlanner(config)
    if config.kind == "nebius":
        return NebiusPlanner(config)
    return None
