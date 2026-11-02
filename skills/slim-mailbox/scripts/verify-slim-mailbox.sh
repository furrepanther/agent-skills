#!/usr/bin/env bash
# Read-only preflight for the installed SLIM mailbox launcher.
set -euo pipefail

if ! launcher="$(command -v slim-runner)"; then
  printf '%s\n' 'SLIM mailbox launcher is unavailable: slim-runner is not on PATH' >&2
  exit 78
fi

if [ ! -x "$launcher" ]; then
  printf 'SLIM mailbox launcher is not executable: %s\n' "$launcher" >&2
  exit 78
fi

resolved="$(readlink -f "$launcher")"
if [ ! -x "$resolved" ]; then
  printf 'SLIM mailbox launcher target is not executable: %s\n' "$resolved" >&2
  exit 78
fi

printf 'slim_mailbox_launcher=%s\n' "$resolved"
exec "$launcher" status
