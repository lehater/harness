---
name: capture-harness-observation
description: "Use when a Harness maintainer must persist a defect, design gap, recommendation, research question, improvement idea or accepted architecture direction without leaving it only in conversation history."
---

# Capture Harness Observation

## Trigger

Use when asked to record, capture, remember or add a repository-level Harness
observation for future work.

This is a Maintainer operation. It is not part of the Consumer Skill Surface.

## Inputs

- the observation and its supporting evidence;
- current repository state;
- `docs/audit/README.md`;
- existing HARN/EVO ledgers;
- the owning canonical design/spec when the direction has already been accepted.

## Procedure

1. Read `docs/audit/README.md`; it owns the classification policy.
2. Search both the Audit Backlog and Evolution Radar by root cause/direction
   before allocating a new identifier.
3. If current Harness behavior is demonstrably wrong against an invariant,
   contract or reproducible expected behavior, create/reuse a `HARN-*` entry
   and record concrete evidence/consequence.
4. If the observation is optional improvement, recommendation, research or an
   insufficiently proven defect hypothesis, create/reuse an `EVO-*` entry
   with the appropriate type/status and the evidence needed to validate/reject it.
5. If the direction has been explicitly accepted, put normative content in the
   owning design/spec/ADR and mark/cross-link the related EVO as `ADOPTED`.
6. If EVO research proves a current defect, create/reuse the HARN item and
   cross-link rather than silently converting identifier families.
7. Preserve cumulative history: update an existing root cause/direction instead
   of creating wording-level duplicates.
8. Commit the ledger/spec changes on the current non-main working branch.

## Stop conditions

Do not classify something as a defect merely because a different architecture
might be cleaner. When defect evidence is insufficient, capture it as
`RESEARCH / CAPTURED` in the Evolution Radar and state what evidence is missing.

Do not make the Radar the normative owner of an accepted architecture decision.

## Output

One coherent repository update to the owning ledger and, when applicable, the
canonical design/spec containing the accepted decision.
