"""Temporary test server. Never use the public fixture token for a real session."""

import os
import tempfile

import uvicorn

from sudo_x.api import create_app

if __name__ == "__main__":
    with tempfile.TemporaryDirectory(prefix="sudo-x-e2e-") as directory:
        os.environ["SUDOX_DATA_DIR"] = directory
        uvicorn.run(
            create_app(token="test-fixture-token-not-for-real-use-00001"),
            host="127.0.0.1", port=8766, access_log=False, log_level="warning",
            proxy_headers=False,
        )
