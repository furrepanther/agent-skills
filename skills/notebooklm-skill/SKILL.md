---
name: notebooklm
description: Use when querying or managing Google NotebookLM content in Antigravity using production nlm/notebooklm-mcp interfaces. Prefer CLI for throughput and MCP for orchestrated multi-step tool flows.
---

# NotebookLM Production Skill

This skill is aligned to the current Antigravity production connector:
- CLI: `nlm`
- MCP server: `notebooklm-mcp`
- Runtime bootstrap: Antigravity WSL scripts

Legacy `scripts/run.py` workflows are deprecated for this environment.

## When To Use

Use this skill when the user asks to:
- query NotebookLM notebooks or sources
- manage notebooks/sources/notes
- generate or download NotebookLM artifacts
- export artifacts to Google Docs/Sheets
- use NotebookLM through MCP in Gemini/Codex/Claude

## Interface Selection (Performance Rule)

- Use CLI first for speed and throughput:
  - lower per-call overhead
  - best for repeated commands and batch operations
- Use MCP for orchestration:
  - better for multi-step agentic tool flows
  - structured tool responses across runner boundaries

Default policy:
- Start in CLI.
- Escalate to MCP only when the task needs orchestration/tool-chaining.

## Canonical Paths (Antigravity)

- Runtime setup:
  - `/mnt/c/Users/furre/.gemini/antigravity/scripts/setup_notebooklm_mcp.sh`
- Native login wrapper:
  - `/mnt/c/Users/furre/.gemini/antigravity/scripts/notebooklm_native_login.sh`
- MCP entrypoint:
  - `/mnt/c/Users/furre/.gemini/antigravity/scripts/mcp_wsl_entrypoint.sh`
- Pinned CLI binaries:
  - `/home/billw/.venv-notebooklm-cli/bin/nlm`
  - `/home/billw/.venv-notebooklm-cli/bin/notebooklm-mcp`

## Setup And Health Checks

```bash
/mnt/c/Users/furre/.gemini/antigravity/scripts/setup_notebooklm_mcp.sh
/home/billw/.venv-notebooklm-cli/bin/nlm doctor
```

## Authentication (Production Flow)

1. Check auth:
```bash
/home/billw/.venv-notebooklm-cli/bin/nlm login --check
```

2. Native login (preferred):
```bash
/mnt/c/Users/furre/.gemini/antigravity/scripts/notebooklm_native_login.sh
```

3. Approved fallback (if native browser path fails in this host):
```bash
/home/billw/.venv-notebooklm-cli/bin/nlm login --provider openclaw --cdp-url http://127.0.0.1:18800
```

4. Validate session:
```bash
/home/billw/.venv-notebooklm-cli/bin/nlm notebook list
```

## CLI Quick Operations

### Notebook management
```bash
/home/billw/.venv-notebooklm-cli/bin/nlm notebook list
/home/billw/.venv-notebooklm-cli/bin/nlm notebook create "Research Notebook"
/home/billw/.venv-notebooklm-cli/bin/nlm notebook get <notebook_id>
/home/billw/.venv-notebooklm-cli/bin/nlm notebook rename <notebook_id> "New Title"
```

### Source management
```bash
/home/billw/.venv-notebooklm-cli/bin/nlm source list <notebook_id>
/home/billw/.venv-notebooklm-cli/bin/nlm source add <notebook_id> --url https://example.com --wait
/home/billw/.venv-notebooklm-cli/bin/nlm source add <notebook_id> --file /path/doc.pdf --wait
/home/billw/.venv-notebooklm-cli/bin/nlm source content <source_id>
```

### Query (source-grounded)
```bash
/home/billw/.venv-notebooklm-cli/bin/nlm notebook query <notebook_id> "Question here"
/home/billw/.venv-notebooklm-cli/bin/nlm notebook query <notebook_id> "Follow-up question" --conversation-id <conversation_id>
```

### Notes
```bash
/home/billw/.venv-notebooklm-cli/bin/nlm note list <notebook_id>
/home/billw/.venv-notebooklm-cli/bin/nlm note create <notebook_id> --title "Summary" --content "..."
```

### Research
```bash
/home/billw/.venv-notebooklm-cli/bin/nlm research start "query text" --source web --mode fast --notebook-id <notebook_id>
/home/billw/.venv-notebooklm-cli/bin/nlm research status <task_id>
/home/billw/.venv-notebooklm-cli/bin/nlm research import <task_id>
```

### Artifact generation
```bash
/home/billw/.venv-notebooklm-cli/bin/nlm audio create <notebook_id>
/home/billw/.venv-notebooklm-cli/bin/nlm report create <notebook_id>
/home/billw/.venv-notebooklm-cli/bin/nlm slides create <notebook_id>
/home/billw/.venv-notebooklm-cli/bin/nlm studio status <notebook_id>
```

### Artifact download/export
```bash
/home/billw/.venv-notebooklm-cli/bin/nlm download audio <notebook_id> --output ./podcast.m4a
/home/billw/.venv-notebooklm-cli/bin/nlm export artifact <notebook_id> <artifact_id> --type docs
```

### Sharing
```bash
/home/billw/.venv-notebooklm-cli/bin/nlm share status <notebook_id>
/home/billw/.venv-notebooklm-cli/bin/nlm share public <notebook_id>
/home/billw/.venv-notebooklm-cli/bin/nlm share invite <notebook_id> --email user@example.com
```

## MCP Mode (When Needed)

Use MCP only for orchestration-heavy tasks. In this environment, `notebooklm_cli`
is already mapped through the canonical WSL entrypoint.

If reconfiguration is needed:
```bash
/home/billw/.venv-notebooklm-cli/bin/nlm setup add antigravity
```

## Operational Rules

- Prefer CLI for direct NotebookLM work.
- Keep destructive actions explicit and confirmed.
- Do not claim completion without command output.
- If auth fails, run `nlm doctor` and re-authenticate.

## Common Failures

- `Profile 'default' not found`: run native login wrapper.
- `Cannot connect to CDP endpoint`: use native login first; fallback to approved `openclaw` only if needed.
- Stale auth after login: run `nlm login --check` then retry the command.
