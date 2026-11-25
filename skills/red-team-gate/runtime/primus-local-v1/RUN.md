# Running the Shared Gate

1. Verify the shared checkout is current and clean enough for this runtime;
   do not overwrite unrelated dirty work.
2. Run the local inference preflight on the host that will execute the gate.
3. Construct the packet with the shared builder and verify its serialized
   digest before dispatch.
4. Run `bin/run-red-team-gate` with `--local`, an explicit input packet, an
   output file, and a task-scoped raw-output directory under `/tmp`.
5. Require all enabled lanes, Grumpy, inline documentation, and cleanup proof
   to complete with no warnings, errors, unresolved findings, or `unknown`.
6. Preserve the result and bounded evidence paths as the review receipt. Do not
   promote or alter production solely because the command returned zero.

The launcher creates one temporary host-specific config from
`config/reviewers.template.json` and removes it on normal exit. It sets
`PYTHONPATH` only for the child process and never installs packages or mutates
the host interpreter.

The only supported cross-system control transport remains SSH TCP/22. TCP
22022 is filesystem sharing only. Agent Mail work orders go to Datacube's
canonical `PurpleCanyon` identity after peer preflight and authenticated
receipt; `RoseStone` is the Primus logical owner and `SwiftCat` is transport.
