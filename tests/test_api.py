import asyncio
import json
import os
import platform
import stat
import time
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from sudo_x.api import MAX_REQUEST_BYTES, create_app, session_token
from sudo_x.engine import Engine
from sudo_x.models import TERMINAL, TaskInput
from sudo_x.provider import MockPlanner, NebiusPlanner, PlanEnvelope, provider_config
from sudo_x.research import TavilyResearch
from sudo_x.store import Store, data_directory

TOKEN = "test-session-token-" + "x" * 32
BASE = "http://127.0.0.1:8765"
AUTH = {"Authorization": f"Bearer {TOKEN}"}
MUTATION = {**AUTH, "Origin": BASE}


@pytest.fixture
def storage(tmp_path, monkeypatch):
    directory = tmp_path / "private-data"
    monkeypatch.setenv("SUDOX_DATA_DIR", str(directory))
    monkeypatch.setenv("SUDOX_SESSION_TOKEN", TOKEN)
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)
    return directory


@pytest.fixture
def client(storage):
    with TestClient(create_app(), base_url=BASE) as test_client:
        yield test_client


def submit(client, kind="system", prompt="Show a local system snapshot"):
    response = client.post("/api/tasks", headers=MUTATION, json={"prompt": prompt, "kind": kind})
    assert response.status_code == 202, response.text
    task = response.json()
    assert task["status"] == "queued"
    assert task["events"][0]["sequence"] == 1
    return task


def finished(client, task_id):
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        response = client.get(f"/api/tasks/{task_id}", headers=AUTH)
        assert response.status_code == 200
        task = response.json()
        if task["status"] in TERMINAL:
            assert [event["sequence"] for event in task["events"]] == list(
                range(1, len(task["events"]) + 1)
            )
            assert task["updated_at"] == task["events"][-1]["timestamp"]
            return task
    pytest.fail("Task did not reach a terminal state")


@pytest.mark.parametrize("method,path", [
    ("GET", "/api/status"), ("GET", "/api/tasks"),
    ("POST", "/api/tasks"), ("GET", f"/api/tasks/{uuid4()}"),
    ("POST", f"/api/tasks/{uuid4()}/cancel"), ("GET", "/api/unknown"),
])
def test_all_api_routes_require_bearer(client, method, path):
    for headers in ({}, {"Authorization": "Bearer wrong"}):
        response = client.request(method, path, headers=headers)
        assert response.status_code == 401
        assert response.json()["error"]["code"] == "unauthorized"
        assert response.headers["www-authenticate"] == "Bearer"
    assert client.request(method, path + f"?token={TOKEN}").status_code == 401


def test_status_and_no_cors(client):
    response = client.get("/api/status", headers=AUTH)
    body = response.json()
    assert body["mode"] == "local"
    assert body["provider"] == "not_configured"
    assert body["version"] == "0.1.0"
    assert {cap["id"]: cap["enabled"] for cap in body["capabilities"]} == {
        "system": True, "nigeria": True, "planner": False, "request": False,
        "news.nigeria": False, "security.network_scan": False,
        "remote.inspect": False, "code.sandbox": False,
    }
    assert TOKEN not in response.text
    assert response.headers["cache-control"] == "no-store"
    assert "access-control-allow-origin" not in response.headers
    preflight = client.options("/api/tasks", headers={
        "Origin": "https://evil.example", "Access-Control-Request-Method": "POST",
    })
    assert preflight.status_code == 401
    assert "access-control-allow-origin" not in preflight.headers


def test_default_provider_is_not_configured(storage, monkeypatch):
    monkeypatch.delenv("SUDOX_PROVIDER", raising=False)
    assert provider_config().kind == "not_configured"
    with TestClient(create_app(), base_url=BASE) as local_client:
        response = local_client.get("/api/status", headers=AUTH)
    assert response.status_code == 200
    assert response.json()["provider"] == "not_configured"
    assert response.json()["provider_ready"] is False


def test_mock_provider_is_deterministic_and_non_executable(monkeypatch):
    config = provider_config({"SUDOX_PROVIDER": "mock"})
    plan = MockPlanner(config).plan("inspect this project")
    assert plan.provider == "mock"
    assert plan.action == "blocked"
    assert "No external request was made" in plan.message
    assert plan.envelope is not None
    assert plan.envelope.action == "blocked"


def test_nebius_planner_is_typed_and_non_executable(monkeypatch):
    import httpx

    monkeypatch.setenv("NEBIUS_API_KEY", "test-key")
    config = provider_config({
        "SUDOX_PROVIDER": "nebius",
        "SUDOX_MODEL_PRIMARY": "nvidia/synthetic-test",
        "NEBIUS_API_KEY": "not-used-by-synthetic-probe",
    })
    def handler(_request):
        return httpx.Response(200, json={
            "model": "nvidia/synthetic-test",
            "choices": [{"finish_reason": "stop", "message": {"content": json.dumps({
                "version": "1", "capability_id": "request", "action": "propose",
                "arguments": {}, "rationale": "A typed non-executable proposal.",
            })}}],
        })

    planner = NebiusPlanner(
        config, client_factory=lambda **kwargs: httpx.Client(
            transport=httpx.MockTransport(handler), **kwargs
        )
    )
    plan = planner.plan("inspect this project")
    assert plan.provider == "nebius"
    assert plan.action == "answer"
    assert plan.envelope is not None
    assert plan.envelope.action == "propose"
    assert plan.cloud_disclosure is not None
    assert plan.cloud_disclosure.base_url == config.base_url
    assert "No tool" in plan.message


def test_nebius_planner_validates_live_response_without_tools(monkeypatch):
    import httpx

    monkeypatch.setenv("NEBIUS_API_KEY", "test-key")
    config = provider_config({
        "SUDOX_PROVIDER": "nebius", "SUDOX_MODEL_PRIMARY": "nvidia/test",
        "NEBIUS_API_KEY": "test-key",
    })

    def handler(request):
        assert request.headers["Authorization"] == "Bearer test-key"
        payload = request.read().decode()
        assert "No machine snapshot" not in payload
        return httpx.Response(200, json={
            "model": "nvidia/test",
            "choices": [{"finish_reason": "stop", "message": {"content": json.dumps({
                "version": "1", "capability_id": "system", "action": "propose",
                "arguments": {}, "rationale": "Read-only observation requested.",
            })}}],
        })

    import json

    planner = NebiusPlanner(
        config, client_factory=lambda **kwargs: httpx.Client(
            transport=httpx.MockTransport(handler), **kwargs
        )
    )
    plan = planner.plan("inspect the fictional local system")
    assert plan.envelope is not None
    assert plan.envelope.capability_id == "system"
    assert plan.cloud_disclosure is not None
    assert "sent to Nebius" in plan.cloud_disclosure.data_handling


def test_nebius_preview_discloses_cloud_boundary(storage, monkeypatch):
    monkeypatch.setenv("SUDOX_PROVIDER", "nebius")
    monkeypatch.setenv("SUDOX_MODEL_PRIMARY", "nvidia/synthetic-test")
    monkeypatch.setenv("NEBIUS_API_KEY", "not-used-by-synthetic-probe")
    import httpx

    real_client = httpx.Client
    def handler(_request):
        return httpx.Response(200, json={
            "model": "nvidia/synthetic-test",
            "choices": [{"finish_reason": "stop", "message": {"content": json.dumps({
                "version": "1", "capability_id": "request", "action": "propose",
                "arguments": {}, "rationale": "Synthetic test proposal.",
            })}}],
        })
    monkeypatch.setattr(
        "sudo_x.provider.httpx.Client",
        lambda **kwargs: real_client(transport=httpx.MockTransport(handler), **kwargs),
    )
    with TestClient(create_app(), base_url=BASE) as local_client:
        response = local_client.post(
            "/api/planner/preview", headers=MUTATION, json={"prompt": "inspect this project"}
        )
    assert response.status_code == 200
    body = response.json()
    assert body["provider"] == "nebius"
    assert body["cloud_disclosure"]["provider"] == "Nebius Token Factory"
    assert "sent to Nebius" in body["cloud_disclosure"]["data_handling"]
    assert body["envelope"]["action"] == "propose"


def test_tavily_nigeria_research_validates_sources_without_local_data():
    import httpx

    def handler(request):
        body = request.read().decode()
        assert "hostname" not in body
        return httpx.Response(200, json={
            "answer": "A bounded public-source summary.",
            "results": [{
                "title": "Nigeria public source",
                "url": "https://example.com/nigeria",
                "content": "A short source excerpt.",
                "published_date": "2026-09-08",
            }],
        })

    research = TavilyResearch(
        "test-tavily-key",
        client_factory=lambda **kwargs: httpx.Client(
            transport=httpx.MockTransport(handler), **kwargs
        ),
    )
    result = research.search_nigeria()
    assert str(result.sources[0].url) == "https://example.com/nigeria"
    assert result.cloud_disclosure["provider"] == "Tavily"


def test_tavily_research_requires_key():
    with pytest.raises(ValueError, match="not configured"):
        TavilyResearch("").search_nigeria()


def test_review_receipt_is_hashed_and_never_executes(client):
    response = client.post(
        "/api/reviews", headers=MUTATION,
        json={"kind": "planner", "content": {"action": "propose", "arguments": {}}},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["kind"] == "planner"
    assert len(body["action_hash"]) == 64
    assert body["status"] == "reviewed"
    assert body["execution"] == "unavailable"


def test_review_receipt_persists_across_store_restart(storage):
    first = Store(storage)
    receipt = first.create_review("research", {"query": "fixed Nigeria query"})
    first.close()
    second = Store(storage)
    row = second.connection.execute(
        "SELECT id, kind, action_hash, reviewed_at FROM reviews WHERE id = ?", (receipt.id,)
    ).fetchone()
    second.close()
    assert dict(row) == {
        "id": receipt.id, "kind": "research", "action_hash": receipt.action_hash,
        "reviewed_at": receipt.reviewed_at,
    }


def test_provider_budget_configuration_is_bounded():
    base = {
        "SUDOX_PROVIDER": "nebius",
        "SUDOX_MODEL_PRIMARY": "model",
        "NEBIUS_API_KEY": "key",
    }
    assert provider_config({**base, "SUDOX_PROVIDER_TIMEOUT_SECONDS": "2"}).timeout_seconds == 2
    with pytest.raises(ValueError):
        provider_config({**base, "SUDOX_PROVIDER_TIMEOUT_SECONDS": "31"})
    with pytest.raises(ValueError):
        provider_config({**base, "SUDOX_PROVIDER_MAX_TOKENS": "0"})


def test_capabilities_endpoint_explains_disabled_authority(client):
    response = client.get("/api/capabilities", headers=AUTH)
    assert response.status_code == 200
    body = response.json()
    assert body["version"] == "1"
    by_id = {item["id"]: item for item in body["capabilities"]}
    assert by_id["security.network_scan"]["effect"] == "network"
    assert "authorization" in by_id["security.network_scan"]["reason"]
    assert by_id["code.sandbox"]["effect"] == "mutate"


def test_planner_preview_requires_a_configured_non_executable_planner(client):
    response = client.post(
        "/api/planner/preview", headers=MUTATION, json={"prompt": "inspect my project"}
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "planner_not_ready"


def test_mock_planner_preview_returns_data_only(storage, monkeypatch):
    monkeypatch.setenv("SUDOX_PROVIDER", "mock")
    with TestClient(create_app(), base_url=BASE) as local_client:
        response = local_client.post(
            "/api/planner/preview", headers=MUTATION, json={"prompt": "inspect my project"}
        )
    assert response.status_code == 200
    body = response.json()
    assert body["provider"] == "mock"
    assert body["envelope"] == {
        "version": "1", "capability_id": "request", "action": "blocked",
        "arguments": {}, "rationale": "Mock provider cannot execute.",
    }
    assert "No external request was made" in body["message"]


@pytest.mark.parametrize("payload", [
    {
        "capability_id": "request", "action": "propose", "rationale": "x",
        "arguments": {"shell": "ls"},
    },
    {"capability_id": "request", "action": "propose", "rationale": "x", "unknown": True},
    {"capability_id": "Request", "action": "propose", "rationale": "x"},
])
def test_plan_envelope_rejects_execution_or_unknown_fields(payload):
    with pytest.raises(ValueError):
        PlanEnvelope.model_validate(payload)


@pytest.mark.parametrize("environ", [
    {"SUDOX_PROVIDER": "unknown"},
    {"SUDOX_PROVIDER": "nebius"},
    {"SUDOX_PROVIDER": "nebius", "SUDOX_MODEL_PRIMARY": "model"},
    {
        "SUDOX_PROVIDER": "nebius", "SUDOX_MODEL_PRIMARY": "model",
        "NEBIUS_API_KEY": "key", "NEBIUS_BASE_URL": "http://bad",
    },
])
def test_provider_configuration_rejects_unsafe_or_incomplete_values(environ):
    with pytest.raises(ValueError):
        provider_config(environ)


@pytest.mark.parametrize("host", [
    "evil.example:8765", "127.0.0.1.evil.example:8765", "0.0.0.0:8765",
    "127.0.0.2:8765", "127.0.0.1:9999", "localhost:99999", "localhost.",
    "user@localhost:8765", "[::1]:8765", "localhost:0",
])
def test_host_boundary(client, host):
    for path in ("/", "/api/status"):
        response = client.get(path, headers={**AUTH, "Host": host})
        assert response.status_code == 400
        assert response.json()["error"]["code"] == "invalid_host"


@pytest.mark.parametrize("origin", [
    None, "null", "https://127.0.0.1:8765", "http://127.0.0.1:9999",
    "http://localhost:8765/", "http://evil.example:8765",
])
def test_mutation_origin(client, origin):
    headers = dict(AUTH)
    if origin is not None:
        headers["Origin"] = origin
    for path in ("/api/tasks", f"/api/tasks/{uuid4()}/cancel"):
        response = client.post(path, headers=headers, json={"prompt": "test", "kind": "request"})
        assert response.status_code == 403
        assert response.json()["error"]["code"] == "invalid_origin"


def test_localhost_and_custom_port(storage):
    with TestClient(create_app(), base_url="http://localhost:9321") as client:
        assert client.get("/api/status", headers=AUTH).status_code == 200
        response = client.post("/api/tasks", headers={**AUTH, "Origin": "http://localhost:9321"},
                               json={"prompt": "test", "kind": "request"})
        assert response.status_code == 202
        assert client.post("/api/tasks", headers=MUTATION, json={}).status_code == 403


@pytest.mark.parametrize("body", [
    {}, {"prompt": "", "kind": "system"}, {"prompt": "   ", "kind": "system"},
    {"prompt": "x" * 2001, "kind": "system"}, {"prompt": "test", "kind": "shell"},
    {"prompt": "test", "kind": "system", "command": "id"},
    {"prompt": 42, "kind": "request"},
])
def test_input_validation(client, body):
    response = client.post("/api/tasks", headers=MUTATION, json=body)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"
    assert "input" not in response.json()


def test_ids_and_body_limits(client):
    assert client.get("/api/tasks/not-a-uuid", headers=AUTH).status_code == 422
    assert client.get(f"/api/tasks/{uuid4()}", headers=AUTH).status_code == 404
    assert client.post(f"/api/tasks/{uuid4()}/cancel", headers=MUTATION).status_code == 404
    assert client.post("/api/tasks", headers=MUTATION, content="{").status_code == 422
    response = client.post("/api/tasks", headers=MUTATION, content=b"x" * (MAX_REQUEST_BYTES + 1))
    assert response.status_code == 413
    response = client.post("/api/tasks", headers=MUTATION, content=iter([
        b"x" * MAX_REQUEST_BYTES, b"x",
    ]))
    assert response.status_code == 413
    assert client.post("/api/tasks", headers={**MUTATION, "Content-Encoding": "gzip"},
                       content=b"body").status_code == 415


def test_body_limit_counts_separate_asgi_chunks(client):
    async def exercise():
        chunks = iter([
            {"type": "http.request", "body": b"x" * MAX_REQUEST_BYTES, "more_body": True},
            {"type": "http.request", "body": b"x", "more_body": False},
        ])
        sent = []

        async def receive():
            return next(chunks)

        async def send(message):
            sent.append(message)

        await client.app({
            "type": "http", "http_version": "1.1", "method": "POST", "scheme": "http",
            "path": "/api/tasks", "raw_path": b"/api/tasks", "query_string": b"",
            "server": ("127.0.0.1", 8765), "client": ("127.0.0.1", 12345),
            "headers": [
                (b"host", b"127.0.0.1:8765"),
                (b"authorization", f"Bearer {TOKEN}".encode()),
                (b"origin", BASE.encode()),
            ],
        }, receive, send)
        assert sent[0]["status"] == 413

    client.portal.call(exercise)


def test_system_snapshot_and_persistence(storage):
    with TestClient(create_app(), base_url=BASE) as client:
        task = finished(client, submit(client)["id"])
        assert task["status"] == "completed"
        assert task["scene"] == "system"
        result = task["result"]
        assert result["os"] == platform.system()
        assert result["kernel"] == platform.release()
        assert result["python"] == platform.python_version()
        assert result["logical_cpu_count"] == os.cpu_count()
        assert "hostname" not in result
        assert set(result["memory"]) == {"total_bytes", "available_bytes"}
        assert {event["phase"] for event in task["events"]} >= {"act", "verify", "complete"}
        listing = client.get("/api/tasks", headers=AUTH).json()["tasks"]
        assert listing == [task]
        if os.name == "nt":
            from sudo_x.windows_storage import assert_private

            assert_private(storage)
            for path in storage.glob('tasks.sqlite3*'):
                assert_private(path)
        else:
            assert stat.S_IMODE(storage.stat().st_mode) == 0o700
            for path in storage.iterdir():
                assert stat.S_IMODE(path.stat().st_mode) & 0o077 == 0
    with TestClient(create_app(), base_url=BASE) as client:
        assert client.get(f"/api/tasks/{task['id']}", headers=AUTH).json() == task
        assert client.post(f"/api/tasks/{task['id']}/cancel", headers=MUTATION).status_code == 409


def test_offline_nigeria_and_generic_never_read_system(client, monkeypatch):
    def forbidden():
        pytest.fail("Only explicit system kind may collect local metrics")

    monkeypatch.setattr("sudo_x.engine.system_snapshot", forbidden)
    task = finished(client, submit(client, "nigeria", "Latest news from Nigeria")["id"])
    assert task["status"] == "blocked"
    assert task["scene"] == "map"
    assert "live news provider not connected" in task["summary"].lower()
    assert task["result"] == {
        "label": "Nigeria", "mode": "offline_geography", "news_available": False,
        "cities": [
            {"name": "Abuja", "lat": 9.0765, "lon": 7.3986},
            {"name": "Lagos", "lat": 6.5244, "lon": 3.3792},
        ],
    }
    task = finished(client, submit(client, "request", "Scan files and show system snapshot")["id"])
    assert task["status"] == "blocked"
    assert task["scene"] == "overview"
    assert task["result"] is None
    assert "not connected" in task["summary"]
    assert not any(event["phase"] in {"act", "verify", "complete"} for event in task["events"])


def test_cancellation_stops_further_steps(storage, monkeypatch):
    original = Engine._step

    async def hold_before_action(self, task_id, phase, message, **kwargs):
        if phase == "plan":
            self.test_reached.set()
            await self.test_release.wait()
        return await original(self, task_id, phase, message, **kwargs)

    monkeypatch.setattr(Engine, "_step", hold_before_action)
    with TestClient(create_app(), base_url=BASE) as client:
        engine = client.app.state.engine

        async def setup():
            engine.test_reached = asyncio.Event()
            engine.test_release = asyncio.Event()

        client.portal.call(setup)
        task_id = submit(client)["id"]

        async def wait():
            await asyncio.wait_for(engine.test_reached.wait(), timeout=2)

        client.portal.call(wait)
        running = client.get(f"/api/tasks/{task_id}", headers=AUTH).json()
        assert running["status"] == "running"
        assert len(running["events"]) == 2
        response = client.post(f"/api/tasks/{task_id}/cancel", headers=MUTATION)
        assert response.status_code == 200
        cancelled = response.json()
        assert cancelled["status"] == "cancelled"
        assert cancelled["result"] is None

        async def release():
            engine.test_release.set()
            await asyncio.wait_for(engine.queue.join(), timeout=2)

        client.portal.call(release)
        assert client.get(f"/api/tasks/{task_id}", headers=AUTH).json() == cancelled
        assert client.post(f"/api/tasks/{task_id}/cancel", headers=MUTATION).status_code == 409


@pytest.mark.parametrize("running", [False, True])
def test_restart_reconciles_unfinished(storage, running):
    store = Store(storage)
    task = store.create(TaskInput(prompt="Unfinished task", kind="system"))
    if running:
        store.advance(task.id, "observe", "Started before interruption.")
    store.close()
    with TestClient(create_app(), base_url=BASE) as client:
        recovered = client.get(f"/api/tasks/{task.id}", headers=AUTH).json()
        assert recovered["status"] == "blocked"
        assert "Interrupted" in recovered["summary"]
        assert recovered["result"] is None
        assert recovered["events"][-1]["phase"] == "blocked"
    with TestClient(create_app(), base_url=BASE) as client:
        assert client.get(f"/api/tasks/{task.id}", headers=AUTH).json() == recovered


def test_shutdown_cleans_worker_and_records_interruption(storage, monkeypatch):
    async def wait_forever(self, _task_id):
        await asyncio.Event().wait()

    monkeypatch.setattr(Engine, "_run", wait_forever)
    with TestClient(create_app(), base_url=BASE) as client:
        task_id = submit(client)["id"]
        worker = client.app.state.engine.worker
    assert worker.done()
    store = Store(storage)
    try:
        assert store.get(task_id).status == "blocked"
        assert "shutdown" in store.get(task_id).summary
    finally:
        store.close()


def test_failures_are_honest_and_sanitized(client, monkeypatch):
    def broken():
        raise OSError("private/path or token must not escape")

    monkeypatch.setattr("sudo_x.engine.system_snapshot", broken)
    task = finished(client, submit(client)["id"])
    assert task["status"] == "failed"
    assert task["result"] is None
    assert "private/path" not in str(task)
    assert not any(event["phase"] == "complete" for event in task["events"])


def test_history_cap_and_recent_fifty(client, monkeypatch):
    async def seed():
        store = client.app.state.store
        for number in range(55):
            task = store.create(TaskInput(prompt=f"Task {number}", kind="request"))
            store.advance(task.id, "blocked", "Unsupported fixture.", status="blocked")

    client.portal.call(seed)
    tasks = client.get("/api/tasks", headers=AUTH).json()["tasks"]
    assert len(tasks) == 50
    assert tasks[0]["prompt"] == "Task 54"
    monkeypatch.setattr("sudo_x.store.MAX_TASKS", 55)
    response = client.post(
        "/api/tasks", headers=MUTATION, json={"prompt": "overflow", "kind": "request"}
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "task_limit_reached"
    assert client.get(f"/api/tasks/{tasks[-1]['id']}", headers=AUTH).status_code == 200


def test_active_queue_is_bounded(storage, monkeypatch):
    async def wait_forever(self, _task_id):
        await asyncio.Event().wait()

    monkeypatch.setattr(Engine, "_run", wait_forever)
    with TestClient(create_app(), base_url=BASE) as client:
        for _ in range(32):
            submit(client, "request", "queued")
        response = client.post("/api/tasks", headers=MUTATION,
                               json={"prompt": "overflow", "kind": "request"})
        assert response.status_code == 429
        assert response.json()["error"]["code"] == "queue_full"


def test_static_assets_and_traversal(storage, tmp_path):
    assets = tmp_path / "dist"
    assets.mkdir()
    (assets / "index.html").write_text("<!doctype html><title>SUDO X test</title>")
    (assets / "main.js").write_text("// test bundle")
    outside = tmp_path / "private.txt"
    outside.write_text("must not be served")
    try:
        (assets / "escape.txt").symlink_to(outside)
    except OSError as exc:
        if os.name != "nt" or exc.winerror != 1314:
            raise
        # Windows requires Developer Mode for unprivileged symlink creation.
    with TestClient(create_app(ui_dir=assets), base_url=BASE) as client:
        assert client.get("/").status_code == 200
        assert client.get("/main.js").text == "// test bundle"
        assert client.get("/tasks/view").status_code == 200
        assert client.get("/missing.js").status_code == 404
        for path in ("/%2e%2e/private.txt", "/escape.txt", "/.env", "/%5cprivate.txt"):
            response = client.get(path)
            assert response.status_code == 404
            assert "must not be served" not in response.text
        assert client.get("/api/unknown", headers=AUTH).status_code == 404
        assert client.get("/api/unknown").status_code == 401
    with TestClient(create_app(ui_dir=tmp_path / "missing-dist"), base_url=BASE) as client:
        assert client.get("/").json()["error"]["code"] == "ui_not_built"
        assert client.get("/api/status", headers=AUTH).status_code == 200


def test_storage_permissions_and_single_process(storage, tmp_path):
    store = Store(storage)
    try:
        with pytest.raises(ValueError, match="Another SUDO X"):
            Store(storage)
    finally:
        store.close()
    reopened = Store(storage)
    reopened.close()
    if os.name == "nt":
        return  # Windows ACL and reparse-point rejection have dedicated tests.
    unsafe = tmp_path / "public-data"
    unsafe.mkdir(mode=0o755)
    unsafe.chmod(0o755)
    with pytest.raises(ValueError, match="0700"):
        Store(unsafe)
    linked = tmp_path / "linked-data"
    linked.symlink_to(storage, target_is_directory=True)
    with pytest.raises(ValueError, match="non-symlink"):
        Store(linked)


def test_xdg_and_token_configuration(monkeypatch, tmp_path):
    monkeypatch.delenv("SUDOX_DATA_DIR", raising=False)
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path))
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    assert data_directory() == tmp_path / "sudo-x"
    monkeypatch.setenv("SUDOX_DATA_DIR", "relative/path")
    with pytest.raises(ValueError, match="absolute"):
        data_directory()
    monkeypatch.delenv("SUDOX_SESSION_TOKEN", raising=False)
    assert session_token() != session_token()
    monkeypatch.setenv("SUDOX_SESSION_TOKEN", "short")
    with pytest.raises(ValueError, match="32-256"):
        session_token()


def test_cli_rejects_root_and_nonloopback(monkeypatch):
    from sudo_x.cli import main

    monkeypatch.setattr("sys.argv", ["sudo-x"])
    monkeypatch.setattr("sudo_x.cli.is_privileged", lambda: True)
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 2
    monkeypatch.setattr("sys.argv", ["sudo-x", "--host", "0.0.0.0"])
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 2
