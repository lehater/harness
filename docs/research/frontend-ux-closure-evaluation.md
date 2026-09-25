# Evaluation — granular frontend UX knowledge closure

Status: experimental evaluation after synthetic Harness validation and real Prep consumer test.

Branches:

- Harness: `research/frontend-ux-closure-v1`
- Prep: `research/frontend-ux-closure-v1`

No merge/canonicalization decision is made by this document.

## Result

The experiment supports the **direction** of splitting Human Interface knowledge into independently addressable capabilities while keeping one HUMAN-INTERFACE-DESIGN Authority.

The current patch should **not** be canonicalized as-is yet.

Both final CI runs pass:

- Harness `make harness-check`: PASS on `02770055e1f56d96520f44cda9da264957ef0d83`;
- Prep full Validate workflow: PASS while pinned to that Harness SHA.

## What the experiment validated

### 1. Knowledge granularity is useful without Authority proliferation

The following knowledge kinds behaved as independently useful public contracts under the existing HUMAN-INTERFACE-DESIGN Authority:

- `conceptual-interface-model`;
- `information-architecture-design`;
- `interaction-design`;
- `interface-topology-design`.

Prep supplied materially different knowledge for each rather than four names for the same document.

### 2. Site/app maps can remain projections

Prep's site map initially contained structural information that was not represented canonically: application shell, target workspace and curation workspace.

The experiment added explicit `structural: true` topology views. After that change, the site map no longer needs to own extra semantic structure.

Therefore the useful invariant is not “a sitemap file must exist”. It is:

> all material task views and structural frames must be present in canonical Interface Topology; a sitemap/app map may visualize them.

### 3. A completeness chain catches omissions that Screen/View validation alone cannot

The executable closure is:

```text
USER task
  -> Interaction Design context or explicit no-ui disposition
      -> Interface Topology task view or explicit non-view disposition
          -> required Screen/View subject
```

The synthetic fixture proves failures for:

- uncovered USER tasks;
- interaction contexts lost before topology;
- unknown conceptual references in IA;
- missing topology-derived Screen/View subjects;
- structural frames incorrectly claiming task interaction contexts.

### 4. Real-project use found Harness-model defects

Prep exposed defects that the synthetic fixture initially missed:

- Interaction Design was accidentally coupled to IA through `location_ref`, contradicting the intended parallel production branches. The evaluator and skill contract were corrected so Topology performs the placement/mapping.
- Structural shells/workspaces were present in the human site map but absent from canonical topology. `structural: true` topology views were introduced.
- These failures demonstrate that a real consumer project adds material evidence beyond self-validation of Harness.

### 5. The missing Prep Task Model was made explicit

The old Prep graph skipped the Task Model even though the reference user-facing graph contains that capability.

The experimental Prep graph now makes Task Model an explicit APPLICATION-DESIGN capability upstream of User Journeys and interface knowledge.

This improves task completeness reasoning before screen partitioning.

## Benefits observed in Prep

The new model separates questions that were previously conflated inside broad Human Interface prose:

- what user-facing concepts/modes exist;
- how information is grouped and found;
- what the user does and how the system responds;
- what views/frames exist and how they connect;
- how each individual view is composed.

It also turned the previously manual site-map insight into canonical topology knowledge and made structural workspace frames machine-addressable.

## Remaining problems before canonicalization

### P0 — Existing-project adoption/reconciliation: resolved experimentally through Engineering Coverage

A legacy project graph must not be silently rewritten merely because Harness reference policy evolved.

The experiment now uses the existing Engineering Coverage mechanism as the independent migration/completeness lens:

- `FRONTEND` Consumer activation requires the granular human-interface concerns independently of pre-existing granular providers;
- a legacy graph with only broad `human-interface-design` therefore receives `MISSING / MODEL_PRODUCTION_CONTRACT` rows for conceptual model, information architecture, interaction and navigation/topology;
- the standard Authority-role mapping routes those missing semantic claims to HUMAN-INTERFACE-DESIGN;
- `project-bootstrap-reconcile` is updated to run this Coverage diagnostic after conservative registry/graph reconciliation;
- no Capability is inserted automatically.

A regression test in `validate_engineering_coverage.py` proves the legacy broad frontend example cannot hide the new obligations.

### P1 — Screen/View subject coverage: resolved experimentally without a sidecar

Harness now provides a generic `evaluate_topology_screen_subject_coverage(topology, screen_subjects)` evaluator.

The invariant is format-independent:

- Interface Topology owns the expected material view/frame subject set;
- the project owns an adapter that extracts Screen/View subject ids from its canonical Screen/View artifact format;
- Harness compares the two sets and rejects missing or unexpected subjects.

Prep no longer needs a manually maintained `screen-view-subject-coverage.yaml`; stable view ids are embedded in its existing canonical Screen/View Markdown and extracted by the project integration adapter.

This preserves the Integration Contract: Harness contains no Prep-specific parser, and project artifact format remains project-owned.

### P1 — Broad `human-interface-design` now overlaps granular capabilities

For migration compatibility, the experiment retained the old broad Human Interface capability downstream of conceptual/IA/interaction/topology.

Its independent public meaning is now weak.

Before canonicalization choose one:

1. define a genuinely independent synthesis/integration contract for broad Human Interface; or
2. retire/deprecate the broad capability and let consumers depend on the granular contracts they actually need.

Keeping both indefinitely risks duplicate truth.

### P1 — Structural closure is not semantic-quality proof

`frontend_interface_knowledge.py` currently proves reference integrity and completeness relationships. It does not prove that an IA grouping is usable, an interaction recovery path is sufficient, or a conceptual model matches users.

That is intentional for structural closure, but the new concern claims are marked as requiring semantic evaluation. Canonicalization therefore needs a clear path for per-kind semantic acceptance evidence rather than treating structural validation as full UX quality proof.

### P2 — Early verification topology needs policy refinement

The experiment demonstrates that early interface verification can exist before local Screen/View design without creating a graph cycle.

That pattern is useful, but its exact placement should be consumer/project dependent. Harness should support early IA/findability/interaction verification rather than universally force a particular product-development sequence.

## Recommendation

Do not merge the experiment as-is.

Retain the branch and proceed with a second research iteration focused on the four issues above, especially P0 legacy/reconciliation detection and P1 generic subject coverage.

The central design hypothesis is supported:

> HUMAN-INTERFACE-DESIGN should own several independently addressable knowledge contracts, and Interface Topology should be the canonical completeness boundary for view/frame identity and navigation; site maps remain projections.

The remaining work is primarily Harness control/coverage integration and simplification, not a reversal of that knowledge model.
