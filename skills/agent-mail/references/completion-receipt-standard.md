# Completion Receipt Standard

Use this standard whenever an agent labels assigned work `completed`, accepts
another agent's completion claim, or supplies completion evidence to a
promotion, review, or handoff decision. It applies to work coordinated through
Agent Mail; a delivery, read marker, acknowledgement, SLIM receipt, or queue
state is never completion evidence by itself.

## Common minimum

A completion receipt identifies:

- the work-order or request ID, revision, owner, and executing session;
- the exact scope and each acceptance criterion that was evaluated;
- the actual actions and mutations performed, or an explicit `no mutation`;
- current evidence: commands, tests, probes, artifact digests, or other
  directly relevant verification, with outcomes rather than intended steps;
- every remaining dependency, warning, failed check, unknown, or residual
  risk; and
- one explicit status: `completed`, `blocked`, `failed`, or `cancelled`.

Use `completed` only when the assigned scope and acceptance criteria are fully
met with current evidence and no unresolved item remains. Use `blocked` when
an external dependency prevents further work, `failed` when an attempted action
did not achieve its intended result, and `cancelled` only when work was
explicitly withdrawn. Do not turn a partial result into `completed` because
some tests passed or an expected defect was not observed.

## Code, review, and promotion work

For code, review, release, migration, or promotion work, include in addition:

- fork/worktree path, branch, full immutable revision, and clean-worktree
  proof at the time of inspection or test;
- complete changed-path coverage, with every excluded path named as an
  unresolved scope item;
- commands actually run and their exact outcome; distinguish fresh execution
  from supplied, historic, or carried-forward evidence;
- every finding's location, trigger, impact, and disposition; and
- an explicit review decision: `accept`, `reject`, or `unknown`, plus
  `scope_complete: true|false`.

An `accept` requires `scope_complete: true` and no unresolved finding, warning,
parser failure, evidence gap, or unknown. A review acceptance is not authority
to deploy, mutate production, or broaden the assigned scope.

## Source and evidence transport

When a review decision depends on source, tests, logs, or other artifacts, the
receipt must state how the reviewer accessed the complete required bytes.
Paths, hashes, pointer IDs, storage success, and a compact index prove
provenance or storage; they do not alone prove reviewer access.

For paged or partitioned evidence, record the correlation ID, exact manifest,
full digests, ordered page or partition receipts, and a completion condition
that proves every declared artifact was available and processed. Missing,
reordered, stale, truncated, or digest-mismatched evidence makes the decision
`unknown` and blocks a completion claim until corrected.

## Receiving a receipt

Before accepting a peer's completion claim, verify that its current revision,
scope, evidence, and status match the requested work. If the receipt covers
only a subset, says a dependency is pending, relies on inaccessible source, or
omits a required criterion, record it as progress or an explicit blocked/unknown
state—not completion.
