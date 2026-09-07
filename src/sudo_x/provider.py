"""Provider boundary: model access is explicit, typed, and disabled by default."""

import os
from dataclasses import dataclass
from typing import Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field, field_validator

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


@dataclass(frozen=True)
class ProviderPlan:
    """A model proposal. It is data only; it cannot execute a tool."""

    provider: ProviderKind
    model: str | None
    action: Literal["blocked", "answer"]
    message: str
    envelope: PlanEnvelope | None = None


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
    return ProviderConfig(kind="nebius", model=model, base_url=base_url)


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


def planner_for(config: ProviderConfig) -> Planner | None:
    if config.kind == "mock":
        return MockPlanner(config)
    # The Nebius transport is intentionally a later, separately approved milestone.
    return None
