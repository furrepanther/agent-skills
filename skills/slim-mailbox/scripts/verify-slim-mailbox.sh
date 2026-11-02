#!/usr/bin/env bash
# Read-only preflight for the installed SLIM mailbox launcher.
set -euo pipefail

usage() {
  printf '%s\n' 'usage: verify-slim-mailbox.sh [--require-configured-peer PEER]' >&2
}

required_peer=""
case "$#" in
  0)
    ;;
  2)
    if [ "$1" = "--require-configured-peer" ] && [ -n "$2" ]; then
      required_peer="$2"
    else
      usage
      exit 64
    fi
    ;;
  *)
    usage
    exit 64
    ;;
esac

script_dir="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
mailbox_helper="$script_dir/slim-mailbox"
if [ ! -x "$mailbox_helper" ]; then
  printf 'SLIM mailbox helper is unavailable or not executable: %s\n' "$mailbox_helper" >&2
  exit 78
fi

if ! launcher="$("$mailbox_helper" --launcher-path)"; then
  printf '%s\n' 'SLIM mailbox helper could not resolve its launcher' >&2
  exit 78
fi

printf 'slim_mailbox_launcher=%s\n' "$launcher"
if ! status_payload="$("$mailbox_helper" status)"; then
  printf '%s\n' 'SLIM mailbox launcher failed its status request' >&2
  exit 78
fi
printf '%s\n' "$status_payload"

if [ -n "$required_peer" ]; then
  if ! command -v jq >/dev/null 2>&1; then
    printf '%s\n' 'SLIM mailbox peer preflight requires jq' >&2
    exit 78
  fi
  if ! printf '%s\n' "$status_payload" | jq -e --arg peer "$required_peer" \
    '.ok == true and (.peers | type == "array") and (.peers | index($peer) != null)' \
    >/dev/null; then
    printf 'SLIM mailbox peer is not configured: %s\n' "$required_peer" >&2
    exit 69
  fi
fi
