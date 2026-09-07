import argparse
import asyncio
import os
import shutil
import socket
import subprocess
import webbrowser

import uvicorn

from sudo_x.api import create_app, session_token


def main() -> None:
    parser = argparse.ArgumentParser(description="SUDO X normal-user loopback-only local backend")
    parser.add_argument("--port", type=int, default=8765, help="Loopback TCP port (default: 8765)")
    parser.add_argument(
        "--open", action="store_true", help="Open the local session in your browser"
    )
    parser.add_argument(
        "--app", action="store_true",
        help="Open a standalone Chromium app window (falls back to the default browser)",
    )
    args = parser.parse_args()
    if os.getuid() == 0 or os.geteuid() == 0:
        parser.error("Run sudo-x as your normal user, never with sudo/root.")
    if not 1 <= args.port <= 65535:
        parser.error("--port must be between 1 and 65535.")
    try:
        token = session_token()
    except ValueError as exc:
        parser.error(str(exc))
    url = f"http://127.0.0.1:{args.port}/#token={token}"

    class LocalServer(uvicorn.Server):
        async def startup(self, sockets=None):
            await super().startup(sockets=sockets)
            if not self.started:
                return
            # Print once, locally, after startup succeeds. Fragments never enter HTTP requests.
            print(f"SUDO X local session (private; do not share):\n{url}", flush=True)
            if args.app:
                browser = shutil.which("chromium") or shutil.which("chromium-browser")
                if browser:
                    try:
                        subprocess.Popen(
                            [browser, f"--app={url}", "--new-window"],
                            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                        )
                        return
                    except OSError:
                        pass
            if args.open or args.app:
                try:
                    opened = await asyncio.to_thread(webbrowser.open, url)
                except webbrowser.Error:
                    opened = False
                if not opened:
                    print("Browser did not open; use the local session URL above.", flush=True)

    config = uvicorn.Config(
        create_app(token=token), host="127.0.0.1", port=args.port,
        access_log=False, proxy_headers=False, server_header=False,
        log_level="warning", workers=1,
    )
    # Bind ourselves so port conflicts fail before printing a credential or opening a browser.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        try:
            listener.bind(("127.0.0.1", args.port))
            listener.listen(128)
        except OSError:
            parser.error("Cannot bind the selected loopback port; choose a free unprivileged port.")
        LocalServer(config).run(sockets=[listener])
