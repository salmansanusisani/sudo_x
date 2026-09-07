"""Single source of truth for what SUDO X can expose to a planner or UI."""

from dataclasses import dataclass
from typing import Literal

from sudo_x.models import Capability

Effect = Literal["read", "visualize", "plan", "mutate", "network"]


@dataclass(frozen=True)
class CapabilitySpec:
    id: str
    label: str
    description: str
    effect: Effect
    enabled: bool
    reason: str

    def public(self) -> Capability:
        return Capability(
            id=self.id,
            label=self.label,
            enabled=self.enabled,
            description=self.description,
        )


def registry(*, provider_kind: str = "not_configured") -> tuple[CapabilitySpec, ...]:
    """Return capabilities for the current process; disabled means unavailable, not denied."""
    planner_description = {
        "mock": "Deterministic non-executable planning boundary; no external request is made.",
        "nebius": (
            "Bounded Nebius/NVIDIA planning preview; prompts are disclosed before cloud inference "
            "and output cannot execute tools."
        ),
    }.get(provider_kind, "No reasoning provider is configured.")
    return (
        CapabilitySpec(
            id="system", label="Local system snapshot", effect="read", enabled=True,
            description="Explicit read-only OS, Python, CPU, load and memory snapshot.",
            reason="Available as a bounded local read.",
        ),
        CapabilitySpec(
            id="nigeria", label="Nigeria offline geography", effect="visualize", enabled=True,
            description="Fixed Abuja/Lagos map demonstration only; live news is unavailable.",
            reason="Bundled geometry and fixed coordinates only.",
        ),
        CapabilitySpec(
            id="planner", label="Structured reasoning planner", effect="plan",
            enabled=provider_kind in {"mock", "nebius"}, description=planner_description,
            reason=("Mock planner loaded." if provider_kind == "mock"
                    else (
                        "Live bounded preview loaded; no cloud tool authority is enabled."
                        if provider_kind == "nebius"
                        else "A real provider call is not enabled in this build."
                    )),
        ),
        CapabilitySpec(
            id="request", label="General assistant", effect="plan", enabled=False,
            description=(
                "Provider planning is isolated and cannot execute tools in this build."
                if provider_kind == "mock"
                else "Provider and general machine tools are not connected."
            ),
            reason=(
                "General requests remain blocked until plan validation and policy execution exist."
            ),
        ),
        CapabilitySpec(
            id="security.network_scan", label="Authorized network observation", effect="network",
            enabled=False, description="Scoped Nmap observations for enrolled assets.",
            reason="Asset authorization, egress enforcement, and parser gates are not implemented.",
        ),
        CapabilitySpec(
            id="remote.inspect", label="Enrolled remote diagnostics", effect="network",
            enabled=False,
            description="Bounded diagnostics on explicitly enrolled remote machines.",
            reason="Pinned identity and remote dispatcher gates are not implemented.",
        ),
        CapabilitySpec(
            id="code.sandbox", label="Isolated coding workspace", effect="mutate", enabled=False,
            description="Create and test code in an isolated copy.",
            reason="Sandbox executor and independent verifier gates are not implemented.",
        ),
    )


def capability_map(provider_kind: str) -> dict[str, CapabilitySpec]:
    return {item.id: item for item in registry(provider_kind=provider_kind)}
