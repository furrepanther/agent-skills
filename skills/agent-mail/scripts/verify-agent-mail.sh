#!/usr/bin/env bash
# Read-only preflight for the canonical Agent Mail CLI launcher.
set -euo pipefail

if [[ "$#" -ne 0 ]]; then
  printf '%s\n' 'usage: verify-agent-mail.sh' >&2
  exit 64
fi

script_dir="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
launcher="$script_dir/agent-mail"
if [[ ! -x "$launcher" ]]; then
  printf 'Agent Mail launcher is unavailable or not executable: %s\n' "$launcher" >&2
  exit 78
fi

exec "$launcher" --verify
