import hashlib
import json
import os
import sqlite3
import stat
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from sudo_x.models import (
    TERMINAL,
    APIError,
    Event,
    Phase,
    ReviewReceipt,
    Status,
    Task,
    TaskInput,
)

if os.name == "nt":
    from sudo_x.windows_storage import acquire_lease, assert_private, prepare_directory
else:
    import fcntl

MAX_TASKS = 1000
MAX_ACTIVE_TASKS = 32
RECENT_TASKS = 50


def now() -> str:
    return datetime.now(UTC).isoformat(timespec="microseconds")


def data_directory() -> Path:
    override = os.environ.get("SUDOX_DATA_DIR")
    if override:
        path = Path(override).expanduser()
        if not path.is_absolute():
            raise ValueError("SUDOX_DATA_DIR must be an absolute path.")
        return path
    if os.name == "nt":
        local = os.environ.get("LOCALAPPDATA", "")
        base = Path(local) if local and Path(local).is_absolute() else Path.home() / "AppData/Local"
        return base / "sudo-x"
    xdg = os.environ.get("XDG_DATA_HOME", "")
    base = Path(xdg) if xdg and Path(xdg).is_absolute() else Path.home() / ".local/share"
    return base / "sudo-x"


class Store:
    """Single-process store; all calls run on the application's event-loop thread."""

    def __init__(self, directory: Path):
        self.connection = None
        self._fd = None
        self._lease = None
        if os.name == "nt":
            prepare_directory(directory)
        else:
            self._prepare_posix_directory(directory)
        path = directory / "tasks.sqlite3"
        try:
            if os.name == "nt":
                self._lease = acquire_lease(directory)
                # SQLite companions must inherit the same private directory ACL.
                for candidate in (
                    path,
                    directory / "tasks.sqlite3-wal",
                    directory / "tasks.sqlite3-shm",
                ):
                    if candidate.exists() or candidate.is_symlink():
                        assert_private(candidate)
                        info = candidate.lstat()
                        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                            raise ValueError("SUDO X database must be a private regular file.")
            else:
                self._open_posix_database(path)
            self._initialize(path)
        except BaseException:
            self.close()
            raise

    @staticmethod
    def _prepare_posix_directory(directory: Path) -> None:
        directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        info = directory.lstat()
        if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
            raise ValueError("SUDO X data directory must be user-owned, non-symlink, mode 0700.")

    def _open_posix_database(self, path: Path) -> None:
        self._fd = os.open(path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
        info = os.fstat(self._fd)
        if (
            not stat.S_ISREG(info.st_mode)
            or info.st_uid != os.getuid()
            or info.st_mode & 0o077
            or info.st_nlink != 1
        ):
            raise ValueError("SUDO X database must be a private, user-owned regular file.")
        try:
            fcntl.flock(self._fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ValueError("Another SUDO X process is using this data directory.") from exc

    def _initialize(self, path: Path) -> None:
        self.connection = sqlite3.connect(path, timeout=2)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.connection.execute("PRAGMA journal_mode = WAL")
        version = self.connection.execute("PRAGMA user_version").fetchone()[0]
        if version not in (0, 1, 2):
            raise ValueError("Unsupported SUDO X database version.")
        if version == 0:
            self.connection.executescript("""
                    BEGIN;
                    CREATE TABLE tasks (
                        id TEXT PRIMARY KEY,
                        prompt TEXT NOT NULL,
                        kind TEXT NOT NULL CHECK(kind IN ('system', 'nigeria', 'request')),
                        status TEXT NOT NULL CHECK(status IN
                            ('queued', 'running', 'completed', 'blocked', 'cancelled', 'failed')),
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        summary TEXT NOT NULL,
                        scene TEXT NOT NULL,
                        result TEXT
                    );
                    CREATE INDEX tasks_recent ON tasks(created_at DESC);
                    CREATE TABLE events (
                        task_id TEXT NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
                        sequence INTEGER NOT NULL,
                        timestamp TEXT NOT NULL,
                        phase TEXT NOT NULL,
                        message TEXT NOT NULL,
                        PRIMARY KEY(task_id, sequence)
                    );
                    CREATE TABLE reviews (
                        id TEXT PRIMARY KEY,
                        kind TEXT NOT NULL CHECK(kind IN ('planner', 'research')),
                        action_hash TEXT NOT NULL,
                        reviewed_at TEXT NOT NULL
                    );
                    CREATE INDEX reviews_recent ON reviews(reviewed_at DESC);
                    PRAGMA user_version = 2;
                    COMMIT;
                """)
        elif version == 1:
            self.connection.executescript("""
                BEGIN;
                CREATE TABLE reviews (
                    id TEXT PRIMARY KEY,
                    kind TEXT NOT NULL CHECK(kind IN ('planner', 'research')),
                    action_hash TEXT NOT NULL,
                    reviewed_at TEXT NOT NULL
                );
                CREATE INDEX reviews_recent ON reviews(reviewed_at DESC);
                PRAGMA user_version = 2;
                COMMIT;
            """)

    def close(self) -> None:
        if self.connection is not None:
            self.connection.close()
            self.connection = None
        if self._fd is not None:
            os.close(self._fd)
            self._fd = None
        if self._lease is not None:
            self._lease.Close()
            self._lease = None

    def get(self, task_id: str) -> Task:
        row = self.connection.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if row is None:
            raise APIError(404, "task_not_found", "Task not found.")
        values = dict(row)
        values["result"] = json.loads(values["result"]) if values["result"] else None
        values["events"] = [
            Event(**dict(event))
            for event in self.connection.execute(
                "SELECT sequence, timestamp, phase, message FROM events "
                "WHERE task_id = ? ORDER BY sequence",
                (task_id,),
            )
        ]
        return Task(**values)

    def recent(self) -> list[Task]:
        rows = self.connection.execute(
            "SELECT id FROM tasks ORDER BY created_at DESC, id DESC LIMIT ?", (RECENT_TASKS,)
        ).fetchall()
        return [self.get(row["id"]) for row in rows]

    def create(self, task_input: TaskInput) -> Task:
        task_id, timestamp = str(uuid4()), now()
        scene = {"system": "system", "nigeria": "map", "request": "overview"}[task_input.kind]
        with self.connection:
            if self.connection.execute("SELECT count(*) FROM tasks").fetchone()[0] >= MAX_TASKS:
                raise APIError(
                    409,
                    "task_limit_reached",
                    "History is full (1000 tasks). No history was deleted. "
                    "Stop SUDO X and explicitly archive or remove its data directory "
                    "before retrying.",
                )
            active = self.connection.execute(
                "SELECT count(*) FROM tasks WHERE status IN ('queued', 'running')"
            ).fetchone()[0]
            if active >= MAX_ACTIVE_TASKS:
                raise APIError(429, "queue_full", "At most 32 active tasks are allowed.")
            self.connection.execute(
                "INSERT INTO tasks VALUES (?, ?, ?, 'queued', ?, ?, ?, ?, NULL)",
                (
                    task_id,
                    task_input.prompt,
                    task_input.kind,
                    timestamp,
                    timestamp,
                    "Queued for a bounded local task.",
                    scene,
                ),
            )
            self.connection.execute(
                "INSERT INTO events VALUES (?, 1, ?, 'observe', ?)",
                (task_id, timestamp, "Request accepted and persisted in the local queue."),
            )
        return self.get(task_id)

    def advance(
        self,
        task_id: str,
        phase: Phase,
        message: str,
        *,
        status: Status = "running",
        result: dict | None = None,
    ) -> bool:
        with self.connection:
            current = self.get(task_id)
            if current.status in TERMINAL:
                return False
            timestamp = now()
            self.connection.execute(
                "UPDATE tasks SET status = ?, updated_at = ?, summary = ?, "
                "result = COALESCE(?, result) WHERE id = ?",
                (
                    status,
                    timestamp,
                    message,
                    json.dumps(result) if result is not None else None,
                    task_id,
                ),
            )
            self.connection.execute(
                "INSERT INTO events VALUES (?, ?, ?, ?, ?)",
                (task_id, len(current.events) + 1, timestamp, phase, message),
            )
        return True

    def interrupt(self, message: str) -> None:
        rows = self.connection.execute(
            "SELECT id FROM tasks WHERE status IN ('queued', 'running')"
        ).fetchall()
        for row in rows:
            self.advance(row["id"], "blocked", message, status="blocked")

    def create_review(self, kind: str, content: dict) -> ReviewReceipt:
        canonical = json.dumps(content, sort_keys=True, separators=(",", ":"))
        receipt = ReviewReceipt(
            id=str(uuid4()), kind=kind, action_hash=hashlib.sha256(canonical.encode()).hexdigest(),
            reviewed_at=now(),
        )
        with self.connection:
            self.connection.execute(
                "INSERT INTO reviews VALUES (?, ?, ?, ?)",
                (receipt.id, receipt.kind, receipt.action_hash, receipt.reviewed_at),
            )
        return receipt
