# Evidence Packet

Use this reference when a Red-Team-Gate handoff needs to fit a lane ceiling or
when evidence must overflow to the approved temporary store.

## Required fields

Keep one machine-readable packet with:

- task id, owner, purpose, scope, lane ceiling, and stop/completion condition;
- `TASK` as a non-empty string; `ACCEPTANCE_CRITERIA` as a non-empty list of
  unique string/object criteria; `TESTS`, `KNOWN_CONSTRAINTS`, and
  `OUT_OF_SCOPE` as non-empty string lists; and `PROVENANCE` identity/revision/
  time fields and artifact references as strings;
- exact base revision and each scoped path exactly once;
- a non-empty typed `EVIDENCE` list with unique record ids and criterion ids;
  every record names `test_or_locus`, `input_boundary`, `observed_outcome`, a
  `status` of `pass`, `fail`, or `unknown`, and an exact artifact reference (or
  explicit `inline:<source>` reference);
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
- When cleanup is in scope, provide draft-only
  `PROVENANCE.cleanup_proof` with `status=pass`, an exact or inline receipt
  reference, full receipt digest, exact target, observed-absence paths,
  positive record/byte caps, passing active-pointer/post-delete checks, and a
  zero-entry recursive-tree check.
  The builder derives `cleanup_verified`; callers may not forge that flag.

## Construction barrier

Build the packet from a typed draft through one shared builder. The only valid
states are `draft`, `normalized`, `validated`, `attested`, and `serialized`;
only the final serialized result may be dispatched. Reject drafts that contain
builder-owned attestation flags, digests, or `PROVENANCE.gate_state`, and never
edit an attested JSON document in place. A changed source, path, revision,
artifact, or evidence record requires a new build and new digests.

Do not rely on permissive JSON coercion: a number/object in a text field or an
untyped artifact reference is a construction error. The builder must reject it
before setting any attestation flag.

When the review package does not provide its own builder, use the skill-local
dependency-free fallback `scripts/review_packet_builder.py` and its executable
`scripts/test_review_packet_builder.py` regression suite. Pass only the builder
output to the review wrapper. A fallback preflight is not evidence that the
wrapper independently enforces the same contract; that missing integration is
a blocker for any claim of wrapper-level rejection. This skill-only fallback
does not modify a production wrapper; wrapper integration is a separate change
with its own tests and review. When full artifacts exceed the inline ceiling,
the builder marks `PROVENANCE.pointer_required=true`; the wrapper must hydrate
and verify the exact pointer before dispatching any lane.

Before dispatch, the builder must reject duplicate criterion/evidence IDs and
paths, missing criterion coverage, alias-only fields, inconsistent revision or
source identity, malformed or mismatched full digests, artifact reference or
size mismatches, and any `unknown` evidence that lacks an explicit blocker and
no-claim state. It must run schema, semantic-coverage, provenance/digest,
artifact-byte, and serialized-wire-size checks in that order. Any warning or
error is a hard dispatch barrier: make zero reviewer/router calls, report the
failed check, and regenerate from the corrected draft rather than retrying the
same packet.

Every path in `DIFF_OR_FILES` must also appear in
`PROVENANCE.artifact_refs`; inline criterion evidence does not replace
provenance for the reviewed file scope.

Inline packets must include the reviewable bytes: each `DIFF_OR_FILES` entry
must carry a non-empty `diff` or `content` string. Path-only entries are
allowed only with matching `FULL_ARTIFACTS` containing the complete
`content` whose full digest is verified against `file_sha256_full`, plus the
wrapper's verified pointer-backed transport when the packet is too large for
the lane.

The regression suite must exercise the real builder/wrapper boundary with
invalid missing/alias-only fields, wrong types, duplicate IDs/paths,
criterion-without-evidence, contradictory statuses, caller-forced attestation,
bad or mismatched digests, artifact mismatch, stale revision/identity, Unicode
and envelope overflow, plus one valid packet. Assert zero downstream calls for
every invalid case and exact typed-field/wire-digest preservation for the valid
case.

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
   complete `EVIDENCE` record (including criterion id, status, boundary,
   outcome, and artifact reference), plus the verified pointer. Do not emit sequential fragments, truncation markers, or
   stringified provenance that changes its type. Entry digests must be full
   64-character values with an unambiguous label such as `entry_sha256_full`;
   preserve any declared `file_sha256_full` or `artifact_sha256_full` even if
   evidence excerpts are removed.
4. Delete only the named temporary ids after no active pointer refers to them.
   Enforce the record/byte cap, verify deletion by exact id, and retain the
   cleanup result. A failed or ambiguous check blocks promotion.
5. Test the actual packet construction/dispatch boundary for every active lane
   ceiling. An in-bound serialized packet must be eligible for dispatch; an
   over-bound packet must fail before router dispatch. Configuration-only
   consistency checks are insufficient because envelope fields and Unicode
   serialization can change the wire size.

## Budget-preserving pointer retrieval

Use a two-layer exchange:

1. The reviewer receives one compact index containing the task id, owner,
   scope, base revision, exact temporary record id, full content and packet
   digests, required paths/decisions/findings, and the explicit promotion
   state. The index is the budgeted proof of identity and status, not a second
   copy of the full evidence.
2. The complete packet remains in one temporary record. For the evidence
   needed to decide, retrieve the exact record id, verify its digest and
   generation, then deliver the named field or bounded byte/line slice to the
   reviewer. Prove reviewer receipt; producer-side verification alone is not
   reviewer access. If required evidence cannot be delivered or receipt cannot
   be established, return `insufficient_evidence` and block promotion.
   Pointer lookup, metadata lookup, and content retrieval are separate steps;
   a pointer never authorizes a broad database scan.
3. Within one gate, deduplicate repeated pointer requests by exact id and
   verified digest. Re-fetch content only when the digest, generation, or
   requested field changes. Never place the full packet and the same packet's
   fragments into the same model context.
   The typed per-file source receipt uses `file_sample_bytes_per_file` for
   the bounded sample cap and `file_sample_total_bytes` for the measured
   aggregate. These are distinct quantities; a reviewer must not interpret a
   per-file cap as the total delivered byte count. Router-owned junior 4B
   delegation for light work is allowed, but it is not direct gate evidence
   and its counters are not a pass/fail condition.
   In the 12,000-character compatibility tier, the lane handoff may carry one
   verified source page and a byte-bounded sample ledger. Each sample is keyed
   to the complete evidence-index order; the receiver must reconstruct the
   exact path, enforce the declared byte cap, and verify coverage/digests. The
receipt also carries compact `file_sha256_full` digest strings in the same path
order, proving the complete artifact digest for every sampled path. Older
path-plus-digest object rows remain accepted for compatibility. This is an access proof for
   the bounded handoff, not a replacement for the full pointer-backed source
   bytes.
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
ceiling, the active lane handoff is at most 16384 characters; 12000 characters
is the validated compatibility tier. Each observation is at most 65536 bytes
and 100 lines, with a tail of at most 100 lines. The historical 3500-character
handoff, intermediate 4000-character candidate, and prior 7000-character
compatibility ceiling remain explicit rollback baselines. Never raise
observation caps; request a narrower slice or use the independent stop
condition.

## Tool and dependency execution

When execution needs a dependency or tool, use an isolated disposable local
environment; pin/record source, version, and hash; run bounded validation; do
not mutate the production interpreter or system packages. Production promotion
needs a separate currency, compatibility, and rollback gate. Correct and rerun
all findings, including warnings, or keep them explicit blocking unknowns; never
silently downgrade a warning.
