#!/usr/bin/env bash
# Install or verify the shared Agent Mail and SLIM mailbox CLI entrypoints.
# This is a user-level helper only: it never starts, stops, or edits services.
set -euo pipefail

usage() {
  printf '%s\n' \
    'usage: install-mailbox-cli-launchers.sh [--target-dir ABSOLUTE_DIRECTORY] [--dry-run | --verify]'
}

target_dir=''
mode='install'

while [ "$#" -gt 0 ]; do
  case "$1" in
    --target-dir)
      if [ "$#" -lt 2 ] || [ -z "$2" ]; then
        usage >&2
        exit 64
      fi
      target_dir="$2"
      shift 2
      ;;
    --dry-run)
      if [ "$mode" != 'install' ]; then
        usage >&2
        exit 64
      fi
      mode='dry-run'
      shift
      ;;
    --verify)
      if [ "$mode" != 'install' ]; then
        usage >&2
        exit 64
      fi
      mode='verify'
      shift
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      usage >&2
      exit 64
      ;;
  esac
done

if [ -z "$target_dir" ]; then
  if [ -z "${HOME:-}" ]; then
    printf '%s\n' 'HOME is required when --target-dir is omitted' >&2
    exit 64
  fi
  target_dir="$HOME/.local/bin"
fi

case "$target_dir" in
  /*)
    ;;
  *)
    printf 'target directory must be absolute: %s\n' "$target_dir" >&2
    exit 64
    ;;
esac

script_dir="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
repo_root="$(CDPATH= cd -- "$script_dir/.." && pwd -P)"

launcher_names=(agent-mail slim-mailbox)
launcher_candidates=(
  "$repo_root/skills/agent-mail/scripts/agent-mail"
  "$repo_root/skills/slim-mailbox/scripts/slim-mailbox"
)
launcher_sources=()

for candidate in "${launcher_candidates[@]}"; do
  if [ ! -x "$candidate" ]; then
    printf 'shared launcher is unavailable or not executable: %s\n' "$candidate" >&2
    exit 78
  fi
  launcher_sources+=("$(readlink -f -- "$candidate")")
done

if [ "$mode" = 'verify' ]; then
  if [ ! -d "$target_dir" ]; then
    printf 'launcher target directory is unavailable: %s\n' "$target_dir" >&2
    exit 78
  fi
elif [ "$mode" != 'dry-run' ]; then
  mkdir -p -- "$target_dir"
fi

if [ -e "$target_dir" ] && [ ! -d "$target_dir" ]; then
  printf 'launcher target is not a directory: %s\n' "$target_dir" >&2
  exit 73
fi

if [ -d "$target_dir" ]; then
  target_dir="$(readlink -f -- "$target_dir")"
else
  target_dir="$(readlink -m -- "$target_dir")"
fi

actions=()
has_conflict=false
has_missing=false

for index in "${!launcher_names[@]}"; do
  name="${launcher_names[$index]}"
  source_path="${launcher_sources[$index]}"
  target_path="$target_dir/$name"

  if [ -L "$target_path" ]; then
    resolved_target="$(readlink -f -- "$target_path" 2>/dev/null || true)"
    if [ "$resolved_target" = "$source_path" ]; then
      actions+=(already)
    else
      printf 'launcher target conflicts with canonical source: %s\n' "$target_path" >&2
      has_conflict=true
      actions+=(conflict)
    fi
  elif [ -e "$target_path" ]; then
    printf 'launcher target already exists and is not the canonical symlink: %s\n' "$target_path" >&2
    has_conflict=true
    actions+=(conflict)
  else
    actions+=(missing)
    has_missing=true
  fi
done

if [ "$has_conflict" = true ]; then
  exit 73
fi

if [ "$mode" = 'verify' ]; then
  if [ "$has_missing" = true ]; then
    for index in "${!launcher_names[@]}"; do
      if [ "${actions[$index]}" = missing ]; then
        printf 'canonical launcher is not installed: %s\n' "$target_dir/${launcher_names[$index]}" >&2
      fi
    done
    exit 78
  fi
  for index in "${!launcher_names[@]}"; do
    printf 'launcher_verified=%s\n' "$target_dir/${launcher_names[$index]}"
  done
  exit 0
fi

for index in "${!launcher_names[@]}"; do
  name="${launcher_names[$index]}"
  source_path="${launcher_sources[$index]}"
  target_path="$target_dir/$name"
  case "${actions[$index]}" in
    already)
      printf 'launcher_already_installed=%s\n' "$target_path"
      ;;
    missing)
      if [ "$mode" = 'dry-run' ]; then
        printf 'launcher_would_install=%s -> %s\n' "$target_path" "$source_path"
      else
        if ln -s -- "$source_path" "$target_path" 2>/dev/null; then
          printf 'launcher_installed=%s -> %s\n' "$target_path" "$source_path"
        else
          resolved_target="$(readlink -f -- "$target_path" 2>/dev/null || true)"
          if [ -L "$target_path" ] && [ "$resolved_target" = "$source_path" ]; then
            printf 'launcher_installed_concurrently=%s\n' "$target_path"
          else
            printf 'launcher installation failed or target changed: %s\n' "$target_path" >&2
            exit 73
          fi
        fi
      fi
      ;;
  esac
done
