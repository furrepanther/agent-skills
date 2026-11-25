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

## Failure-closure canon

Every observed test, runtime, transport, persistence, policy, or coordination
failure remains open until its actionable root cause is identified, corrected
at the owning layer, rerun on the affected path, and protected by a
proportionate recurrence guard. An error record, alert, restart, unchanged
retry, severity change, suppression, or `blocked` label is containment or
evidence only; none is a fix. If another owner controls the correction, send
the exact evidence, causal finding, acceptance test, and next reconciliation
point through the authoritative work-order path rather than silently doing the
work or treating the note as closure. Do not claim empty-boat, readiness, or
promotion while a material failure lacks that closure record.

## Review continuity ledger

[references/lesson-ledger.md](references/lesson-ledger.md) preserves reusable
lessons and historical review dispositions. Read it before dispatching a gate
and record a new reusable lesson only after it is reflected in this skill or a
linked reference. Record already-covered lessons as `already_reflected`, and
keep secrets and high-volume telemetry out of the ledger and Memory Fabric.

Historical `target_executions`, `completed_executions`, or window-status
fields are audit metadata, never a global execution cap, promotion blocker, or
requirement to open a new window. Continue the review, correction, and
validation work needed to reach an evidence-supported decision. Bound each
individual dispatch or repair retry by its risk, authority, and independent
stop condition; do not use an arbitrary cumulative iteration count to stop a
required gate.

An explicit work order may impose a count limit for its named task and host
when that limit has its own stated authority and stop condition. Apply it only
within that declared scope; never generalize it into a default, a cross-host
constraint, or a limit on an unrelated promotion gate.

## Hard boundaries

- DeepHarness-RSI source transport is retired as a review and promotion lane.
  Do not dispatch it, wait on it, or treat its receipt, storage record, or
  transport state as a gate result. Use this Red-Team Gate with direct source
  access and its required local evidence instead. Historical DeepHarness
  material may be background context only; it can neither clear nor block a
  current gate.
- Route all substantive inference through `http://127.0.0.1:11888`; direct
  provider/model, cloud, or new fallback paths are prohibited. The local gate
  model alias is fixed to `local-inference-11888` and rejects
  `PRIMUS_CHECKER_MODEL`, `PRIMUS_GRUMPY_MODEL`, or CLI values that name any
  other worker. Primus may expose an opt-in junior/delegated 4B route on
 11891 for other tasks, but it is not a Red-Team Gate fallback and must never
 satisfy gate evidence. The router may use that attested junior lane for
 light delegated work; that is permitted router-owned inference, and its
 counters are informational rather than a gate pass/fail criterion. The
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

## Full gate components

The named full Red-Team Gate is one ordered review, not a substitute name for
one reviewer lane:

1. The enabled SDLC lanes run through the local Primus 27B router.
2. Solid Snake runs as the explicit hidden-path, race, stale-state, and
   partial-failure adversarial lane.
3. Grumpy runs last as the hostile consolidation and final stopper.

An empty-boat result requires all expected SDLC lanes, Solid Snake, and Grumpy
to complete with valid local route evidence, no unresolved findings, no
warnings or unknowns, and verified cleanup. The delegated 4B junior route may
serve light non-gate work through the Primus router, but its counters or output
cannot satisfy any full-gate lane.

### Canonical packet and lane-coverage contract

- The review wrapper consumes the typed top-level fields `TASK`,
  `ACCEPTANCE_CRITERIA`, `DIFF_OR_FILES`, `TESTS`, `EVIDENCE`,
  `KNOWN_CONSTRAINTS`, `OUT_OF_SCOPE`, and `PROVENANCE`. Friendly aliases such as
  `implementation_files`, `implementation_scope`, or nested lowercase `tests`
  are not review evidence until an explicit packet-authoring step maps them to
  those fields and verifies the emitted packet.
- Treat the draft as typed input, not a bag of text: `TASK` is a non-empty
  string; `ACCEPTANCE_CRITERIA` is a non-empty list of unique string/object
  criteria; `DIFF_OR_FILES` is a path list or inline path-plus-bytes list;
  `TESTS`, `KNOWN_CONSTRAINTS`, and `OUT_OF_SCOPE` are non-empty string lists
  (a single string may be normalized to one item); and `PROVENANCE` is an
  object with string identity/revision/time fields and string artifact paths.
  Reject wrong types and do not coerce arbitrary objects or numbers into
  strings. This type gate exists to stop malformed packets before attestation,
  not merely to make reviewer prompts clearer.
- Before dispatch, require non-empty `TASK`, `ACCEPTANCE_CRITERIA`,
  `DIFF_OR_FILES`, `TESTS`, and `EVIDENCE`; require `PROVENANCE` to be an object
  with `provenance_verified=true` and `complete_packet=true`. `EVIDENCE` must
  be a non-empty typed list with one or more records per substantive criterion;
  each record must include a unique `id`, `criterion_id`, `test_or_locus`,
  `input_boundary`, `observed_outcome`, `status` (`pass`, `fail`, or `unknown`),
  and an exact `artifact_ref` or explicit `inline:<source>` reference. A bare
  command, test count, or artifact digest cannot substitute for criterion-level
  proof. A reviewer result that
  says the packet is empty or incomplete is an evidence-transport failure, not
  a substantive code finding and not a pass.
- Build packets through the shared typed builder and schema contract when the
  review package provides them (`tools/review_packet_builder.py`,
  `schemas/review_packet_input_v1.json`, and
  `templates/review_packet_template.json`). Run the matching
  `tools/review-packet-preflight --input <packet>` before starting any lane.
  If the package does not provide those exact components, use this skill's
  dependency-free fallback `scripts/review_packet_builder.py --input <draft>
  --output <packet>` and run `scripts/test_review_packet_builder.py` first.
  Pass only the builder's output to the wrapper; never hand-author the final
  attested packet.
  When `FULL_ARTIFACTS` are supplied, the fallback marks
  `PROVENANCE.pointer_required=true` if the complete packet cannot fit inline;
  pass that output through the wrapper's verified pointer-hydration path and
  do not dispatch the full storage packet directly.
  The builder may set `provenance_verified=true` and `complete_packet=true`
  only after the required sections, immutable base revision, source identity,
  and evidence have passed validation. The wrapper must use the same validator
  at its boundary when that integration exists. If it does not, the caller's
  successful fallback preflight is required but must not be described as
  independent wrapper enforcement; record that integration gap as a blocker
  for any claim that the wrapper itself rejects malformed packets.
- This skill-only fallback does not modify an existing production wrapper; a
  wrapper integration is a separate change with its own tests and review.
- The safe authoring sequence is: write only the draft fields, run the
  builder's self-test, build one serialized packet, inspect that exact emitted
  packet, and dispatch only that file. Any change to the emitted JSON—even a
  metadata edit—requires a fresh build and fresh digests. A successful
  structural build is not a promotion decision.
- Treat packet construction as a one-way state machine:
  `draft -> normalized -> validated -> attested -> serialized`. Callers provide
  only the draft/source fields; they must not pre-set or hand-edit
  `provenance_verified`, `complete_packet`, `pointer_verified`,
  `cleanup_verified`, `empty_boat`, digests, or `PROVENANCE.gate_state`. The
  builder owns those fields and must reject a draft that supplies them. Any
  mutation after attestation invalidates the attestation and requires a fresh
  build; never patch the final JSON in place.
- Cleanup evidence is supplied as draft-only `PROVENANCE.cleanup_proof`; callers
  must not set the builder-owned `cleanup_verified` flag. When present, the
  proof must contain `status=pass`, an exact or inline `receipt_ref`, a full
  `receipt_sha256_full`, one exact cleanup `target`, unique observed-absence
  paths, positive `record_cap` and `byte_cap`, and passing active-pointer and
  post-delete checks plus `recursive_tree_check=pass` and
  `recursive_tree_entry_count=0`. The builder may set `cleanup_verified=true` only after
  this typed validation; the reviewer still verifies the receipt bytes and
  target evidence. Missing proof leaves cleanup unverified and blocks any
  promotion claim that requires cleanup.
- Make the builder perform semantic checks before it emits the final packet:
  assign stable unique criterion IDs, reject duplicate criteria/evidence IDs or
  paths, require every criterion to have at least one matching evidence record,
  require `unknown` evidence to carry an explicit blocker/no-claim state, and
  require the base revision, source identity, repository scope, and artifact
  references to agree across all sections. Unknown keys or aliases must be
  rejected or mapped explicitly; they must never be silently ignored.
- The preflight is a dispatch barrier, not a lint hint. Run schema/type,
  semantic-coverage, provenance/digest, artifact-byte, and serialized-wire-size
  checks in that order. On any error or warning, emit no reviewer request and
  no router call; return the exact failed field/check and regenerate from the
  corrected draft. Do not retry the unchanged packet and do not let a caller
  force the attestation flags true.
- Keep a construction regression matrix at the real builder/wrapper boundary:
  missing or alias-only required fields, wrong field types, duplicate IDs or
  paths, criterion without evidence, contradictory `pass`/`unknown` state,
  caller-forced attestation, invalid or mismatched full digests, artifact
  reference/size mismatch, stale base revision/source identity, Unicode and
  envelope size overflow, and a valid packet that must reach dispatch. Assert
  that every invalid case makes zero reviewer/router calls and that the valid
  case preserves the exact typed fields and wire digest.
- When `FULL_ARTIFACTS` is present, require non-empty
  `PROVENANCE.artifact_refs` that exactly cover the artifact paths, and require
  every artifact's complete UTF-8 `content` and byte digest
  (`file_sha256_full`) to match. Validate declared byte sizes when supplied.
  Missing content or references, malformed digests, digest mismatches,
  duplicate paths, or size mismatches are input-validation failures, not
  reasons to retry a packet unchanged.
  Regenerate the packet through the builder after correcting the source.
- `PROVENANCE.artifact_refs` must also declare every path in `DIFF_OR_FILES`,
  even when the evidence is otherwise inline. This makes the reviewed scope
  independently addressable and prevents a packet from claiming a complete
  diff while supplying no artifact provenance.
- An inline packet must carry reviewable bytes, not only names: every
  `DIFF_OR_FILES` entry must include a non-empty `diff` or `content` string.
  Path-only entries are valid only when `FULL_ARTIFACTS` supplies the complete
  digest-verified artifact bytes for the same paths and the wrapper's verified
  pointer-backed transport is used when the packet exceeds the wire ceiling.
  A packet that declares `inline_only` while carrying only path references is
  malformed and must be rejected before attestation or dispatch.
- Boundary contracts require an executable regression test at the real
  construction/dispatch boundary, not only a configuration-consistency test.
  For every active lane ceiling, prove that an in-bound packet reaches the
  checker and that an over-bound packet is rejected before router dispatch;
  keep the assertion tied to the actual serialized wire representation so
  Unicode escaping and envelope fields cannot create a hidden overflow.
- Reviewer output is a separate bounded contract: lane prompts must require
  compact, non-duplicative JSON sized for the local completion ceiling. Do not
  retry a response that hit the length limit unchanged; narrow the response
  shape or remove duplicated evidence while preserving the required findings,
  decisions, and acceptance proof, then issue a new packet/review revision.
  A clean result must use an empty residual-risk list; a sentence saying that
  no defect was found is evidence or rationale, not an unresolved risk.
- Treat reviewer fields as a typed contract, not independent prose. Before
  accepting `no_blocking_defect_found`, cross-check that every extracted
  requirement is `clear`, every corresponding coverage record is `covered`,
  and no gap or missing-evidence status contradicts the decision. Any such
  contradiction fails closed as `insufficient_evidence` and requires a new
  review result; do not normalize the contradiction into a pass.
- For each nontrivial acceptance criterion, the compact `EVIDENCE` record must
  name the test or locus plus its controlled boundary/input and the asserted
  observable outcome. A bare passing command or test name is not proof that the
  criterion was exercised. If the descriptions cannot fit, compact the typed
  records while preserving every criterion ID, status, and artifact reference;
  never drop a record, replace it with a digest-only placeholder, or silently
  fall back to a bare `TESTS` pass count. The verified pointer-backed path may
  carry complete bytes, but it does not excuse omitting the reviewer-visible
  criterion proof.
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
   Treat the 16,384-character lane limit as the canonical active ceiling and
   the 12,000-character value as a validated compatibility tier: reserve documented child-normalization/launcher
   headroom (currently 100 characters) so the emitted packet remains below the
   active limit after the receiving checker reconstructs its payload. The
   historical 3,500-character value, intermediate 4,000-character candidate,
   and prior 7,000-character compatibility ceiling remain explicit rollback
   baselines, not active limits.
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
   atomic index. When pointer-backed transport is permitted, inline raw bytes
   are not required if the reviewer receives the necessary verified content
   through a supported retrieval or hydration path. Producer-side storage,
   hashes, and transport attestation alone do not prove reviewer access. If the
   content needed for the decision is unavailable or reviewer receipt cannot
   be established, return `insufficient_evidence` and block promotion. Never
   accept a no-block result that marks required evidence inaccessible or a
   requirement missing evidence.
   The current 12,000-character compatibility transport uses one verified
   source-review page plus a byte-bounded sample ledger for every indexed file;
   sample rows carry their complete-index position so a compact handoff cannot
   silently rename, reorder, or omit a path. The full source bytes remain only
   in the exact pointer-backed record, and the child must validate the page,
   sample coverage, pointer digest, and typed evidence rows before review.
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
