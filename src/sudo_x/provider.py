"""Provider boundary: model access is explicit, typed, and disabled by default."""

import os
import time
from dataclasses import dataclass
from typing import Literal, Protocol

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
    """Offline synthetic transport for the Nebius/NVIDIA provider boundary."""

    def __init__(self, config: ProviderConfig):
        if config.kind != "nebius" or not config.model or not config.base_url:
            raise ValueError("NebiusPlanner requires complete Nebius configuration.")
        self.config = config
        self.budget = Budget(config.timeout_seconds, config.max_tokens)

    def plan(self, prompt: str) -> ProviderPlan:
        if not prompt.strip():
            raise ValueError("A planner prompt cannot be blank.")
        started = time.monotonic()
        if time.monotonic() - started > self.budget.timeout_seconds:
            return self._blocked("Synthetic provider budget expired before planning.")

        # This is deliberately local and deterministic. It proves the typed boundary
        # without creating an outbound request or granting tool authority.
        envelope = PlanEnvelope(
            capability_id="request",
            action="propose",
            arguments={"prompt_length": len(prompt), "max_tokens": self.budget.max_tokens},
            rationale="Synthetic Nebius/NVIDIA probe returned a typed non-executable proposal.",
        )
        return ProviderPlan(
            provider="nebius",
            model=self.config.model,
            action="answer",
            message=(
                "Synthetic Nebius/NVIDIA transport completed locally. No external request was "
                "made and no tool, file, network, or machine action is available."
            ),
            envelope=envelope,
            cloud_disclosure=CloudDisclosure(
                provider="Nebius synthetic transport",
                model=self.config.model,
                base_url=self.config.base_url,
                data_handling="Synthetic local probe only; prompt was not sent to a cloud service.",
            ),
        )

    def _blocked(self, message: str) -> ProviderPlan:
        return ProviderPlan(
            provider="nebius", model=self.config.model, action="blocked", message=message,
            envelope=PlanEnvelope(
                capability_id="request", action="blocked", rationale="Provider budget was exceeded."
            ),
            cloud_disclosure=CloudDisclosure(
                provider="Nebius synthetic transport", model=self.config.model,
                base_url=self.config.base_url,
                data_handling=(
                    "No prompt data was sent because the local budget gate blocked the probe."
                ),
            ),
        )


def planner_for(config: ProviderConfig) -> Planner | None:
    if config.kind == "mock":
        return MockPlanner(config)
    if config.kind == "nebius":
        return NebiusPlanner(config)
    return None
