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
exec "$launcher" status
