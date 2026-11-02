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

# Datacube has one canonical deployed mailbox launcher.  Accepting a different
# executable merely because it is named ``slim-runner`` would reintroduce the
# path drift this preflight exists to prevent.  Primus intentionally uses its
# own host-installed launcher, so only the Datacube side has a fixed path.
host_name="$(hostname -s 2>/dev/null | tr '[:upper:]' '[:lower:]')"
case "$host_name" in
  datacube*)
    canonical_datacube_launcher="/mnt/f/Production/antigravity/slim-runner"
    if [ "$resolved" != "$canonical_datacube_launcher" ]; then
      printf 'SLIM mailbox launcher drift on Datacube: expected %s, got %s\n' \
        "$canonical_datacube_launcher" "$resolved" >&2
      exit 78
    fi
    ;;
esac

printf 'slim_mailbox_launcher=%s\n' "$resolved"
if ! status_payload="$("$launcher" status)"; then
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
