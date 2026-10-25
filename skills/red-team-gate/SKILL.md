---
name: red-team-gate
description: Universal local-agent procedure for running an adversarial Red-Team-Gate review of changes, candidate algorithms, or promotion decisions that need hostile validation, functional deduplication, explicit adopt/adapt/reject/unknown decisions, or empty-boat evidence. Automatically discoverable when those conditions are present.
metadata:
  short-description: Orchestrate an adversarial review gate
---

# Red-Team Gate

This is the universal Red-Team-Gate procedure for all local agents. Use this
skill automatically when any agent handles a hostile review, a promotion gate,
a safety or reliability claim, competing implementations, duplicated
capabilities, or a request to prove that no findings remain. It is also
available explicitly as `$red-team-gate`.

Automatic discovery is a host skill-selection hint, not execution permission;
it grants no tools, writes, external resolution, or promotion authority.

This skill orchestrates review and evidence. It does not authorize source
changes, external writes, cloud inference, or production mutation.

## Rolling lesson-transfer window

This is a bounded, non-sliding 15-execution lesson window with a cumulative hard cap of fifteen total
counted executions, recorded in
[references/lesson-ledger.md](references/lesson-ledger.md), count the current
execution when it starts. Before dispatching each counted gate, read the
ledger and compare the planned packet, transport, and review behavior against
the lessons already captured here. After the gate completes, record only
reusable lessons that are not already reflected in this skill or its linked
references; update the skill/reference first, then append the run disposition
and skill revision/digest to the ledger. A lesson that is already covered is
recorded as `already_reflected`, not duplicated. Keep this window bounded to
fifteen executions, preserve the ledger after closure for audit, and do not put
high-volume run telemetry or secrets in it or in Memory Fabric.
When `completed_executions` reaches `target_executions`, stop dispatching new
counted executions until a new window id and target are explicitly established;
corrective retries of the same open gate do not create a new promotion decision.
The cap is cumulative within the window, not a sliding limit; counted
executions never reset until a new window id is explicitly established.

## Hard boundaries

- Route all substantive inference through `http://127.0.0.1:11888`; direct
  provider/model, cloud, or new fallback paths are prohibited. The
  environment-owned adapter contract is: exact loopback target, task-scoped
  input, no provider/model selector, and route evidence with endpoint,
  adapter identity/version, request id, and local/cloud status. Do not build a
  raw provider schema. Adapter absence, target/evidence ambiguity,
  direct-provider/model signal, invalid response, timeout, or cloud handoff
  fails closed and makes the affected decision `unknown`; never invent,
  install, or update that adapter.
- Stay within the user-scoped local files, services, and repository paths.
  Upstream GitHub code is read-only. If GitHub code must be modified, work only
  in the user's personal fork; never push, merge into, or write to upstream.
  Without a verified personal fork, stop that edit or promotion as `unknown`.
- Delegated jobs declare task id, owner, purpose, scope, output byte/line caps,
  and an independent stop condition; never terminate solely for duration/age.
- Every read names exact source/task selector, `byte_cap`, `line_cap`, and
  `selection`; use bounded tail or task-id prefilter plus tail only. Whole-log,
  uncapped, and broad log reads are prohibited.
- A pending local review request is not a hang merely because it is old. Continue
  while bounded health, queue, worker-slot, or metrics probes show live queued or
  processing activity, or monotonic token/admission progress. Fail only on an
  explicit request/service error, a terminally unavailable evidence surface, or
  repeated healthy-but-idle probe snapshots that establish transport ambiguity.
  The observation interval and a small consecutive-idle evidence threshold are
  diagnostic settings, never total job-duration limits; retain only a capped tail
  of compact snapshots and never read whole logs. Report `transport_ambiguous`
  rather than silently retrying or claiming a model failure.

### Canonical packet and lane-coverage contract

- The review wrapper consumes the typed top-level fields `TASK`,
  `ACCEPTANCE_CRITERIA`, `DIFF_OR_FILES`, `TESTS`, `KNOWN_CONSTRAINTS`,
  `OUT_OF_SCOPE`, and `PROVENANCE`. Friendly aliases such as
  `implementation_files`, `implementation_scope`, or nested lowercase `tests`
  are not review evidence until an explicit packet-authoring step maps them to
  those fields and verifies the emitted packet.
- Before dispatch, require non-empty `TASK`, `ACCEPTANCE_CRITERIA`,
  `DIFF_OR_FILES`, and `TESTS`; require `PROVENANCE` to be an object with
  `provenance_verified=true` and `complete_packet=true`. A reviewer result that
  says the packet is empty or incomplete is an evidence-transport failure, not
  a substantive code finding and not a pass.
- Automatic supplemental lane selection is additive. With no explicit lane
  subset, all enabled mandatory SDLC lanes must run; auto-selected lanes must
  never replace that default set. With an explicit subset, only that subset
  plus explicitly auto-added lanes may run. Compare the actual completed lane
  set with the expected set and fail closed if automatic selection silently
  reduces coverage.

### Targeted repair loop

The canonical wrapper may perform a bounded targeted repair before declaring an
affected lane incomplete. The loop is evidence repair, not a second opinion and
not permission to weaken a finding:

- Run the deterministic front-door prefilter first, then run the full Grumpy
  reviewer as the server-side final gate over the consolidated lane evidence.
  Grumpy remains the authoritative stopper and must not be moved to a client
  UI or bypassed because it rejects a packet.
- Repair only deterministic transport/schema defects or a reviewer-reported
  missing/empty field when the authoritative packet is complete. Rebuild the
  lane packet from that source and rerun only the affected lane; rerun Grumpy
  afterward because its input changed. Unchanged lanes are not rerun.
- If the authoritative packet is incomplete, recover it only through one
  verified temporary Memory-Fabric pointer whose exact record, content digest,
  packet digest, retention metadata, and non-canonical status all match. If
  recovery fails or no pointer exists, mark the lane `insufficient_evidence`
  and stop; never infer, summarize away, or invent evidence.
- Cap corrective attempts by count (default one, hard maximum two), not by
  elapsed time. Record every attempted action, source pointer, digest check,
  output path, parse result, and final repair status in the review artifact.
- Never auto-edit production code, repair a substantive `block`, suppress a
  warning, or convert a failed/unknown outcome into a pass. A successful
  repair only permits the affected lane to be reviewed again; the final
  decision still requires clean SDLC, Grumpy, runtime, and cleanup evidence.

This split keeps the frequent Grumpy stop useful: its deterministic fast path
filters obvious defects cheaply, while the full local-router Grumpy backend
sees the complete post-repair evidence packet. Datacube remains a peer and
Memory-Fabric authority, not an implicit Grumpy execution host; use a formal
peer review lane only when cross-system impact requires it.

## Procedure

1. Freeze the review scope: intended outcome, exact paths or revision, source
   provenance, fork/upstream status, lane ceiling, and promotion authority.
   Preserve existing dirty work and do not infer permission to edit from review
   access.
2. Attack the proposed behavior. Probe bypasses, trust-boundary confusion,
   partial failure, retries, concurrency, cancellation, recovery, cleanup,
   privacy, stale or contradictory evidence, and unsafe promotion. Every
   finding must be actionable: give a locus, trigger, impact, bounded evidence
   reference, and a concrete fix or acceptance test.
3. Compare alternatives by capability, not repository prestige. Measure
   utility against the stated objective, functionally deduplicate overlapping
   behavior, assign one canonical owner per capability, and select the best
   algorithm using correctness, failure containment, privacy, recovery,
   resource headroom, throughput, testability, and operational complexity.
   Do not add a second router, queue, memory authority, telemetry path,
   fallback policy, or checkpoint owner merely because it is novel or fast.
4. Record an explicit decision for every candidate and capability:
   `adopt`, `adapt`, `reject`, or `unknown`. `adopt` and `adapt` require exact
   evidence and a proof test; `reject` requires the incompatibility or losing
   tradeoff; `unknown` is a blocking discovery item and must not be treated as
   compatible.
5. Build one compact, complete evidence packet under the lane ceiling. If the
   full packet does not fit, use only the existing approved temporary
   Memory-Fabric evidence path: persist the full packet, verify its exact
   pointer and content/packet digests, then send one compact index with
   pointer-backed overflow. Never split a structured file entry into fragments
   or discard actionable evidence. Before dispatch, run the same checker-size
   compaction locally and assert that every required name, path, finding id,
   digest, and gate-state token survives. Keep candidate mapping counts
   separate from verified checkout or report counts; a URL mapping is not a
   checkout proof. The validator's expected candidate/report scope must match
   the manifest and the packet; do not mix deferred candidates into a fixed
   intake count unless the schema represents their status explicitly.
   Treat the 7,000-character lane limit as the current measured compatibility
   candidate, not a target: reserve documented child-normalization/launcher
   headroom (currently 100 characters) so the emitted packet remains below the
   limit after the receiving checker reconstructs its payload. The historical
   3,500-character value and the intermediate 4,000-character candidate remain
   explicit rollback baselines until the 7,000-character compatibility gate is
   empty-boat green.
   The compact evidence-index packet itself must include a full 64-character
   `entry_sha256_full` and `entry_sha256_full_len=64` for every listed entry,
   plus full 64-character artifact digests in the compact evidence text when applicable, using an unambiguous
   field such as `file_sha256_full`; wrapper-generated shortened display
   digests do not replace them. Spell
   When independent verification of bounded source artifacts is part of the
   acceptance criteria, store their complete bytes in a pointer-backed
   `FULL_ARTIFACTS` section with those file digests; keep the lane handoff
   compact and verify the pointer's content/packet digests.
   Preserve the typed transport attestation in compact Grumpy handoffs:
   `transport=pointer_backed_complete_bytes`, `complete_bytes_stored=true`,
   and `inline_bytes_in_lane=false`, alongside the verified exact pointer and
   atomic index. When this attestation is present and the acceptance criteria
   permit pointer-backed transport, the reviewer must not demand inline raw
   bytes; paths and hashes alone remain insufficient without the attestation.
   Preserve the canonical `PROVENANCE.repo_or_scope` during compaction so the
   receiving checker does not substitute a temporary input filename and make
   the parent size estimate disagree with the child. A below-floor complete
   index is a rejected candidate to skip during fallback search, not an
   exception that may abort a later valid representation.
   blocking promotion states explicitly rather than relying on a nearby
   `blocked` field. After wrapper generation, inspect the actual emitted
   packet and assert that the pointer's content/packet digests equal the
   compact index values; a preflight simulation alone is insufficient. See
   [references/evidence-packet.md](references/evidence-packet.md).
   Put the structural result, functional-proof state, promotion decision, and
   no-claim status in a typed `PROVENANCE.gate_state` field that compaction
   preserves; do not rely on a free-form `TESTS` field surviving head/tail
   compaction.
   The wrapper's own per-entry digest must also be a full 64-character value
   under an unambiguous name such as `entry_sha256_full`; a field named
   `sha256` containing a shortened prefix is a blocking provenance defect.
   Atomic preservation therefore requires a full 64-character SHA-256 digest
   for every evidence entry, not merely one digest for the containing packet.
   If an entry declares `file_sha256_full` or `artifact_sha256_full`, preserve
   that full artifact digest in the fixed index rather than relying on an
   evidence excerpt that may be removed to fit the lane.
   If page zero is insufficient, use verified pointer-backed continuation
   pages: request one exact record id, selector, cursor, generation, and
   byte/line cap at a time; require parent/page digests, next cursor, and
   completion state; carry receipts and finding IDs instead of replaying old
   page bodies. Treat missing, stale, out-of-order, over-cap, or digest-
   mismatched pages as `unknown` and blocking. “Unlimited” means no fixed
   total page count before the task-scoped completion condition, never
   unlimited storage, retention, retries, or uncapped reads.
   A complete evidence index is an atomic typed artifact preserved as one
   indivisible whole: assemble and verify
   every fixed row and full digest before emitting it; on any capacity or
   verification failure, emit no partial index and mark the gate blocked. Any later lane or
   Grumpy budget pass must recognize an existing `complete_evidence_index`,
   preserve every fixed path/full-digest record, and retain whole per-entry
   evidence excerpts when they fit. It must never treat the index as opaque
   text, drop entries, or create a sequential fragment review. If the fixed
   records cannot fit the requested bound, fail closed as an evidence-budget
   blocker rather than truncating them.
   For transport, retry, health, or false-success fixes, the associated
   runtime gate must collect both a deterministic negative-path regression
   (for example, a stubbed unreachable peer proving nonzero exit and exact
   arguments) and independent live recovery proof. Independent live recovery
   proof is a distinct current health/recovery probe that does not reuse the
   negative-path stub or its output; record the historical failure and current
   recovery as separate labeled evidence. A current health pass does not prove
   the failure path. This skill mandates that runtime-gate dependency; a
   skill-only gate verifies that the mandate is explicit and never substitutes
   for the actual negative-path or live-recovery evidence.
6. At each checkpoint, apply empty-boat semantics. Empty boat means the scope,
   provenance, packet completeness, pointer verification, cleanup record,
   candidate decisions, and findings are all accounted for, with no
   uncategorized warning/error, uncapped read, unsupported stop, hidden
   unknown, missing owner, parser failure, or unresolved blocker. Absence of
   reported findings is not an empty boat.
   Keep validation state explicit: a structural validator may pass while a
   promotion gate remains blocked. State both results and their authority in
   the packet; never present a structural pass as promotion approval. When
   functional proof is intentionally absent, include that absence as an
   explicit blocking test result and state that no promotion claim is made.
   Continue the same gate until implementation, packet, runtime, and cleanup
   are all empty-boat; do not advance the phase or promote while any one of
   those surfaces has an unresolved warning, error, unknown, or blocker.
7. Dispose of every finding before promotion. All findings, including warnings,
   must be corrected with evidence and a rerun, or remain explicit blocking
   unknowns. No warning may be silently downgraded, waived, or hidden. No
   finding may disappear through deduplication, truncation, timeout, or cleanup.
   Iterate the same gate after each correction until the packet, implementation,
   negative-path proof, runtime evidence, and cleanup state are all empty-boat;
   do not count a failed evidence preflight or a reviewer retry as a new
   promotion decision, and do not advance the work phase while the same gate is
   still open.
8. If dependency or tool execution is needed, use an isolated disposable local
   environment (such as a virtual environment), pin and record provenance,
   run bounded validation, and do not mutate the production interpreter or
   system packages. Production promotion requires a separate currency,
   compatibility, and rollback gate.
9. Clean temporary overflow only by exact record id after active-pointer checks,
   within explicit record/byte bounds, and with post-delete verification. Keep
   the cleanup result in the packet. If pointer verification or cleanup proof
   fails, block promotion and report `unknown`; do not broaden deletion.

## Handoff

Return a compact decision record containing the scope and base revision,
router route, packet/pointer and digest status, candidate decisions, every
finding disposition, empty-boat status, cleanup status, blockers, and the
promotion decision. Do not claim a clean gate while any required item is
unknown, unresolved, unowned, or unverified.
