#!/bin/sh
set -eu
ROOT=$(dirname "$(readlink -f "$0")")
if [ ! -x "$ROOT/.venv/bin/sudo-x" ]; then
  printf '%s\n' 'The local environment is missing. Follow README.md setup instructions.' >&2
  exit 1
fi
if [ ! -f "$ROOT/ui/dist/index.html" ]; then
  printf '%s\n' 'The GUI is not built. Run npm ci and npm run build in ui/.' >&2
  exit 1
fi
exec "$ROOT/.venv/bin/sudo-x" --app "$@"
