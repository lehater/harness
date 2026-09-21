# Repository Realization Design v1

Status: canonical candidate.

## Purpose

Close the last implementation-facing structural gap without prescribing a universal directory tree, build system or toolchain.

Repository Realization is a facet of `implementation-design`. It materializes accepted architecture/component/policy/security/quality/verification decisions into a physical codebase and enforceable developer/integration toolchain.

## Ownership

`IMPLEMENTATION-DESIGN` owns:
- mapping accepted semantic/component modules to physical repository/package roots;
- selected repository topology where not already architectural;
- concrete tool choices for already-applicable obligations;
- dependency/environment reproducibility mechanism;
- generated/source/config/test/migration topology needed for coding;
- authoritative quality-gate wiring when the delivery workflow has merge/release gates;
- explicit implementation freedoms.

It does not re-own module semantics, dependency direction, security policy, quality targets or verification truth.

## Core invariants

1. Physical structure follows semantic cohesion, ownership, independent change, dependency direction, visibility/deployability and locality of change.
2. Folder names are not architecture. Accepted boundaries and forbidden edges are.
3. Architecturally significant forbidden dependencies have deterministic mechanical enforcement.
4. Tool obligations are stated independently from products; concrete products are replaceable realization decisions.
5. Versioned project inputs are sufficient to reproduce the dependency/tool/build environment to the level required by the project.
6. Human-authored and generated artifacts are distinguishable; generators and canonical source are explicit.
7. When merge/release gating is applicable, its authoritative enforcement boundary is explicit and reproducible. In PR/CI workflows that boundary is normally CI. Local/pre-commit checks optimize feedback and reuse the same semantics where practical, but are not a second source of truth.
8. Generated tree/config/guide outputs are projections, never a second source of truth.

## Applicability

Each obligation is one of `REQUIRED`, `NOT_APPLICABLE`, `DEFERRED`, or `QUESTION`.

Applicability is derived from accepted project facts where mechanically safe (persistence, external dependencies, deployable/package artifacts, generated files, security boundaries, multiple packages, merge/release workflow) and otherwise declared explicitly with rationale.

Silence for a known applicable facet is incomplete.

## Minimal structured contract

A project-native structured artifact should be able to express:

```yaml
version: 1
kind: repository-realization-design
status: accepted
module_realizations:
  - semantic_owner: ...
    physical_root: ...
    public_boundary: ...
dependency_rules:
  - rule: ...
    enforcement: ...
obligations:
  - id: deterministic-formatting
    applicability: REQUIRED
    enforcement: {tool: ..., command: ..., gate: ...}
generated_artifacts:
  - path: ...
    source_of_truth: ...
    regenerate: ...
environment:
  dependency_resolution: ...
  lock_or_equivalent: ...
gate_policy:
  applicability: REQUIRED
quality_gates:
  - id: ...
    trigger: pull_request
    blocking: true
    command: ...
implementation_freedoms:
  - ...
```

For a project without an applicable merge/release gate:

```yaml
gate_policy:
  applicability: NOT_APPLICABLE
  rationale: ...
quality_gates: []
```

Exact field extensions are project-native; Harness only requires the semantic invariants.

## Completeness

Repository realization is complete for an Implementation consumer when:
- required implementation modules have a physical realization;
- required dependency rules have enforcement;
- applicable obligations have enforcement or an explicit terminal disposition;
- generated/source and migration/test boundaries are decided when applicable;
- environment/dependency resolution is reproducible as required;
- authoritative gates are explicit when merge/release gating is applicable, otherwise non-applicability is explicit;
- no unresolved `QUESTION` remains.

No new Authority, Capability family or knowledge kind is required. Projects may expose a separate implementation-design Capability for repository realization when its lifecycle is independently useful, but it keeps `knowledge_kind: implementation-design`.
