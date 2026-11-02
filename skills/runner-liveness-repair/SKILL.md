---
name: runner-liveness-repair
description: Review or change startup runners, watchdogs, coordinators, and repair paths when a slow process must be distinguished from a confirmed hang; prevents clock-only termination and duplicate replacement.
---

# Runner liveness and repair

Use this skill when changing or operating a long-lived runner, service
launcher, watchdog, startup coordinator, or automatic repair path on Datacube
or Primus.  It does not apply to an ordinary bounded HTTP/database request
unless that request timeout is used to terminate or replace a process.

This is the shared policy for every automatic runner: Memory Fabric, Mem0,
SimpleMem, MemWiki ingestion/indexing, document jobs, model services, and
future runners on either host.  A runner that has not been reviewed under this
policy may be inventoried, but it is not approved for a new automatic startup
chain.

## Required distinction

Classify every deadline before changing behavior:

- A **request deadline** bounds one probe or client call.  It may report an
  unknown result, but does not prove the server or worker stopped.
- An **observation deadline** bounds how long a caller waits for startup.
  When it expires, preserve the identified child, release the caller, and
  record/alert that startup remains pending.  Do not signal or replace it.
- A **repair action** is allowed only after affirmative hang evidence.  A
  failed health check or elapsed duration alone is not sufficient.

## Automatic-runner rules

- Never wrap a long-lived launcher, coordinator, service, model server, WSL
  process, or its process group in a timeout that can terminate it solely
  because time elapsed.
- Do not use `kill`, `pkill`, `SIGTERM`, `SIGKILL`, or a service restart as the
  automatic consequence of a startup/health deadline.
- Preserve an alive, identified slow process and refuse a duplicate launch.
  A slow process may need optimization; it is not by itself a termination
  condition.
- Keep bounded request probes for local health checks when they only bound the
  request.  Treat their result as one observation, not a stop/restart command.
- A manually authorized maintenance quiesce may use its separately reviewed
  procedure.  It must target an exact verified process and retain a receipt.

## Evidence before repair

Require all of the following before any repair/restart path is armed:

1. Exact process identity and ownership match the intended runner.
2. Multiple observations show no relevant forward progress (for example,
   heartbeat, queue advancement, expected work output, or validated health
   transition) across the declared observation window.
3. The repair path is idempotent, prevents a concurrent replacement, records
   the reason and prior PID/revision, and has a bounded post-repair check.
4. The action is within the caller's authority.  WSL shutdown/restart and
   model-server lifecycle changes require their own explicit authorization.

Use [the policy reference](references/runner-liveness-policy.md) for the
decision table, evidence receipt, and retirement rules.

## Shared-source rule

This skill lives in the shared `agent-skills` Git source.  Do not create a
home-local substitute.  Changes must be made in an isolated personal-fork
worktree under the local GitHub root and be usable from both Datacube and
Primus.
