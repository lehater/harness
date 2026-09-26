---
name: decision-explorer
description: "Use before producing a candidate for a decision-governed knowledge kind. Blindly challenge required decision axes and produce noncanonical alternative-space evidence without selecting a solution."
---

# Decision Explorer

## Trigger

Use when an actionable routed capability has an active project Decision Governance
policy and its knowledge kind has a decision contract.

Run this pass before candidate production or selection.

## Inputs

The only project context for this pass is the Harness-generated
`harness-decision-explorer-request`. Do not inherit a producer conversation or
candidate draft into the explorer context.

- actionable capability and knowledge kind;
- accepted prerequisite/support knowledge from the Harness-generated Explorer Request;
- the knowledge-kind decision contract;
- the effective project exploration policy;
- no preferred candidate solution.

## Procedure

1. Consume the Harness-generated Explorer Request. Treat its canonical input manifest as the complete allowed project context for this pass.
2. Load every required decision axis and its material dimensions/challenge strategies.
3. Establish applicability from accepted canonical knowledge. Do not use silence as NOT_APPLICABLE.
4. For every APPLICABLE axis, run the required number of distinct challenge strategies.
5. Generate alternative classes without ranking or choosing them.
6. Describe each alternative through material effects on the registered dimensions.
7. At RESEARCH or deeper, collect the required external evidence before closing the exploration pass.
8. If applicability itself cannot be established, mark it UNRESOLVED and route the missing semantic decision to the owning Authority.
9. Emit a harness-decision-exploration document with the exact Explorer Request `request_id`. Do not include selected/preferred/chosen/disposition fields.
10. Only after this evidence exists may the artifact producer evaluate viability and form the candidate.

The explorer's responsibility is falsification of apparent uniqueness, not approval
of the producer's first idea.

## Output contract

Noncanonical `harness-decision-exploration` evidence containing:

- capability and knowledge kind;
- per-axis applicability;
- exploration level;
- challenge probes;
- discovered decision points;
- materially distinct alternatives;
- research-source provenance where required.

## Stop conditions

Stop without candidate production when:

- a required axis is UNRESOLVED;
- required probe diversity cannot be performed;
- RESEARCH evidence cannot be obtained at the required level;
- the decision contract itself is insufficient to distinguish material alternatives.

## Registration

Do not register Decision Exploration in Core. It is semantic-admission evidence only.
Only later unresolved governance outcomes become Core Questions.
