# Primus Local Red-Team Gate Runtime

This directory is the shared, versioned runtime for the revised local
Red-Team Gate. It is intended to be runnable from both Primus and Datacube
through the shared `agent-skills` checkout. It is not the Primus Forge harness
and it does not promote or modify that unfinished research project.

## Contract

- Default inference is local-only through `http://127.0.0.1:11888/v1`.
- Run the gate with `--local`; the gate must not call llama.cpp directly.
- The gate runs the enabled SDLC lanes, then Grumpy as the hostile final lane.
- Complete source bytes, UTF-8 validity, full digests, duplicate paths, size
  boundaries, acceptance coverage, and cleanup evidence are fail-closed.
- When a complete packet exceeds the lane ceiling, the wrapper rehydrates and
  verifies a bounded set of UTF-8 `SOURCE_PAGES` continuation pages per lane
  from the exact temporary pointer. Each page has a parent packet digest, page
  digest, selector, byte cap, and receipt; a pointer alone is never reviewer
  access.
- Grumpy receives the full acceptance criteria plus verified route receipts
  from every child lane, including endpoint, adapter, request, and local/cloud
  status evidence.
- Temporary evidence uses the canonical loopback Mem0 API from
  `ANTIGRAVITY_MEMORY_API_URL`/`PRIMUS_MEMORY_API_URL` when supplied, otherwise
  `http://127.0.0.1:8001`; remote URLs and retired `18000`/`18001` defaults are
  rejected.
- Targeted repair may rebuild an affected lane from the authoritative packet,
  but it may not weaken a finding or retry an unchanged packet.
- Temporary generated configuration and review material belongs under `/tmp`;
  no scratch or review material belongs in a backup directory.
- No cloud credential or secret is included in this runtime.

## Usage

From the shared checkout:

```bash
skills/red-team-gate/runtime/primus-local-v1/bin/run-red-team-gate \
  --input /path/to/attested-packet.json \
  --output /tmp/primus-review/gate-result.json \
  --raw-dir /tmp/primus-review/gate-raw \
  --local
```

The packet must be constructed and attested by the shared Red-Team Gate
builder before dispatch. A valid HTTP response is not a promotion decision;
the result must show all expected lanes complete, Grumpy clean, no unresolved
findings, and an empty boat. Promotion still requires explicit owner approval.

## Provenance

The runtime is assembled from the reviewed Primus production wrappers and
their current prompts, schemas, reviewer profiles, and inference-mode helper.
The wrapper copies use runtime-relative defaults so the shared checkout works
under both `/linuxdata/Github/...` on Primus and `/mnt/linuxdata/Github/...`
on Datacube. The original production wrappers remain authoritative until an
owner-approved promotion.

See `MANIFEST.json` for exact source and bundle hashes, and `RUN.md` for the
cross-system installation/verification procedure.

The current verification receipts are `verification/empty-boat-v21-result.json`
and `verification/solid-snake-local-review-v1.json`. The v21 receipt covers
the post-fix production source-validation review: six SDLC lanes, Grumpy, and
inline documentation completed with zero blocking or unresolved findings.
