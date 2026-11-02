# Runner liveness and repair policy

## Decision table

| Situation | Automatic action | Prohibited action |
| --- | --- | --- |
| A health/request probe reaches its own deadline | Record the unknown/failed probe and continue observation. | Treating the probe deadline as proof the server stopped. |
| A newly launched runner is still alive but not ready by the caller's observation deadline | Release the caller as pending/degraded, retain the exact PID, and prevent a duplicate start. | Signaling or replacing the runner because the clock expired. |
| A runner is identified and has no verified progress across repeated observations | Produce a repair receipt and use the reviewed, authorized repair path. | Killing a broad process pattern, escalating to SIGKILL, or restarting WSL/model servers as an automatic fallback. |
| A planned promotion requires quiescence | Use the specifically approved quiesce procedure and preserve its receipt/snapshot evidence. | Reusing a watchdog timeout or an unrelated stop script. |

## Minimum repair receipt

Record the runner name, canonical source revision, exact PID and owner,
observations and timestamps, progress signals examined, decision, repair
operator/authority, post-repair result, and rollback/recovery location.  The
change-tracking database is the preferred durable destination once available.

## Validation

- Add a fixture in which a child remains alive and becomes healthy slowly; the
  launcher must not signal it because an observation deadline expires.
- Test that an existing listener is never replaced without identity proof.
- Test that request-level timeouts do not invoke a process-control path.
- Keep a static inventory of automatic runners.  Classify explicit operator
  stop tools separately rather than silently exempting them.

## Retirement and drift containment

After a replacement path is promoted and verified, inventory every old
launcher/coordinator/helper with its digest, source revision, active caller
scan, and process scan.  Archive a manifest and rollback reference first.
Delete only artifacts proven inactive and unreferenced.  Never delete dirty
user worktrees or active production sources during this cleanup.
