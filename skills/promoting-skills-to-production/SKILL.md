---
name: promoting-skills-to-production
description: Use when reviewing post-pipeline skill repos before mem0/production promotion, including duplicate detection, functional similarity triage, and family-first retrieval packaging.
---

# Promoting Skills To Production

## Overview

This skill defines the standard process for moving skills from post-pipeline staging into production-ready memory.

Primary goals:
- avoid mem0 clutter
- reject near-duplicate noise early
- preserve best core operational guidance
- keep retrieval fast and bounded

## Required Inputs

- Candidate skill repo or skill files under review
- Current mem0 skill corpus (source of truth)
- Local skill index/router cache (fast retrieval layer)

## Non-Negotiable Rules

1. Must compare incoming skills against what already exists in mem0.
2. No exact duplicates may be processed to mem0.
3. Similar functionality must be compared, even when names differ (for example `document_ingest`, `document_ingester`, `document_intake`).
4. Very similar functionality uses family grouping (not raw full-set retrieval).

## Duplicate Gate

### Exact duplicate rejection

Reject immediately if both conditions are true:
- file line count > 20
- normalized diff against an existing mem0 skill <= 5 lines

Normalization guidance:
- trim trailing whitespace
- collapse repeated blank lines
- ignore frontmatter ordering differences
- compare core instruction body, not just metadata labels

## Functional Similarity Triage

Classify each candidate against nearest mem0 skills:

- `exact`: same intent + nearly same wording
- `similar`: same problem space, materially different guidance/details
- `very_similar`: closely overlapping intent and guidance where retrieval ambiguity is likely
- `distinct`: different operational intent

### Required action by class

- `exact`:
  - reject candidate
  - log reason and matched mem0 skill ID/path

- `similar`:
  - compare for core operational value (not prose quality)
  - synthesize one winner skill file containing the best core instructions/data
  - keep only the winner for promotion path

- `very_similar`:
  - use family grouping process
  - avoid flooding retrieval with multiple near-equivalents

- `distinct`:
  - promote normally

## Family Grouping Process (Very Similar Skills)

Create/update family metadata:
- `family_id`
- `family_label`
- `canonical_skill`
- `member_skills`
- `confidence`

Policy:
- mem0 remains source of truth
- selection/ranking runs through local indexed router/cache
- retrieval returns compact family-guided bundles, not full raw sets

## Retrieval Contract (Production)

Input:
- task text
- optional constraints (stack, risk, latency/safety priority)

Output:
- `families`: top 1-3 with confidence
- `candidates`: top 2-4 skills per family
- `final_shortlist`: bounded total 6-10 skills

Rationale:
- prevents over-fetch and context-window bloat
- lowers ambiguity
- keeps response speed predictable

## Promotion Output Checklist

Before promotion:
- [ ] mem0 comparison completed
- [ ] duplicate gate applied
- [ ] similarity class assigned with evidence
- [ ] synthesis or family grouping applied as required
- [ ] retrieval contract fields available (`families`, `candidates`, `final_shortlist`)

Promotion artifacts:
- decision log (accepted/rejected/synthesized/grouped)
- winner skill file(s)
- updated family metadata (if applicable)
- promotion destination in `F:\\Github` for easy access

## Anti-Patterns

- writing directly to mem0 without comparison
- promoting multiple near-identical skills because names differ
- selecting skills by documentation polish instead of operational quality
- returning full family member sets to agents by default

## Quick Decision Table

| Condition | Action |
|---|---|
| lines > 20 and diff <= 5 | Reject as exact duplicate |
| Similar functionality, meaningful new core guidance | Synthesize one winner |
| Very similar functionality, high retrieval ambiguity | Family-group and route by family |
| Distinct functionality | Promote directly |
