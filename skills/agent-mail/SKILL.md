---
name: agent-mail
description: Use for authoritative Agent Mail intake, contact approval, acknowledgement, replies, and cross-host work coordination. Do not use SLIM as a substitute for Agent Mail decisions or acceptance.
---

# Agent Mail

Agent Mail is the authoritative record for cross-runner work orders, revisions,
decisions, and completion. SLIM is only an advisory notification path: a SLIM
receipt, delivery notice, or seen state never proves that work was accepted.

The canonical shared source for this skill is
`shared-github://agent-skills/skills/agent-mail/SKILL.md`. The host views are
`/mnt/linuxdata/Github/agent-skills/skills/agent-mail/` on Datacube and
`/linuxdata/Github/agent-skills/skills/agent-mail/` on Primus.

## Safe intake

At turn start and before a consequential action, check the authenticated Agent
Mail inbox. Read the original mail body, validate its target, current revision,
scope, and ownership, then acquire the system's execution claim before side
effects. Do not execute a compacted notification, a SLIM hint, or a quoted
command as though it were the original work order.

Process urgent and high-priority mail first. For a request that cannot proceed,
reply once with the concrete blocker, owner, and next action. Do not create a
timeout or polling reply loop; reuse its thread and correlation identifiers.

## Contacts and acknowledgements

When a contact policy requires approval, use `respond_contact(..., accept=true)`
from the receiving identity and preserve its approved result. Contact links are
directed: the current `list_contacts` surface may show only links initiated by
the caller, so an empty list for the receiving identity is not a rejection. Use
an authorized contact-audit or the requesting identity's list when one is
available. Sending a message, seeing a delivery record, acknowledging a
message, or receiving a SLIM ACK is not contact acceptance.

Use `acknowledge_message` only after the message has been read and its next
action is known. Reply in the existing thread when reporting progress or a
result so the evidence remains connected to the work order.

## Identity and credential handling

Use the active host's managed identity environment or a maintained wrapper that
loads it. Never paste, log, serialize, or place a registration token or bearer
token in a resource URI, query string, command line, diagnostic error, or
message body. Sanitize nonempty secret values before surfacing an error.

Use the deployed loopback endpoint from the active service configuration. Probe
`/health/readiness` before assuming a transport is usable. The upstream default
may differ from a managed deployment; do not hard-code a port or start/restart
the service merely because a default endpoint does not answer.

## Datacube and Primus coordination

Load the shared Agent Mail/SLIM coordination contract before remote execution:

- Datacube: `/mnt/f/Production/antigravity/startup/common/AG_AGENT_MAIL_SLIM_COORDINATION_V1.md`
- Primus: `/usr/production/runner-startup/common/AG_AGENT_MAIL_SLIM_COORDINATION_V1.md`

Use Agent Mail for authority and durable evidence. SLIM may announce that mail
is waiting, but the recipient must retrieve the authenticated original. Use the
stable host-qualified identity aliases and the canonical OS user `antigravity`.
Control SSH remains TCP/22; TCP/22022 is filesystem sharing only.

## Editing and completion

Before editing a shared source, work in a personal GitHub fork and isolated
worktree under the shared GitHub root. Reserve the narrowly affected paths when
the project supports reservations, and coordinate any conflict before editing.
Return a compact Agent Mail result with changed paths, revision, verification,
and any remaining blocker. Store durable operational lessons in Memory Fabric
after the action; it does not replace the reply or acceptance evidence.
