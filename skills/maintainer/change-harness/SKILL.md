---
name: change-harness
description: "Use when modifying Harness behavior, contracts, routing, validators, runtime mechanisms or canonical architecture. Require reproducible evidence, scenario/acceptance coverage and full validation before integration."
---

# Change Harness

## Trigger

Use for changes to Harness itself that can affect observable behavior,
architecture contracts, routing/discovery, validation semantics, Core behavior,
Consumer Pack behavior or agent-facing procedures.

This is a Maintainer operation. It is not exported to target repositories.

## Inputs

- requested Harness change or confirmed HARN finding;
- relevant canonical design/specification;
- `docs/design/harness-assurance-policy-v0.md`;
- `docs/design/harness-ability-to-evidence-v0.md`;
- current non-main branch state;
- existing Scenario Suite/acceptance coverage;
- related EVO/HARN records when present.

## Procedure

1. Confirm work is occurring on a non-main branch. Never implement directly on
   `main`.
2. Identify the owning bounded context/layer and map the change to the
   applicable canonical Harness ability/failure mode in
   `docs/design/harness-ability-to-evidence-v0.md`; identify the canonical
   contract that defines the behavior. Do not let a skill or README become a second
   semantic owner.
3. If the change touches CI triggers, gate composition, validator/test inventory
   or check ordering, load `docs/design/ci-execution-policy-v0.md` and
   `spec/ci/check-registry-v0.yaml` before editing execution behavior.
4. State/reuse the concrete failure, invariant or accepted architecture
   decision that justifies the change.
5. Apply `docs/design/harness-assurance-policy-v0.md`: choose the lowest test
   level that can falsify the affected failure mode. Reuse reviewed evidence or
   a reviewed Test Design from
   `docs/design/harness-test-design-catalog-v0.md` before inventing a new test
   shape. Before changing observable behavior, add or update the smallest
   failing deterministic acceptance/scenario evidence that expresses the
   intended invariant when such an oracle exists. For judgement-dependent
   behavior, use the behavioral-evaluation protocol rather than pretending a
   supplied route/model key proves agent judgement. Do not substitute a larger
   real-project/E2E test for a missing lower-level mechanism oracle.
6. For a Core extension, require the concrete consumer failure and acceptance
   fixture required by `docs/design/core-v0.md`; do not add workflow/process
   entities without demonstrated need.
7. If the change affects cross-layer consumer-visible behavior, classify/update
   it in the Scenario Suite according to
   `docs/design/scenario-suite-v0.md`. A subsystem validator does not replace a
   cross-layer scenario when several Harness mechanisms participate.
8. Implement the smallest coherent change and update canonical contracts,
   registries and migrations together.
9. Run the smallest deterministic affected validators/tests during iteration.
   For CI topology/inventory changes, run `python validators/validate_ci_policy.py`
   before broader checks so policy failures stop expensive work early.
10. Run the full applicable repository gate (`make harness-check` / PR workflow)
   on a coherent candidate.
11. Keep integration as a draft/non-main change until all applicable checks are
    green and the resulting Harness behavior has been reviewed. Integration to
    `main` is a separate squash-merge action.

## Stop conditions

Stop the implementation path and record/research the issue instead when:

- the desired behavior has no accepted semantic owner;
- the proposed fix requires inventing a new Core/process concept without a
  demonstrated consumer failure;
- the only justification is aesthetic relocation with no ownership/routing
  improvement;
- deterministic or scenario evidence contradicts the proposed behavior.

## Output

A coherent non-main change set with:

- updated implementation/contracts;
- regression or acceptance evidence appropriate to the behavior;
- updated HARN/EVO status when applicable;
- green focused checks and, before integration, green full repository gates.
