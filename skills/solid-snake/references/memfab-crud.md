# Solid Snake Memory Fabric CRUD

Use this reference when Solid Snake needs durable learning or audit write-back.

## Scope

Use Memory Fabric for durable knowledge:

- root causes and durable fixes
- changed files plus why they changed
- reusable troubleshooting evidence
- skill, prompt, or workflow lineage
- standing decisions and operator preferences

Do not use Memory Fabric for secrets, high-volume telemetry, process lifecycle events, test-job spam, raw logs, or one-off observations with no reuse value.

## Access

Use the host's sanctioned Memory Fabric/MemWiki front door:

- Prefer the host's MCP tools: `memory_retrieve`, `memory_query`, `memory_search`, `memory_store`, or `memory_write`.
- On Primus, the bounded API tunnel is `http://127.0.0.1:18001` with `GET /health`, `POST /search`, `POST /memory/write`, `POST /memory/update`, and `POST /memory/delete`.
- On Datacube, use its canonical local MCP/API front door as documented by that host; do not guess a port or bypass the service boundary.
- Never read or write the peer's Memory Fabric database files directly.
- Use REST only when sanctioned MCP tools are unavailable in the current runner.

## Read/Search

Search before writing so Snake extends the existing knowledge graph instead of spraying duplicates.

```bash
curl -sS http://127.0.0.1:18001/search \
  -H 'Content-Type: application/json' \
  -d '{"query":"solid snake concurrency memory fabric skill","limit":5,"user_id":"global","force_exact":false}'
```

Use exact handles, skill names, file paths, component names, or failure signatures when available. Treat a failed or empty search as a fact to report, not permission to invent prior context.

## Create

Write concise durable notes with provenance. Include enough context for a future agent to decide whether the knowledge still applies.

```bash
curl -sS http://127.0.0.1:18001/memory/write \
  -H 'Content-Type: application/json' \
  -d '{
    "user_id": "global",
    "title": "Solid Snake durable lesson: <short title>",
    "content": "<fact-rich durable note>",
    "source": "solid-snake",
    "origin_tool": "solid-snake",
    "artifact_kind": "memory_note",
    "metadata": {
      "source_runner": "Primus",
      "source_tool": "solid-snake",
      "repo_or_system": "<repo-or-system>",
      "component": "<component>",
      "category": "lesson_learned",
      "tags": ["solid-snake", "debugging"],
      "changed_files": [],
      "verification": "<commands, review ids, or evidence refs>",
      "observed_at_utc": "<ISO-8601 UTC timestamp>"
    }
  }'
```

## Update

Update only when the target `memory_id` or `entry_id` is known and the new text supersedes or sharpens the old record. Do not overwrite a useful historical note just because a newer note exists; link or supersede when history matters.

```bash
curl -sS http://127.0.0.1:18001/memory/update \
  -H 'Content-Type: application/json' \
  -d '{
    "memory_id": "<memory-id>",
    "user_id": "global",
    "content": "<updated durable content>",
    "origin_tool": "solid-snake",
    "metadata": {
      "update_reason": "<why this update is valid>",
      "verification": "<evidence>"
    }
  }'
```

## Delete

Delete only when a record is clearly wrong, secret-bearing, duplicate garbage, or unsafe to retain. Preserve an audit reason. Prefer updating or superseding when the old record has historical value.

```bash
curl -sS http://127.0.0.1:18001/memory/delete \
  -H 'Content-Type: application/json' \
  -d '{
    "memory_id": "<memory-id>",
    "user_id": "global",
    "reason": "<specific deletion reason>",
    "origin_tool": "solid-snake",
    "metadata": {
      "source_runner": "Primus",
      "source_tool": "solid-snake"
    }
  }'
```

## Concurrency Memory Checklist

When storing knowledge about multithreading or multiuser bugs, include:

- the shared resource and every owner allowed to mutate it
- lock, event, stream, queue, or transaction ordering assumptions
- thread-local versus process-global state boundaries
- partial-failure behavior and cleanup path
- how the failure becomes visible instead of silently poisoning later work
- the smallest probe that proved or would prove the claim
