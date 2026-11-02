#!/usr/bin/env bash
# Narrow behavioral checks for install-mailbox-cli-launchers.sh.
set -euo pipefail

script_dir="$(CDPATH= cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
installer="$script_dir/install-mailbox-cli-launchers.sh"
repo_root="$(CDPATH= cd -- "$script_dir/.." && pwd -P)"
test_root="$(mktemp -d "${TMPDIR:-/tmp}/agent-skills-mailbox-launchers.XXXXXX")"

cleanup() {
  set +e
  [ -L "$test_root/bin/agent-mail" ] && unlink "$test_root/bin/agent-mail"
  [ -L "$test_root/bin/slim-mailbox" ] && unlink "$test_root/bin/slim-mailbox"
  [ -L "$test_root/home/.local/bin/agent-mail" ] && unlink "$test_root/home/.local/bin/agent-mail"
  [ -L "$test_root/home/.local/bin/slim-mailbox" ] && unlink "$test_root/home/.local/bin/slim-mailbox"
  [ -L "$test_root/race/agent-mail" ] && unlink "$test_root/race/agent-mail"
  [ -L "$test_root/race/slim-mailbox" ] && unlink "$test_root/race/slim-mailbox"
  [ -f "$test_root/conflict/agent-mail" ] && unlink "$test_root/conflict/agent-mail"
  rmdir "$test_root/bin" "$test_root/home/.local/bin" "$test_root/home/.local" \
    "$test_root/home" "$test_root/race" "$test_root/conflict" "$test_root" 2>/dev/null
}
trap cleanup EXIT

"$installer" --target-dir "$test_root/bin" --dry-run
[ ! -e "$test_root/bin" ]

"$installer" --target-dir "$test_root/bin"
"$installer" --target-dir "$test_root/bin" --verify

[ "$(readlink -f "$test_root/bin/agent-mail")" = "$repo_root/skills/agent-mail/scripts/agent-mail" ]
[ "$(readlink -f "$test_root/bin/slim-mailbox")" = "$repo_root/skills/slim-mailbox/scripts/slim-mailbox" ]

HOME="$test_root/home" "$installer"
HOME="$test_root/home" "$installer" --verify
[ "$(readlink -f "$test_root/home/.local/bin/agent-mail")" = "$repo_root/skills/agent-mail/scripts/agent-mail" ]
[ "$(readlink -f "$test_root/home/.local/bin/slim-mailbox")" = "$repo_root/skills/slim-mailbox/scripts/slim-mailbox" ]

set +e
"$installer" --target-dir "$test_root/race" &
first_install_pid=$!
"$installer" --target-dir "$test_root/race" &
second_install_pid=$!
wait "$first_install_pid"
first_install_status=$?
wait "$second_install_pid"
second_install_status=$?
set -e
[ "$first_install_status" -eq 0 ]
[ "$second_install_status" -eq 0 ]
"$installer" --target-dir "$test_root/race" --verify

mkdir "$test_root/conflict"
: > "$test_root/conflict/agent-mail"
set +e
"$installer" --target-dir "$test_root/conflict" >/dev/null 2>&1
conflict_status=$?
set -e
[ "$conflict_status" -eq 73 ]
[ ! -e "$test_root/conflict/slim-mailbox" ]

printf '%s\n' 'install-mailbox-cli-launchers tests passed'
