from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

Kind = Literal["system", "nigeria", "request"]
Status = Literal["queued", "running", "completed", "blocked", "cancelled", "failed"]
Phase = Literal["observe", "plan", "act", "verify", "complete", "blocked"]
TERMINAL = frozenset({"completed", "blocked", "cancelled", "failed"})


class TaskInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    prompt: str = Field(min_length=1, max_length=2000)
    kind: Kind


class Event(BaseModel):
    sequence: int
    timestamp: str
    phase: Phase
    message: str


class Task(BaseModel):
    id: str
    prompt: str
    kind: Kind
    status: Status
    created_at: str
    updated_at: str
    summary: str
    events: list[Event]
    scene: Literal["system", "map", "overview"]
    result: dict[str, Any] | None = None


class TaskList(BaseModel):
    tasks: list[Task]


class Capability(BaseModel):
    id: str
    label: str
    enabled: bool
    description: str


class BackendStatus(BaseModel):
    mode: Literal["local"] = "local"
    provider: Literal["not_configured", "mock", "nebius"] = "not_configured"
    provider_model: str | None = None
    provider_ready: bool = False
    version: str = "0.1.0"
    capabilities: list[Capability]


class APIError(Exception):
    def __init__(self, status: int, code: str, message: str):
        self.status = status
        self.code = code
        self.message = message
