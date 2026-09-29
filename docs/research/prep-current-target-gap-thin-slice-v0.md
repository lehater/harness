# Prep current-target-gap thin slice v0

Status: completed; executable scenario validated by the unchanged harness core.

## Purpose

Trace one user-facing meaning from accepted problem evidence to the last pre-code frontend design boundary:

desired/target state + evidence-backed current state -> meaningful gap -> what deserves attention -> learner-facing representation.

The experiment asks whether the current Prep scope silently loses this meaning, and whether Harness detects the missing downstream design if that meaning is activated as current scope. Production code is not evaluated.

## Baselines

Harness: lehater/harness@36c5b45aa8d60d3fa317d6ea7f46da2265b7310a

Prep: lehater/prep@b3ec3b0fec0d8ba29f2ca66867737e8838332592

Scenario: spec/scenario-suite/scenarios/real-project-prep-current-target-gap-thin-slice.yaml

## Canonical Prep evidence

Problem Space says a person needs to move from current knowledge/ability to a desired state, current state is only partially observable, enough current state must be established to identify meaningful differences, and those differences guide what needs attention.

Vision preserves the same direction. Product Capabilities defines PC-09 Progress and adaptation: show the learner their current evidence-backed position relative to the target and use changing evidence to revise gaps, priorities and subsequent learning activity.

The same PC-09 contract explicitly defers automatic statistics -> learner state -> gaps -> priorities -> replanning from the current slice.

Learning Design already defines Gap as a target-relative difference between required capability and evidence-backed learner state. Learner Model does not yet define the inference from recorded review statistics to accepted learner state. Application Design therefore stops at factual review statistics and explicitly defers learner-state inference, gaps, priorities and replanning.

Task Model preserves that boundary through TASK-L-REVIEW-FACTS: inspect factual ReviewObservations/statistics without mastery/readiness/retention inference. User Journeys do not assert a current gap-analysis journey.

The human interface remains aligned:
- Conceptual Interface defines REVIEW-FACTS as factual observations/statistics without mastery inference.
- Interaction Design defines I-L-STATISTICS around factual aggregates/history.
- Screen/View Design defines Statistics as factual evidence and forbids relabeling it as mastery/readiness/proficiency/retention.
- Screen/View Design separately marks a learner-state overlay as future and not currently implementable until accepted Question-to-Knowledge state inference exists.

At the last pre-code boundary, Frontend Component Design forbids importing experimental progress assumptions as product state, and Frontend Implementation Design excludes learning mastery/readiness inference from current realization scope.

## Experiment

The real current-scope path should remain ACCEPTED because the behavior is explicitly deferred upstream and the downstream artifacts preserve that boundary rather than silently dropping active behavior.

Sensitivity control A replaces the current PC-09 scope atom with an active obligation: the learner must see current evidence-backed position relative to the target and meaningful gaps. Current Application Design is left unchanged. Expected result: UNDISPOSITIONED_SOURCE owned by APPLICATION-DESIGN.

Sensitivity control B supplies an active user task: the learner inspects current evidence-backed position relative to the target and meaningful gaps. Current Conceptual Interface remains factual-review-only. Expected result: UNDISPOSITIONED_SOURCE owned by HUMAN-INTERFACE-DESIGN.

## Validation result

The Scenario Suite passed on the pinned baselines. The real current-scope path is accepted through the pre-code component boundary. Both sensitivity controls are rejected exactly as expected: activated PC-09 localizes to APPLICATION-DESIGN, and an activated current-gap user task localizes to HUMAN-INTERFACE-DESIGN.

No LLM execution was required; after the selected semantic atom was admitted, coverage and localization were deterministic.

## Interpretation

This distinguishes two cases:

- explicitly deferred upstream meaning -> no false RED;
- active upstream meaning + insufficient downstream design -> deterministic RED.

Therefore the current absence of a gap UI in Prep is not itself a defect: the capability is intentionally outside the current slice. But if Prep activates PC-09 without expanding Application/Task/UI design, existing Harness semantic derivation accounting should reject the design and localize the first missing responsibility.

No new Core entity, Authority, workflow state, semantic DSL or LLM oracle is required.

One representational friction remains: semantic.derivation has NOT_APPLICABLE and QUESTION dispositions but no generic DEFERRED disposition. This experiment does not justify changing that contract because the project-owned deferral can be preserved as ordinary accepted semantic content. Revisit only if additional real slices repeatedly make this an adoption blocker.
