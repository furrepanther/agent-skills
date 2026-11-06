# Red-Team Gate diagnostic lane selectors

Use these selectors only with the sanctioned local Red-Team Gate wrapper and
its normal typed review packet, output path, and private raw-evidence
directory. They reduce diagnosis time; they do not reduce the requirements for
a full gate.

## Selectors

Exactly one selector may be supplied:

- `--SD-only` (alias `--sd-only`) runs the built-in SDLC security,
  reliability, testing, and evaluator package only.
- `-SS-only` (aliases `--SS-only`, `--ss-only`) runs only the sanctioned
  Solid Snake executable. `--solid-snake-runner` is required.
- `--GR-only` (alias `--gr-only`) runs only the sanctioned Grumpy executable.
  `--grumpy-runner` is required.

Selectors are mutually exclusive with one another, `--dry-run`, and
`--test-unreachable-router`. Each selected package retains the wrapper's
typed-packet checks and local-only router preflight. External Solid Snake and
Grumpy runners must still return their required local-route attestation.

## Result contract

A diagnostic run must record all of the following:

- `mode: diagnostic_sdlc`, `diagnostic_solid_snake`, or
  `diagnostic_grumpy`;
- `diagnostic_only: true`;
- a `diagnostic_pass`, `diagnostic_revise`, or `diagnostic_blocked` status;
- `full_gate_completed: false`;
- `promotion_eligibility: not_eligible_diagnostic_only`; and
- `empty_boat: false`, even if the selected package reports no findings.

Only the selector-free full sequence may set `full_gate_completed: true` and
may produce `empty_boat: true`. A diagnostic result can guide a repair or
rerun, but must be followed by the complete gate before a promotion decision.
