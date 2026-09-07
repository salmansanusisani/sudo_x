import hmac
import os
import re
import secrets
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import UUID

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from starlette.exceptions import HTTPException
from starlette.types import ASGIApp, Receive, Scope, Send

from sudo_x.engine import Engine
from sudo_x.models import APIError, BackendStatus, Capability, Task, TaskInput, TaskList
from sudo_x.store import Store, data_directory

MAX_REQUEST_BYTES = 32768
SECURITY_HEADERS = {
    "Cache-Control": "no-store",
    "Referrer-Policy": "no-referrer",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Content-Security-Policy": (
        "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: blob:; media-src 'self' blob:; "
        "font-src 'self' data:; connect-src 'self'; "
        "object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'"
    ),
}


def error_response(status: int, code: str, message: str) -> JSONResponse:
    headers = dict(SECURITY_HEADERS)
    if status == 401:
        headers["WWW-Authenticate"] = "Bearer"
    return JSONResponse({"error": {"code": code, "message": message}}, status, headers=headers)


def session_token() -> str:
    token = os.environ.get("SUDOX_SESSION_TOKEN")
    if token is None:
        return secrets.token_urlsafe(32)
    if not re.fullmatch(r"[A-Za-z0-9_-]{32,256}", token):
        raise ValueError("SUDOX_SESSION_TOKEN must be 32-256 URL-safe ASCII characters.")
    return token


class LocalBoundary:
    """Validate before routing, and bound actual streamed bytes before JSON parsing."""

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        request = Request(scope)
        headers = request.headers

        async def reject(status: int, code: str, message: str) -> None:
            await error_response(status, code, message)(scope, receive, send)

        hosts = headers.getlist("host")
        match = (
            re.fullmatch(r"(127\.0\.0\.1|localhost)(?::([0-9]{1,5}))?", hosts[0])
            if len(hosts) == 1 else None
        )
        port = int(match[2] or "80") if match else 0
        server = scope.get("server")
        if (
            not match or not 1 <= port <= 65535 or scope.get("scheme") != "http"
            or (server is not None and server[1] != port)
        ):
            await reject(400, "invalid_host", "Use the loopback HTTP address and listener port.")
            return
        is_api = scope["path"] == "/api" or scope["path"].startswith("/api/")
        if is_api:
            authorization = headers.getlist("authorization")
            expected = "Bearer " + scope["app"].state.session_token
            if len(authorization) != 1 or not hmac.compare_digest(
                authorization[0].encode("utf-8"), expected.encode("ascii")
            ):
                await reject(401, "unauthorized", "A valid session bearer token is required.")
                return
            if scope["method"] not in {"GET", "HEAD", "OPTIONS"}:
                suffix = "" if port == 80 else f":{port}"
                allowed = {f"http://127.0.0.1{suffix}", f"http://localhost{suffix}"}
                origins = headers.getlist("origin")
                if len(origins) != 1 or origins[0] not in allowed:
                    await reject(
                        403, "invalid_origin", "Mutation Origin must match the local port."
                    )
                    return
        lengths = headers.getlist("content-length")
        if lengths and (len(lengths) != 1 or not re.fullmatch(r"[0-9]{1,10}", lengths[0])):
            await reject(400, "invalid_content_length", "Invalid Content-Length.")
            return
        if lengths and int(lengths[0]) > MAX_REQUEST_BYTES:
            await reject(413, "request_too_large", "Request body exceeds 32768 bytes.")
            return
        if headers.get("content-encoding", "identity") != "identity":
            await reject(415, "unsupported_encoding", "Compressed request bodies are not accepted.")
            return
        body = bytearray()
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            body.extend(message.get("body", b""))
            if len(body) > MAX_REQUEST_BYTES:
                await reject(413, "request_too_large", "Request body exceeds 32768 bytes.")
                return
            if not message.get("more_body", False):
                break

        replayed = False

        async def replay() -> dict:
            nonlocal replayed
            if replayed:
                return await receive()
            replayed = True
            return {"type": "http.request", "body": bytes(body), "more_body": False}

        async def secure_send(message: dict) -> None:
            if message["type"] == "http.response.start":
                replaced = {key.lower().encode("ascii") for key in SECURITY_HEADERS}
                message["headers"] = [
                    (key, value) for key, value in message.get("headers", [])
                    if key.lower() not in replaced
                ] + [
                    (key.lower().encode("ascii"), value.encode("ascii"))
                    for key, value in SECURITY_HEADERS.items()
                ]
            await send(message)

        await self.app(scope, replay, secure_send)


def create_app(*, token: str | None = None, ui_dir: Path | None = None) -> FastAPI:
    """Construct without opening storage; the lifespan owns all runtime resources."""
    assets = ui_dir if ui_dir is not None else Path(__file__).resolve().parents[2] / "ui/dist"

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.session_token = token if token is not None else session_token()
        store = Store(data_directory())
        engine = Engine(store)
        app.state.store = store
        app.state.engine = engine
        try:
            engine.start()
            yield
        finally:
            try:
                await engine.stop()
            finally:
                store.close()
                app.state.session_token = ""

    app = FastAPI(
        title="SUDO X", version="0.1.0", lifespan=lifespan,
        docs_url=None, redoc_url=None, openapi_url=None,
    )
    app.add_middleware(LocalBoundary)

    @app.exception_handler(APIError)
    async def api_error(_request: Request, exc: APIError):
        return error_response(exc.status, exc.code, exc.message)

    @app.exception_handler(RequestValidationError)
    async def validation_error(_request: Request, _exc: RequestValidationError):
        return error_response(
            422, "validation_error",
            "Invalid request. Use a UUID task ID and a JSON object with only prompt "
            "(1-2000 nonblank characters) and kind (system, nigeria, or request).",
        )

    @app.exception_handler(HTTPException)
    async def http_error(_request: Request, exc: HTTPException):
        return error_response(exc.status_code, "http_error", "Request cannot be served.")

    @app.exception_handler(Exception)
    async def unexpected_error(_request: Request, _exc: Exception):
        return error_response(500, "internal_error", "An internal error prevented this request.")

    @app.get("/api/status", response_model=BackendStatus)
    async def status():
        return BackendStatus(capabilities=[
            Capability(
                id="system", label="Local system snapshot", enabled=True,
                description="Explicit read-only OS, Python, CPU, load and memory snapshot.",
            ),
            Capability(
                id="nigeria", label="Nigeria offline geography", enabled=True,
                description="Fixed Abuja/Lagos map demonstration only; live news is unavailable.",
            ),
            Capability(
                id="request", label="General assistant", enabled=False,
                description="Provider and general machine tools are not connected.",
            ),
        ])

    @app.get("/api/tasks", response_model=TaskList)
    async def tasks(request: Request):
        return TaskList(tasks=request.app.state.store.recent())

    @app.post("/api/tasks", response_model=Task, status_code=202)
    async def create_task(body: TaskInput, request: Request):
        return request.app.state.engine.submit(body)

    @app.get("/api/tasks/{task_id}", response_model=Task)
    async def task_detail(task_id: UUID, request: Request):
        return request.app.state.store.get(str(task_id))

    @app.post("/api/tasks/{task_id}/cancel", response_model=Task)
    async def cancel_task(task_id: UUID, request: Request):
        return request.app.state.engine.cancel(str(task_id))

    @app.api_route("/{path:path}", methods=["GET", "HEAD"], include_in_schema=False)
    async def frontend(path: str):
        if path == "api" or path.startswith("api/"):
            raise APIError(404, "not_found", "API route not found.")
        if "\x00" in path or "\\" in path or any(
            part.startswith(".") for part in path.split("/") if part
        ):
            raise APIError(404, "not_found", "Asset not found.")
        root = assets.resolve()
        target = (root / (path or "index.html")).resolve()
        if not target.is_relative_to(root):
            raise APIError(404, "not_found", "Asset not found.")
        if target.is_file():
            return FileResponse(target)
        # Only extensionless browser routes get the SPA entry point, never missing assets.
        index = (root / "index.html").resolve()
        if not Path(path).suffix and index.is_relative_to(root) and index.is_file():
            return FileResponse(index)
        if not (root / "index.html").is_file():
            raise APIError(503, "ui_not_built", "Backend ready; ui/dist has not been built yet.")
        raise APIError(404, "not_found", "Asset not found.")

    return app
