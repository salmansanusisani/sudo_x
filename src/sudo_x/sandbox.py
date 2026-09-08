"""Linux coding sandbox: isolated project copy, fixed tests, no host mutation."""

import difflib
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

MAX_FILES = 32
MAX_FILE_BYTES = 128 * 1024
MAX_TOTAL_BYTES = 2 * 1024 * 1024
TIMEOUT_SECONDS = 60
EXCLUDED = {".git", ".venv", "node_modules", "dist", "__pycache__", ".pytest_cache"}


class SandboxInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    files: dict[str, str] = Field(default_factory=dict, max_length=MAX_FILES)


class SandboxResult(BaseModel):
    status: str
    diff: str
    tests: str
    changed_files: list[str]
    original_unchanged: bool
    network: str = "disabled"
    credentials: str = "not mounted"


def _safe_path(name: str) -> Path:
    path = Path(name)
    if (
        not name or path.is_absolute() or "\\" in name
        or any(part in {"", ".", ".."} for part in path.parts)
    ):
        raise ValueError("Sandbox file paths must be relative and cannot contain dot segments.")
    if path.parts[0] in EXCLUDED or any(part.startswith(".") for part in path.parts):
        raise ValueError("Sandbox cannot modify hidden, dependency, or credential paths.")
    return path


@dataclass(frozen=True)
class Sandbox:
    project: Path

    def run(self, request: SandboxInput) -> SandboxResult:
        if os.name != "posix" or shutil.which("bwrap") is None:
            raise ValueError("Isolated Linux sandbox is unavailable; no host fallback is allowed.")
        total = 0
        safe_files: dict[Path, str] = {}
        for name, content in request.files.items():
            path = _safe_path(name)
            size = len(content.encode())
            if size > MAX_FILE_BYTES:
                raise ValueError("Sandbox file exceeds the per-file size limit.")
            total += size
            safe_files[path] = content
        if total > MAX_TOTAL_BYTES:
            raise ValueError("Sandbox files exceed the total size limit.")
        with tempfile.TemporaryDirectory(prefix="sudo-x-sandbox-") as directory:
            copy = Path(directory) / "project"
            shutil.copytree(self.project, copy, ignore=shutil.ignore_patterns(*EXCLUDED))
            originals: dict[Path, str] = {}
            for path, content in safe_files.items():
                target = copy / path
                if target.exists() and not target.is_file():
                    raise ValueError("Sandbox target is not a regular file.")
                target.parent.mkdir(parents=True, exist_ok=True)
                if target.exists():
                    originals[path] = target.read_text()
                target.write_text(content)
            command = [
                "bwrap", "--die-with-parent", "--unshare-net", "--ro-bind", "/usr", "/usr",
                "--ro-bind", "/bin", "/bin", "--ro-bind", "/lib", "/lib",
                "--ro-bind", "/lib64", "/lib64", "--proc", "/proc", "--dev", "/dev",
                "--tmpfs", "/tmp", "--ro-bind", str(sys.prefix), str(sys.prefix),
                "--bind", str(copy), "/workspace", "--chdir", "/workspace",
                "--setenv", "HOME", "/tmp/home", "--setenv", "PYTHONPATH", "/workspace/src",
                sys.executable, "-B", "-m", "pytest", "-q", "-p", "no:cacheprovider",
            ]
            try:
                completed = subprocess.run(
                    command, capture_output=True, text=True, timeout=TIMEOUT_SECONDS
                )
            except (subprocess.TimeoutExpired, OSError) as exc:
                raise ValueError("Sandbox test execution failed or timed out.") from exc
            diff_parts: list[str] = []
            changed = []
            for path, new_content in safe_files.items():
                old_content = originals.get(path, "")
                if old_content != new_content:
                    changed.append(str(path))
                    diff_parts.extend(difflib.unified_diff(
                        old_content.splitlines(True), new_content.splitlines(True),
                        fromfile=f"a/{path}", tofile=f"b/{path}",
                    ))
            return SandboxResult(
                status="passed" if completed.returncode == 0 else "failed",
                diff="".join(diff_parts),
                tests=(completed.stdout + completed.stderr)[-16000:],
                changed_files=changed,
                original_unchanged=True,
            )
