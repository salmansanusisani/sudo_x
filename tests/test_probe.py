import asyncio
import json

import httpx
import pytest

from sudo_x.probe import ENDPOINT, PROMPT, ProbeError, SyntheticProbe

MODEL = "nvidia/synthetic-test-model"


def response_body():
    return {
        "model": MODEL,
        "choices": [{"finish_reason": "stop", "message": {"content": json.dumps({
            "version": "1", "capability_id": "security.network_scan", "action": "blocked",
            "arguments": {}, "rationale": "An explicit target and scope are required.",
        })}}],
        "usage": {"prompt_tokens": 100, "completion_tokens": 30, "total_tokens": 130},
    }


def send(handler, **kwargs):
    return asyncio.run(SyntheticProbe(MODEL).send(
        api_key="synthetic-test-secret", approved=True, account_spend_limit_confirmed=True,
        transport=httpx.MockTransport(handler), **kwargs,
    ))


def test_probe_request_and_receipt_have_no_tool_authority():
    requests = []

    def handler(request):
        requests.append(request)
        assert str(request.url) == ENDPOINT
        assert json.loads(request.content) == SyntheticProbe(MODEL).payload()
        return httpx.Response(200, json=response_body())

    result = send(handler)
    assert len(requests) == 1
    assert result["tools_executed"] == 0
    assert result["envelope"]["action"] == "blocked"
    assert result["usage"]["total_tokens"] == 130
    assert result["cost_usd"] is None
    assert "synthetic-test-secret" not in json.dumps(result)
    disclosure = SyntheticProbe(MODEL).disclosure()
    assert disclosure["payload"]["messages"][0]["content"] == PROMPT
    assert disclosure["tool_authority"] is False


@pytest.mark.parametrize("approved,spend", [(False, False), (True, False), (False, True)])
def test_probe_requires_both_approvals_before_network(approved, spend):
    def forbidden(_request):
        pytest.fail("No request is permitted before approvals")

    with pytest.raises(ProbeError, match="need approval"):
        asyncio.run(SyntheticProbe(MODEL).send(
            api_key="synthetic-test-secret", approved=approved,
            account_spend_limit_confirmed=spend, transport=httpx.MockTransport(forbidden),
        ))


@pytest.mark.parametrize("status", [302, 401, 429, 500])
def test_no_redirects_or_retries_and_errors_do_not_expose_body(status):
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(status, text="secret-provider-error", headers={
            "Location": "https://unapproved.example/"
        })

    with pytest.raises(ProbeError) as exc:
        send(handler)
    assert "secret-provider-error" not in str(exc.value)
    assert len(requests) == 1


@pytest.mark.parametrize("case", ["model", "truncated", "tool", "exec", "usage", "size", "json"])
def test_rejects_invalid_or_unsafe_responses(case):
    body = response_body()
    message = body["choices"][0]["message"]
    if case == "model":
        body["model"] = "other/provider"
    elif case == "truncated":
        body["choices"][0]["finish_reason"] = "length"
    elif case == "tool":
        message["tool_calls"] = [{"name": "exec"}]
    elif case == "exec":
        envelope = json.loads(message["content"])
        envelope["arguments"] = {"command": "untrusted"}
        message["content"] = json.dumps(envelope)
    elif case == "usage":
        body["usage"]["completion_tokens"] = 300

    def handler(_request):
        if case == "size":
            return httpx.Response(200, content=b"x" * 32769)
        if case == "json":
            return httpx.Response(200, content=b"invalid-private-response")
        return httpx.Response(200, json=body)

    with pytest.raises(ProbeError) as exc:
        send(handler)
    assert "untrusted" not in str(exc.value)
    assert "private-response" not in str(exc.value)


def test_total_deadline_is_enforced(monkeypatch):
    monkeypatch.setattr("sudo_x.probe.TIMEOUT_SECONDS", 0.01)

    async def slow(_request):
        await asyncio.sleep(1)
        return httpx.Response(200, json=response_body())

    with pytest.raises(ProbeError, match="timed out"):
        send(slow)


def test_preview_does_not_read_secret_or_open_transport(monkeypatch, capsys):
    from sudo_x.probe import main

    def forbidden(*_args, **_kwargs):
        pytest.fail("A preview cannot access secrets or send data")

    monkeypatch.setattr("sys.argv", ["probe", "--model", MODEL])
    import os

    original_get = os.environ.get

    def get_non_secret(key, default=None):
        if key == "NEBIUS_API_KEY":
            forbidden()
        return original_get(key, default)

    monkeypatch.setattr("sudo_x.probe.os.environ.get", get_non_secret)
    monkeypatch.setattr(httpx, "AsyncClient", forbidden)
    main()
    assert json.loads(capsys.readouterr().out)["max_requests"] == 1


@pytest.mark.parametrize("model,tokens", [("other/model", 256), (MODEL, 257), (MODEL, 0)])
def test_invalid_model_and_budget(model, tokens):
    with pytest.raises(ProbeError):
        SyntheticProbe(model, tokens)
