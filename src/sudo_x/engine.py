import asyncio
import math
import os
import platform
from pathlib import Path

from sudo_x.models import TERMINAL, APIError, Phase, Task, TaskInput
from sudo_x.store import MAX_ACTIVE_TASKS, Store, now


def system_snapshot() -> dict:
    """Only explicit system tasks call this narrow, read-only local adapter."""
    memory = {"total_bytes": None, "available_bytes": None}
    try:
        with Path("/proc/meminfo").open(encoding="ascii") as source:
            lines = source.read(65536).splitlines()
        for line in lines:
            fields = line.split()
            key = {"MemTotal:": "total_bytes", "MemAvailable:": "available_bytes"}.get(fields[0])
            if key and len(fields) == 3 and fields[2] == "kB":
                value = int(fields[1])
                if value >= 0:
                    memory[key] = value * 1024
    except (OSError, ValueError, UnicodeError, IndexError):
        pass
    try:
        load = list(os.getloadavg())
    except (OSError, AttributeError):
        load = None
    return {
        "sampled_at": now(),
        "os": platform.system(),
        "kernel": platform.release(),
        "python": platform.python_version(),
        "logical_cpu_count": os.cpu_count(),
        "load_average": load,
        "memory": memory,
    }


class Engine:
    def __init__(self, store: Store):
        self.store = store
        self.queue: asyncio.Queue[str] = asyncio.Queue(maxsize=MAX_ACTIVE_TASKS)
        self.worker: asyncio.Task | None = None

    def start(self) -> None:
        self.store.interrupt("Interrupted by a previous shutdown; not resumed or retried.")
        self.worker = asyncio.create_task(self._work(), name="sudo-x-local-worker")

    async def stop(self) -> None:
        if self.worker is not None:
            self.worker.cancel()
            await asyncio.gather(self.worker, return_exceptions=True)
        self.store.interrupt("Interrupted by shutdown; no further steps were executed.")

    def submit(self, task_input: TaskInput) -> Task:
        if self.queue.full():
            raise APIError(429, "queue_full", "The bounded local queue is full; try again later.")
        task = self.store.create(task_input)
        self.queue.put_nowait(task.id)
        return task

    def cancel(self, task_id: str) -> Task:
        if not self.store.advance(
            task_id, "blocked", "Cancelled by user; no further steps will run.", status="cancelled"
        ):
            raise APIError(409, "task_terminal", "A terminal task cannot be cancelled.")
        return self.store.get(task_id)

    async def _step(self, task_id: str, phase: Phase, message: str, **kwargs) -> bool:
        # Cooperative checkpoints allow cancellation/polling without staged progress delays.
        await asyncio.sleep(0)
        return self.store.advance(task_id, phase, message, **kwargs)

    async def _work(self) -> None:
        while True:
            task_id = await self.queue.get()
            try:
                async with asyncio.timeout(10):
                    await self._run(task_id)
            except Exception:
                # Never expose exception text, local paths, prompts or credentials in API errors.
                self.store.advance(
                    task_id, "blocked", "Local task failed; no successful outcome is claimed.",
                    status="failed",
                )
            finally:
                self.queue.task_done()

    async def _run(self, task_id: str) -> None:
        task = self.store.get(task_id)
        if task.status in TERMINAL:
            return
        if task.kind == "request":
            if not await self._step(
                task_id, "observe", "This request needs capabilities beyond the local demo."
            ):
                return
            await self._step(
                task_id, "blocked",
                "Provider and general machine tools are not connected. "
                "No shell commands, file searches, or external actions were performed.",
                status="blocked",
            )
            return
        if task.kind == "nigeria":
            if not await self._step(
                task_id, "observe", "Nigeria selected; no live news provider is connected."
            ):
                return
            if not await self._step(
                task_id, "plan", "Show only a fixed offline geography demonstration, not news."
            ):
                return
            result = {
                "label": "Nigeria", "mode": "offline_geography",
                "cities": [
                    {"name": "Abuja", "lat": 9.0765, "lon": 7.3986},
                    {"name": "Lagos", "lat": 6.5244, "lon": 3.3792},
                ],
                "news_available": False,
            }
            if not await self._step(
                task_id, "act",
                "Loaded fixed Abuja and Lagos coordinates; no network request made.",
                result=result,
            ):
                return
            await self._step(
                task_id, "blocked",
                "Offline geography demonstration only. Live news provider not connected; "
                "the news request is not fulfilled.", status="blocked", result=result,
            )
            return
        if not await self._step(
            task_id, "observe",
            "Explicit system snapshot selected; hostname and files are excluded."
        ):
            return
        if not await self._step(
            task_id, "plan", "Read OS, kernel, Python, CPU, load and /proc/meminfo only."
        ):
            return
        # No await between this terminal-state check and the synchronous read-only adapter.
        if self.store.get(task_id).status in TERMINAL:
            return
        result = system_snapshot()
        if not await self._step(
            task_id, "act", "Sampled local system metrics; no commands or modifications performed.",
            result=result,
        ):
            return
        cpu, load, memory = result["logical_cpu_count"], result["load_average"], result["memory"]
        if cpu is not None and cpu < 1:
            raise ValueError("Invalid CPU count")
        if load is not None and (
            len(load) != 3 or any(not math.isfinite(x) or x < 0 for x in load)
        ):
            raise ValueError("Invalid load averages")
        total, available = memory["total_bytes"], memory["available_bytes"]
        if total is not None and available is not None and available > total:
            raise ValueError("Invalid memory counters")
        missing = cpu is None or load is None or total is None or available is None
        if not await self._step(
            task_id, "verify",
            "Checked returned CPU, load and memory counter ranges. "
            "Unavailable counters remain null; this is not a machine health test.",
        ):
            return
        summary = "Read-only local system snapshot collected. No system changes made."
        if missing:
            summary += " Some counters were unavailable and are reported as null."
        await self._step(task_id, "complete", summary, status="completed", result=result)
