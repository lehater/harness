# Capability derivation external validation

Status: experimental validation evidence.

## Scope

Validate reusable semantic-derivation test coverage against real Engineering
Graphs without modifying the external repositories.

Pinned sources:

- Prep: `lehater/prep@b3ec3b0fec0d8ba29f2ca66867737e8838332592`,
  `.harness/engineering-graph.yaml`.
- NAPMS: `lehater/napms@42481577fab7f795cf3a2118b7b6f1c3c075d066`,
  `docs/harness-engineering-graph.yaml`.

The exact graph bytes are stored only as external-validation snapshots under
`spec/scenario-suite/fixtures/external/`. They are not canonical project truth.

## Initial result

Comparing direct ProductionContract dependency knowledge-kind pairs against the
existing Harness derivation corpus exposed:

- Prep: 31 produced capabilities, 100 direct dependency edges, 33 uncovered
  knowledge-kind edge classes.
- NAPMS: 55 produced capabilities, 222 direct dependency edges, 83 uncovered
  knowledge-kind edge classes.
- Union: 107 previously uncovered knowledge-kind edge classes.

The missing surface was concentrated in strategic/tactical DDD, application
design, consistency/data/security/operability, broad human-interface migration,
and backend realization/verification.

## Added reusable families

The external gaps justified three additional semantic scenario families:

1. `ddd-application-semantic-derivation` — strategic domain, model-context,
   tactical domain and application/task/journey/interface propagation.
2. `cross-cutting-design-semantic-derivation` — consistency, data, security,
   quality, operability, engineering policy and system-architecture propagation.
3. `realization-verification-semantic-derivation` — broad human-interface,
   component, implementation, verification, acceptance-scenario and test
   propagation.

These are executable `semantic.derivation` scenarios with semantic assertions,
not declarations inserted only to satisfy coverage.

## Final executable validation

`external-project-derivation-test-coverage` runs the normal
`semantic.derivation_test_coverage` driver over both pinned graphs.

Acceptance requires:

- `status: COMPLETE`;
- `gap_count: 0`;
- `invalid_registration_count: 0`;
- `covered_count == edge_count`.

Coverage proof is derived from executable `semantic.derivation` steps.
A scenario name or metadata-only claim cannot satisfy the gate.

## Interpretation

This validates the reusable test vocabulary against two structurally different
real projects in addition to the Harness-owned example graphs. It does not prove
that every future project will use only already-covered knowledge-kind
relationships.

The snapshots are intentionally pinned. When Prep or NAPMS Engineering Graphs
change materially, refresh the snapshot and rerun the gate; a new edge class
must either gain an executable reusable test or an explicit justified
disposition.
