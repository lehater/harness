# Research — Machine-proof coverage experiment

Status: research only. No canonical or main changes.

## Question

Can the current project Harness knowledge prove Engineering Concern coverage algorithmically, without reading prose and without trusting a manually maintained coverage map?

## Strict proof rule

For this experiment:

- exact concern-specific semantic CapabilityId = proof;
- artifact kind, filename, broad capability and substring match = candidate evidence only;
- candidate evidence can guide investigation, but cannot derive `COVERED`.

This is intentionally stricter than the first prototype.

## Result

Against the current manually reviewed research oracles:

| Pilot | Reviewed concern rows | Concerns currently machine-provable by exact reusable claims |
|---|---:|---:|
| NAPMS | 83 | 4 |
| Nutrition | 90 | 0 |

NAPMS currently proves these reusable concerns directly:

- `interface.machine.contract` via `engineering.interface.http-contract`;
- `data.model` via `engineering.data.persistence-model`;
- `security.threat-analysis` via `engineering.security.threat-analysis`;
- `verification.strategy` via `engineering.verification.strategy`.

Nutrition contains substantial accepted knowledge, but its current project-specific CapabilityIds do not expose a reusable semantic proof vocabulary fine-grained enough for the generic Concern Catalog.

The low number is **not** evidence that the projects are poorly designed. It is evidence that their current machine-readable knowledge contracts are too coarse or too project-specific for a universal algorithmic completion gate.

## Important false-positive found

The first prototype incorrectly allowed a broad artifact such as an observability document to prove multiple leaves:

- logging;
- metrics;
- tracing;
- health/readiness.

That is unsafe.

Likewise:

- "numeric availability target not required" does not make availability `NOT_APPLICABLE`;
- "numeric latency target not required" does not make latency `NOT_APPLICABLE`;
- correlationId does not prove tracing;
- duration/count log fields do not prove a metrics/SLI design;
- dependency failure distinctions do not prove health/readiness diagnostics.

The NAPMS research oracle and overlay were tightened accordingly.

## Architectural implication

If Coverage State is to control planning and completion, Harness needs a **machine-proof contract** between canonical engineering knowledge and the Concern Catalog.

A proof contract must answer:

> Which accepted semantic claim is sufficient evidence that this concern has been considered/decided for this scope?

The contract should not be inferred from prose or file names.

## Candidate designs

### A. Universal CapabilityIds

Example:

```yaml
provides:
  - engineering.operability.logging
  - engineering.operability.tracing-correlation
```

Pros:
- direct;
- simple;
- excellent provenance.

Cons:
- can over-standardize project capability naming;
- domain-specific capabilities still need their own namespace.

### B. Stable `knowledge_kind` on capabilities/artifacts

Example:

```yaml
produces:
  - capability: nutrition-management.frontend.security
    knowledge_kind: engineering.security.boundaries
```

Concern registry:

```yaml
security.boundaries:
  accepted_knowledge_kinds:
    - engineering.security.boundaries
```

Pros:
- project CapabilityId remains project-specific;
- reusable semantics live in Harness;
- best fit with the existing Engineering Graph concept, which already supports `knowledge_kind`.

Cons:
- knowledge kinds must be sufficiently granular;
- migration needed for projects that currently expose only project-local provides.

### C. Artifact-level `covers_concerns`

Example:

```yaml
covers_concerns:
  - security.boundaries
  - security.confidentiality
```

Pros:
- very explicit.

Cons:
- high risk of becoming a second manually maintained truth source;
- easy to mark a concern covered without defining why the artifact is authoritative.

This is not recommended as the primary model.

## Current preferred direction

Use **B: stable knowledge kinds**, with exact CapabilityIds still allowed as direct proof where already universal.

Target chain:

```text
Authority
  -> produces Capability
       -> knowledge_kind
            -> reusable concern-proof mapping
                 -> Concern Coverage State
```

Artifact realization proves that the capability/knowledge kind has actually been materialized and accepted.

This keeps project-specific naming and universal engineering semantics separate.

## Completion algorithm

For an activated concern:

1. resolve accepted proof kinds from the reusable Concern Catalog/mapping;
2. find a producing Authority/Capability in the project Engineering Graph;
3. verify required prerequisites;
4. verify an accepted/current CanonicalArtifact realizes that production;
5. verify no blocking Question/lifecycle invalidation exists;
6. only then derive `COVERED`.

If the concern is activated but:
- no producer exists -> `MISSING`;
- producer is blocked -> `BLOCKED`;
- evidence exists but proof semantics are insufficient -> `UNASSESSED` + attention required;
- accepted proof is stale -> `STALE`.

## Research conclusion

The Coverage Map concept is viable as an algorithmic planner/completion gate, but **the current canonical machine vocabulary is not yet rich enough to prove most leaves automatically**.

The next experiment should therefore focus on a concern-proof/knowledge-kind contract, not on adding more manual coverage rows.
