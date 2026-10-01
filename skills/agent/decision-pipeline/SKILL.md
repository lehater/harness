---
name: decision-pipeline
description: "Use for a Harness decision-governed Capability. Run option formation, critical decision-space review, choice/escalation, candidate production and semantic admission sequentially, then recompute the project roadmap."
---

# Decision Pipeline

## Trigger

Use when Harness marks a Capability READY in the Decision Roadmap, including an
explicitly requested REDO.

## Inputs

- the READY Capability work unit;
- its Harness-generated pre-choice Decision Exploration request;
- accepted prerequisite/support artifacts;
- for REVISION/REDO, the current accepted provider baseline;
- the knowledge-kind Decision Governance contract and project policy.
- persisted Decision Pipeline failure evidence when a previous attempt ended in FAILED_VALIDATION.

## Read boundary

Treat the work unit read set as the complete project input boundary for
pre-choice option formation. In REDO/REVISION, the current accepted provider is
part of that boundary.

Do not read or invent a future candidate, preferred solution or decision review
before option formation is complete.

## Procedure

1. FORM OPTIONS: inspect every required decision axis, run required challenge
   strategies and describe materially distinct alternatives without selecting.
2. REVIEW OPTIONS: review every discovered decision point for mixed concerns,
   missing material cases, accepted-constraint conflicts and Authority-boundary
   mistakes. Refine locally until the decision-space review is COMPLETE.
3. If review exposes an unresolved semantic fact, create a Core Question
   addressed to its owning Authority, block the affected artifact/capability and
   finish this Capability as BLOCKED.
4. CHOOSE OR ESCALATE: classify reviewed alternatives VIABLE/REJECTED/UNKNOWN
   and apply DETERMINED/DELEGATED/ESCALATED under project autonomy.
5. Any ESCALATED decision uses the existing Core Question mechanism.
6. PRODUCE CANDIDATE from the reviewed/accepted decision dispositions.
7. Run strict SEMANTIC ADMISSION with the same Decision Exploration request mode.
8. Form the complete next Project Publication for CURRENT, BLOCKED or
   FAILED_VALIDATION against the revision from which this work started.
9. Atomically publish that revision through the direct publication helper or the
   project-native adapter transaction. Do not persist Core/evaluation/lifecycle/
   failure components independently.
10. Recompute the Decision Roadmap from the newly published revision and continue
    with another READY Capability.

## Critical review requirement

The Decision Exploration evidence is incomplete unless
`decision_space_review` is COMPLETE and covers every discovered decision point
with all required checks:

- `mixed-decision-split`
- `missing-material-case-search`
- `accepted-constraint-cross-check`
- `authority-boundary-cross-check`

Any open material gap blocks choice.

## Failure discipline

A malformed decision space discovered after the review gate is
FAILED_VALIDATION. Persist reproducible failure evidence. Ordinary roadmap
recomputation must keep that Capability non-READY until an explicit retry.
Correct the failing procedure/evidence and explicitly redo the Capability. A
failed CREATE retries in CREATE mode because no accepted current provider exists;
do not invent a REDO baseline.

## Output contract

Prepare only the evidence appropriate to the actual result, then commit it
through one Project Publication transition:

- CURRENT: accepted Decision Exploration + Decision Governance + candidate
  Core realization + admission/lifecycle evidence, with any resolved Question
  state and previous failure entry cleared coherently;
- BLOCKED: Core Questions plus any useful noncanonical analysis;
- FAILED_VALIDATION: failure-set entry with Capability, failure id, failing
  pipeline stage and validation finding sufficient to reproduce the defect.

The terminal result is published only after the complete snapshot validates.

## Registration

Pipeline state is not registered in Core. Only canonical artifacts, lifecycle
acceptance and unresolved/resolved Core Questions affect project truth.
