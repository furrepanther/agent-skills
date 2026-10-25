# Evidence Packet

Use this reference when a Red-Team-Gate handoff needs to fit a lane ceiling or
when evidence must overflow to the approved temporary store.

## Required fields

Keep one machine-readable packet with:

- task id, owner, purpose, scope, lane ceiling, and stop/completion condition;
- exact base revision and each scoped path exactly once;
- typed provenance for every observation: source, observed time, selector,
  byte cap, line cap, and digest where applicable;
- candidate/capability decision records with `adopt`, `adapt`, `reject`, or
  `unknown`, plus evidence and proof-test references;
- finding records with id, locus, trigger, impact, evidence reference, action,
  disposition, owner, and rerun/acceptance evidence;
- `complete`, `provenance_verified`, `pointer_verified`, `cleanup_verified`,
  and empty-boat flags;
- a typed `PROVENANCE.gate_state` carrying structural result,
  functional-proof state, promotion decision, and explicit no-claim status.

## Compact overflow protocol

1. Construct and validate the complete packet before compaction. Keep the full
   packet in the existing approved temporary Memory-Fabric evidence path; never
   write directly to its backing database or create a second authority.
2. Verify the exact returned record id by lookup, and verify packet digest,
   content digest, scope, and base revision. Record bounded purge metadata:
   exact ids, maximum records/bytes, active-pointer condition, and the
   post-delete check.
3. Emit one compact index under the lane ceiling. It must preserve every path,
   required reviewer field, typed provenance, decision, finding id, and the
   verified pointer. Do not emit sequential fragments, truncation markers, or
   stringified provenance that changes its type. Entry digests must be full
   64-character values with an unambiguous label such as `entry_sha256_full`;
   preserve any declared `file_sha256_full` or `artifact_sha256_full` even if
   evidence excerpts are removed.
4. Delete only the named temporary ids after no active pointer refers to them.
   Enforce the record/byte cap, verify deletion by exact id, and retain the
   cleanup result. A failed or ambiguous check blocks promotion.

## Budget-preserving pointer retrieval

Use a two-layer exchange:

1. The reviewer receives one compact index containing the task id, owner,
   scope, base revision, exact temporary record id, full content and packet
   digests, required paths/decisions/findings, and the explicit promotion
   state. The index is the budgeted proof of identity and status, not a second
   copy of the full evidence.
2. The complete packet remains in one temporary record. If a reviewer needs
   substance, retrieve the exact record id first, verify its digest and
   generation, then select only the named field or bounded byte/line slice.
   Pointer lookup, metadata lookup, and content retrieval are separate steps;
   a pointer never authorizes a broad database scan.
3. Within one gate, deduplicate repeated pointer requests by exact id and
   verified digest. Re-fetch content only when the digest, generation, or
   requested field changes. Never place the full packet and the same packet's
   fragments into the same model context.
4. If the exact record, digest, generation, requested field, or bounded slice
   cannot be verified, return `unknown` and block promotion. Do not compensate
   by increasing the lane ceiling, reading the whole store/log, or splitting a
   structured entry into sequential fragments.

The budget invariant is: `compact index + fixed reviewer envelope <= lane
ceiling`; the full packet's size is a storage/retention concern, not a model
context allocation. A post-generation check must compare the emitted index's
content/packet digests with the pointer metadata, not merely trust a preflight
simulation.

## Logical continuation pages

When one complete packet cannot be understood from page zero, continue through
the verified pointer rather than expanding the model budget. Page zero carries
the task, owner, scope, base revision, parent packet digest, exact record ID,
generation, available selectors, cursor, and the per-page byte/line caps.
Each continuation request names the exact record ID, selector, cursor, and
generation. Each response returns the parent digest, page identity, page
digest, next cursor, and `complete` state; it must contain only the selected
bounded page.

The reviewer carries receipts, finding IDs, decisions, and page digests, not
all previously read page bodies. Duplicate requests are satisfied from a
verified task-local receipt. Missing, stale, out-of-order, over-cap, or
digest-mismatched pages produce `unknown` and block the gate; they do not
trigger an uncapped retry, whole-store read, or sequential fragment handoff.
Logical continuation is unbounded only until the task's explicit completion
condition is met. Storage, retention, per-page reads, concurrent requests,
cleanup, and retry counts remain bounded and auditable. Cleanup must honor
active pointer/receipt holds and verify zero live pointers before removal.

## Bounded observation

Every observation names exact source/task/selector, `byte_cap`, `line_cap`, and
`selection`; use bounded tail or task-id prefilter plus tail only. Whole-log,
uncapped, and broad reads are prohibited. Unless the runner supplies a lower
ceiling, the lane handoff is at most 7000 characters; each observation is at
most 65536 bytes and 100 lines, with a tail of at most 100 lines. The historical
3500-character handoff and intermediate 4000-character candidate remain
explicit rollback baselines during the compatibility gate. Never raise
observation caps; request a narrower slice or use the independent stop
condition.

## Tool and dependency execution

When execution needs a dependency or tool, use an isolated disposable local
environment; pin/record source, version, and hash; run bounded validation; do
not mutate the production interpreter or system packages. Production promotion
needs a separate currency, compatibility, and rollback gate. Correct and rerun
all findings, including warnings, or keep them explicit blocking unknowns; never
silently downgrade a warning.
