"""Explicit, synthetic-only Nebius transport. Not connected to task execution."""

import argparse
import asyncio
import json
import os
import re
from dataclasses import dataclass

import httpx

from sudo_x.provider import PlanEnvelope

ENDPOINT = "https://api.tokenfactory.nebius.com/v1/chat/completions"
MAX_RESPONSE_BYTES = 32768
TIMEOUT_SECONDS = 15
PROMPT = (
    "Synthetic SUDO X fixture: an imaginary lab service appeared on port 8080. "
    "There is no authorized target and no tool access. Return only a JSON object with "
    'version="1", capability_id="security.network_scan", action="blocked", arguments={}, '
    "and a short rationale explaining why an explicit scan scope is needed. "
    "Do not include commands, destinations, or private reasoning."
)


class ProbeError(ValueError):
    """Sanitized probe failure; never includes provider bodies or credentials."""


@dataclass(frozen=True)
class SyntheticProbe:
    model: str
    max_completion_tokens: int = 256

    def __post_init__(self):
        if not re.fullmatch(r"nvidia/[A-Za-z0-9._-]{1,120}", self.model):
            raise ProbeError("Select an NVIDIA model ID from your Nebius account's model list.")
        if (
            type(self.max_completion_tokens) is not int
            or not 1 <= self.max_completion_tokens <= 256
        ):
            raise ProbeError("Completion token budget must be between 1 and 256.")

    def payload(self) -> dict:
        return {
            "model": self.model,
            "messages": [{"role": "user", "content": PROMPT}],
            "max_completion_tokens": self.max_completion_tokens,
            "stream": False,
            "n": 1,
            "store": False,
        }

    def disclosure(self) -> dict:
        return {
            "provider": "nebius",
            "endpoint": ENDPOINT,
            "payload": self.payload(),
            "max_requests": 1,
            "timeout_seconds": TIMEOUT_SECONDS,
            "max_response_bytes": MAX_RESPONSE_BYTES,
            "tool_authority": False,
            "data_source": "fixed synthetic fixture; no machine observations or user files",
            "cost_usd": None,
            "cost_note": (
                "Cost is unknown. Confirm an account-side spending limit before sending. "
                "Token limits and timeouts are not dollar limits; a timed-out call may bill."
            ),
            "retention_note": "store=false is not proof of organization-level Zero Data Retention.",
        }

    async def send(
        self, *, api_key: str, approved: bool = False, account_spend_limit_confirmed: bool = False,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> dict:
        if approved is not True or account_spend_limit_confirmed is not True:
            raise ProbeError("Synthetic cloud disclosure and account spending limit need approval.")
        if not api_key.strip() or any(ord(char) < 33 or ord(char) > 126 for char in api_key):
            raise ProbeError("Configure NEBIUS_API_KEY securely in the local environment.")
        try:
            # No retries, redirects, environment proxies, or automatic tool dispatch.
            async with asyncio.timeout(TIMEOUT_SECONDS):
                async with httpx.AsyncClient(
                    transport=transport, timeout=TIMEOUT_SECONDS,
                    follow_redirects=False, trust_env=False,
                ) as client:
                    async with client.stream(
                        "POST", ENDPOINT, json=self.payload(),
                        headers={"Authorization": f"Bearer {api_key}"},
                    ) as response:
                        if response.status_code != 200:
                            raise ProbeError("Nebius rejected or failed the probe; no retry made.")
                        content = bytearray()
                        async for chunk in response.aiter_bytes():
                            content.extend(chunk)
                            if len(content) > MAX_RESPONSE_BYTES:
                                raise ProbeError("Nebius response exceeded the allowed size.")
            body = json.loads(content)
            if body.get("model") != self.model:
                raise ProbeError("Nebius returned an unexpected model identity.")
            choices = body["choices"]
            if len(choices) != 1 or choices[0]["finish_reason"] != "stop":
                raise ProbeError("Nebius did not return one complete response.")
            message = choices[0]["message"]
            if message.get("tool_calls") or message.get("function_call"):
                raise ProbeError("Tool calls are not accepted by the synthetic probe.")
            envelope = PlanEnvelope.model_validate_json(message["content"])
            if (
                envelope.capability_id != "security.network_scan"
                or envelope.action != "blocked" or envelope.arguments
            ):
                raise ProbeError("The synthetic response did not preserve the blocked boundary.")
            usage = body.get("usage")
            if usage is not None:
                usage = {key: usage[key] for key in (
                    "prompt_tokens", "completion_tokens", "total_tokens"
                )}
                if any(type(value) is not int or value < 0 for value in usage.values()):
                    raise ProbeError("Nebius returned invalid token usage.")
                if usage["completion_tokens"] > self.max_completion_tokens:
                    raise ProbeError("Nebius reported usage above the completion budget.")
                if usage["total_tokens"] != usage["prompt_tokens"] + usage["completion_tokens"]:
                    raise ProbeError("Nebius returned inconsistent token usage.")
            return {
                "provider": "nebius", "model": self.model,
                "envelope": envelope.model_dump(mode="json"),
                "usage": usage, "cost_usd": None, "tools_executed": 0,
            }
        except ProbeError:
            raise
        except (TimeoutError, httpx.HTTPError):
            raise ProbeError("Nebius probe timed out or failed; no retry made.") from None
        except (ValueError, KeyError, IndexError, TypeError, AttributeError):
            raise ProbeError("Nebius returned an invalid structured response.") from None


def main() -> None:
    parser = argparse.ArgumentParser(description="Preview a synthetic Nebius disclosure by default")
    parser.add_argument("--model", required=True, help="Exact NVIDIA model ID from your account")
    parser.add_argument("--max-completion-tokens", type=int, default=256)
    parser.add_argument("--send", action="store_true")
    parser.add_argument("--approve-synthetic-cloud", action="store_true")
    parser.add_argument("--confirm-account-spend-limit", action="store_true")
    args = parser.parse_args()
    try:
        probe = SyntheticProbe(args.model, args.max_completion_tokens)
        print(json.dumps(probe.disclosure(), indent=2))
        if args.send:
            result = asyncio.run(probe.send(
                api_key=os.environ.get("NEBIUS_API_KEY", ""),
                approved=args.approve_synthetic_cloud,
                account_spend_limit_confirmed=args.confirm_account_spend_limit,
            ))
            print(json.dumps(result, indent=2))
    except ProbeError as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
