# Red-Team-Gate Lesson Transfer Window

window_id: `red-team-gate-lesson-window-20261022`
target_executions: 15
execution_limit: hard cap of 15 total counted executions
window_contract: bounded, non-sliding 15-execution lesson window
window_semantics: cumulative hard cap; no sliding reset within the window
empty_boat_definition: no pending/in_progress/undispositioned counted entries; every counted entry has a disposition and no unresolved blocker
counting_rule: Count an execution when the gate is dispatched, including the current run.
active_execution: 15
next_execution: none
completed_executions: 15
remaining_executions: 0
cap_definition: target_executions is the hard cap on total counted executions, not a concurrency limit; active_execution is the current ordinal and may not exceed target_executions
cap_enforcement: counted executions 14 and 15 are closed; the cumulative hard cap is reached and no new counted execution may be dispatched in this window
status: closed

## Operating rule

For each of the fifteen executions, compare the packet, transport, and review
result with `SKILL.md`. If a reusable lesson is absent, update the skill or a
linked reference before recording the run disposition. If it is already
covered, record `already_reflected` and do not duplicate it. Keep this ledger
bounded and free of secrets and high-volume telemetry.
The ledger owns window counting and disposition state only; evidence atomicity,
digest preservation, and fail-closed capacity are self-contained requirements
of `SKILL.md`, not optional ledger fields.
When `completed_executions` reaches `target_executions`, stop dispatching new
counted executions until a new window id and target are explicitly established;
corrective retries of the same open gate do not create a new promotion decision.

## Execution 1 (current v6 review)

status: closed
counted: true
review_artifact: `/usr/production/runtime/review_harness_plan_20261022_memory_v6/review.json`
scope: harness plan evidence packet and local Superpowers/SDLC gate
lessons_preloaded:

- Evidence must distinguish the number of mapped upstream candidates from the
  number of verified reports or checkouts.
- A structural validator pass and a blocked promotion gate are compatible
  states and must be stated with separate authority labels.
- Compaction must be simulated against the real 3500-character checker budget,
  with required names and gate-state evidence asserted after compaction.

skill_update: applied to `SKILL.md` before completion of this execution
post_run_disposition: blocked_by_evidence_ambiguity
new_lessons: transferred_to_skill
resolution: later lesson iterations corrected the evidence ambiguity; no unresolved blocker remains
skill_revision_digest: `3759784384476e8599c2d02b7c6ec5688962164706de3d967957fd744202c4aa`
review_result: `/usr/production/runtime/review_harness_plan_20261022_memory_v6/raw/grumpy_final.result.json`

## Execution 2 (v7 review)

status: closed
counted: true
review_artifact: `/usr/production/runtime/review_harness_plan_20261022_memory_v7/review.json`
scope: corrected harness plan evidence packet and local Superpowers/SDLC gate
preflight: compaction simulation passed at 3423 checker characters with all 16 mapping names retained
lessons_checked: mapping-versus-checkout scope and structural-validator-versus-promotion distinction are now reflected
post_run_disposition: blocked_by_manifest_scope_mismatch
new_lessons: transferred_to_skill
resolution: later lesson iterations reconciled manifest and validator scope; no unresolved blocker remains
skill_revision_digest: `3759784384476e8599c2d02b7c6ec5688962164706de3d967957fd744202c4aa`
review_result: `/usr/production/runtime/review_harness_plan_20261022_memory_v7/raw/grumpy_final.result.json`

## Execution 3 (v8 review)

status: closed
counted: true
review_artifact: `/usr/production/runtime/review_harness_plan_20261022_memory_v8/review.json`
scope: sixteen-row manifest, corrected plan, and local Superpowers/SDLC gate
preflight: fresh backup and validator pass after manifest/validator scope reconciliation; packet simulation passed at 3469 checker characters with all 16 mapping names retained
lessons_checked: manifest/validator/plan scope alignment is now explicit
post_run_disposition: blocked_by_compact_digest_and_gate_wording
new_lessons: transferred_to_skill
resolution: later lesson iterations corrected compact digest and gate-state wording; no unresolved blocker remains
skill_revision_digest: `2323a5987deeb1843461a2e9ab6bd430346933782b5d7fe6a8a26e28a2ae9af8`
review_result: `/usr/production/runtime/review_harness_plan_20261022_memory_v8/raw/grumpy_final.result.json`

## Execution 4 (v9 review)

status: closed
counted: true
review_artifact: `/usr/production/runtime/review_harness_plan_20261022_memory_v9/review.json`
scope: full-digest/full-status packet, sixteen-row manifest, corrected plan, and local Superpowers/SDLC gate
preflight: compaction simulation passed at 3469 checker characters with all 16 mapping names and full plan hash retained
lessons_checked: validator scope, structural-versus-promotion state, full digest, and explicit BLOCKED wording are reflected
post_run_disposition: blocked_by_pointer_digest_evidence_ambiguity
new_lessons: transferred_to_skill
resolution: later lesson iterations added pointer digest and evidence-parity requirements; no unresolved blocker remains
skill_revision_digest: `f3b1eb6a2ed362a5547b5e40f9f128e4f7d6c56f98cdc8ec140bacfe730d63c8`
review_result: `/usr/production/runtime/review_harness_plan_20261022_memory_v9/raw/grumpy_final.result.json`

## Execution 5 (v10 review)

status: closed
counted: true
review_artifact: `/usr/production/runtime/review_harness_plan_20261022_memory_v10/review.json`
scope: emitted-pointer digest parity, explicit blocked state, sixteen-row manifest, corrected plan, and local Superpowers/SDLC gate
preflight: packet simulation passed at 3499 characters; emitted v10 packet parity was inspected and content/packet digests matched
lessons_checked: full digest, explicit BLOCKED state, and generated pointer parity are reflected
post_run_disposition: blocked_by_missing_negative_functional_proof_statement
new_lessons: transferred_to_skill
resolution: later lesson iterations added explicit negative-path proof requirements; no unresolved blocker remains
skill_revision_digest: `3cfc37e5dcef21f54d5365f5bf7bf496296fcc1083be1e29f6ab96c108d676b6`
review_result: `/usr/production/runtime/review_harness_plan_20261022_memory_v10/raw/grumpy_final.result.json`

## Execution 6 (v11 review)

status: closed
counted: true
review_artifact: `/usr/production/runtime/review_harness_plan_20261022_memory_v11/review.json`
scope: explicit negative functional-proof evidence, emitted-pointer parity, sixteen-row manifest, corrected plan, and local Superpowers/SDLC gate
preflight: packet simulation passed at 3439 checker characters with all 16 mapping names, full plan hash, BLOCKED state, and negative proof retained
lessons_checked: structural pass versus absent functional proof is explicit
post_run_disposition: blocked_by_ambiguous_shortened_sha_label
new_lessons: transferred_to_skill
resolution: later lesson iterations replaced shortened digest labels with explicit full-digest fields; no unresolved blocker remains
skill_revision_digest: `fa4cc81d615e072b9263f68a3beb12ced443a6ff3bf7853604fb25801a99efdd`
review_result: `/usr/production/runtime/review_harness_plan_20261022_memory_v11/raw/grumpy_final.result.json`

## Execution 7 (v12 review)

status: closed
counted: true
review_artifact: `/usr/production/runtime/review_harness_plan_20261022_memory_v12/review.json`
scope: explicit full file digest field, negative functional-proof state, emitted-pointer parity, sixteen-row manifest, and local Superpowers/SDLC gate
preflight: packet simulation passed at 3282 checker characters with all 16 mapping names, refreshed plan/skill/reference hashes, and the BLOCKED state retained
lessons_checked: full digest naming, pointer parity, absent-functional-proof state, and pointer-backed logical continuation are reflected
new_lessons: compact indexes must emit full 64-character entry digests with unambiguous labels; preserving a full artifact digest only inside an excerpt is insufficient because compaction may remove the excerpt
post_run_disposition: blocked_by_shortened_compact_entry_digest
resolution: later lesson iterations require full per-entry digests and fail-closed compaction; no unresolved blocker remains
skill_revision_digest: `c26ffb39faedeac1945b93d7e0181002cffe4cc45efc336c1264ce5f0f65d48a`
review_result: `/usr/production/runtime/review_harness_plan_20261022_memory_v12/raw/grumpy_final.result.json`

## Execution 8 (v13 review)

status: closed
counted: true
review_artifact: `/usr/production/runtime/review_harness_plan_20261022_memory_v13/review.json`
scope: full entry/artifact digest transport, typed gate_state preservation, pointer-backed logical continuation, sixteen-row manifest, and local Superpowers/SDLC gate
preflight: packet simulation passed at 3366 checker characters with all five scoped paths, five full entry digests, five full artifact digests, explicit gate_state, and the BLOCKED state retained
lessons_checked: shortened compact digest and lossy gate-state compaction are corrected in the wrapper, skill, evidence reference, and focused regression tests
post_run_disposition: superseded_by_current_skill_gate_review
new_lessons: already_reflected
resolution: the prior incomplete review was superseded by the current skill-parity gate; no unresolved blocker remains
skill_revision_digest: `4f6d77802196f094c23146f65147ce653b369cd8cb7c40b411b30029db2d0dc3`

## Execution 9 (GitHub Desktop v29 review)

status: closed
counted: true
review_artifact: `/tmp/github-desktop-upstream-review-20261021.result.v29.json`
scope: GitHub Desktop upstream sync, router-only Local-LLM hardening, and automatic Git LFS activation
preflight: packet was structurally valid, but compact Grumpy evidence omitted or truncated scoped entry evidence under the 3500-character lane budget
lessons_checked: complete evidence index, full entry digests, typed gate_state, and actionable findings are already required by SKILL.md and evidence-packet.md
post_run_disposition: blocked_by_evidence_budget; already_reflected
new_lessons: already_reflected
resolution: later wrapper hardening preserved complete evidence indexes under the lane ceiling; no unresolved blocker remains
skill_revision_digest: `d151fba63adda7162d056b789b13e2a3287cf9cd08856cc099267b418e9e9190`
review_result: `/tmp/github-desktop-upstream-review-20261021.raw.v29/grumpy_final.result.json`

## Execution 10 (v36 local six-lane review)

status: closed
counted: true
review_artifact: `/usr/production/runtime/review_red_team_skill_20261022_v36_retry12/result.json`
scope: Red-Team-Gate skill, lesson ledger, pointer-backed evidence transport, and local Grumpy/SDLC review contract
preflight: full six-lane SDLC review plus Grumpy completed locally; packet child normalization measured at 3399/3400 for the lane target; complete pointer-backed transport attestation preserved; 89 tests passed
lessons_checked: child-normalization scope parity, below-floor complete-index fallback, typed complete-bytes transport attestation, and explicit reviewer acceptance of verified pointer-backed artifacts
post_run_disposition: no_blocking_defect_found
new_lessons: transferred_to_skill_and_reviewer_prompt
resolution: compact fallback now skips indivisible below-floor candidates, preserves canonical repo_or_scope and complete transport flags, and Grumpy no longer treats a valid pointer-backed transport exception as a blocking defect
skill_revision_digest: `abbb8d9064892d23f966637f447b9c2db4795b0c1038b410f0adc1dff47e54ba`
review_result: `/usr/production/runtime/review_red_team_skill_20261022_v36_retry12/result.json`

## Execution 11 (GitHub Desktop Linux Secret Service review)

status: closed
counted: true
review_artifact: `/tmp/github-desktop-keyring-review-20261022.result.json`
scope: Linux Secret Service/keytar credential storage, secure account discovery, legacy plaintext migration, popup suppression, and launcher promotion
preflight: complete evidence packet passed digest validation after one corrected packet metadata defect; six SDLC lanes and Grumpy final completed locally
lessons_checked: secure-store boundary, migration survivability, explicit test-harness limitations, actionable findings, and no-secret evidence handling
post_run_disposition: no_blocking_defect_found; already_reflected
new_lessons: already_reflected
resolution: all reported findings were empty; active build remains eligible after final smoke checks
skill_revision_digest: `abbb8d9064892d23f966637f447b9c2db4795b0c1038b410f0adc1dff47e54ba`
review_result: `/tmp/github-desktop-keyring-review-20261022.raw/grumpy_final.result.json`

## Execution 12 (GitHub Desktop Linux clone default review)

status: closed
counted: true
review_artifact: `/tmp/clone-default-review-result-v2.json`
scope: Linux clone dialog default directory, remembered custom locations, migration, and production promotion
preflight: focused default-dir tests 6 pass; CloneRepository validation tests 11 pass; TypeScript and Prettier pass; corrected packet completed all six SDLC lanes plus Grumpy locally
lessons_checked: explicit migration coverage, custom basename collision coverage, non-Linux fallback coverage, and full-path comparison
post_run_disposition: no_blocking_defect_found; already_reflected
new_lessons: already_reflected
resolution: all findings from the first gate were addressed with added coverage; active production bundle is eligible and promoted
skill_revision_digest: `abbb8d9064892d23f966637f447b9c2db4795b0c1038b410f0adc1dff47e54ba`
review_result: `/tmp/clone-default-review-raw-v2/grumpy_final.result.json`

## Execution 13 (storage-boundary policy review)

status: closed
counted: true
ordinal 13 of total cap 15
review_artifact: `/tmp/primus-review/storage-boundary-review-v2.result.json`
scope: loud W: mechanical-disk latency policy, startup/fallback documentation, executable storage-boundary contract test, and canonical Memory Fabric record
preflight: executable contract test passed with empty_boat=PASS warnings=0 errors=0; complete pointer-backed artifact transport was verified with exact SHA-256 digests
lessons_checked: executable proof for durable policy wording, pointer-backed complete-byte transport, full per-entry digests, local-router-only review, and no duration-only termination
post_run_disposition: no_blocking_defect_found; already_reflected
new_lessons: already_reflected
resolution: initial packet gaps were corrected by adding the executable contract test and complete pointer-backed artifacts; all six SDLC lanes and Grumpy completed cleanly
skill_revision_digest: `154a36e9e3d4d4f65fd071601d90501afa99fd538a9c2ee68ab0f6d4117eb17f`
review_result: `/tmp/primus-review/storage-boundary-review-v2.raw/grumpy_final.result.json`

## Execution 14 (MemFab auth repair review)

status: closed
counted: true
review_artifact: `/tmp/primus-review/memfab-auth-gate-20261024/r14-repair-result.json`
scope: common-MCP MemFab token lookup nonblocking repair, fail-closed authentication behavior, focused tests, and local production readiness
preflight: six SDLC lanes and Grumpy completed locally; all lanes returned zero blocking findings with no failed, parse-failed, retried, or truncated lanes
lessons_checked: token provenance, fail-closed missing/expired-token behavior, event-loop nonblocking lookup, explicit readiness semantics, and local-router-only review are already reflected
post_run_disposition: no_blocking_defect_found; already_reflected
new_lessons: already_reflected
resolution: review is clean; Datacube token issuance remains an external operational gate and was not bypassed
skill_revision_digest: `154a36e9e3d4d4f65fd071601d90501afa99fd538a9c2ee68ab0f6d4117eb17f`
review_result: `/tmp/primus-review/memfab-auth-gate-20261024/r14-repair-raw/grumpy_final.result.json`

## Execution 15 (logger path-selection corrective review)

status: closed
counted: true
review_artifact: `/tmp/primus-review/logger-path-selection-20261024-final/r15-v2-result.json`
scope: host-local system logger path selection, explicit remote-path authority, transient-I/O behavior, audit parity, and complete pointer-backed evidence transport
preflight: current test evidence named all eleven focused tests; six SDLC lanes and Grumpy completed locally with zero blocking findings, no failed lanes, no parse failures, no retries, and no truncation
lessons_checked: explicit test-name evidence, complete full-artifact transport, exact pointer digest verification, bounded temporary cleanup, and local logger/audit parity are reflected
post_run_disposition: no_blocking_defect_found; already_reflected
new_lessons: already_reflected
resolution: corrective review is clean; two temporary evidence deletion requests were queued and remain an operational cleanup follow-up, not a review blocker
skill_revision_digest: `154a36e9e3d4d4f65fd071601d90501afa99fd538a9c2ee68ab0f6d4117eb17f`
review_result: `/tmp/primus-review/logger-path-selection-20261024-final/r15-v2-raw/grumpy_final.result.json`
