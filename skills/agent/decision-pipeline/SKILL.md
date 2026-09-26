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
8. Finish as CURRENT, BLOCKED or FAILED_VALIDATION.
9. Recompute the Decision Roadmap and continue with another READY Capability.

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
FAILED_VALIDATION. Do not introduce an automatic role-switch/reexploration
workflow. Correct the failing procedure/evidence and explicitly redo the
Capability.

## Output contract

Persist only the evidence appropriate to the actual result:

- CURRENT: accepted Decision Exploration + Decision Governance + candidate
  admission/lifecycle evidence;
- BLOCKED: Core Questions plus any useful noncanonical analysis;
- FAILED_VALIDATION: validation finding sufficient to reproduce the defect.

## Registration

Pipeline state is not registered in Core. Only canonical artifacts, lifecycle
acceptance and unresolved/resolved Core Questions affect project truth.
