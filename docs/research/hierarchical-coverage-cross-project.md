# Research — Hierarchical Coverage cross-project comparison

Status: research only.

## Selected concern comparison

| Concern | NAPMS | Nutrition | Tiny ETL |
|---|---|---|---|
| intent.behavior | COVERED | COVERED | COVERED |
| interface.human.accessibility | UNASSESSED | COVERED | NOT_APPLICABLE |
| data.quality | COVERED | COVERED | COVERED |
| data.classification | UNASSESSED | UNASSESSED | UNASSESSED |
| security.identity | COVERED | NOT_APPLICABLE | NOT_APPLICABLE |
| security.threat-analysis | COVERED | UNASSESSED | COVERED |
| security.vulnerability-management | UNASSESSED | UNASSESSED | UNASSESSED |
| reliability.failure-semantics | COVERED | COVERED | COVERED |
| reliability.availability | NOT_APPLICABLE for first-MVP numeric objective | UNASSESSED | NOT_APPLICABLE for batch-service objective |
| reliability.recovery | UNASSESSED | UNASSESSED | COVERED by deterministic rerun |
| reliability.consistency | COVERED | COVERED | NOT_APPLICABLE |
| operability.logging | COVERED | UNASSESSED | COVERED/lightweight |
| operability.metrics | COVERED/lightweight diagnostic measurements | UNASSESSED | NOT_APPLICABLE |
| operability.tracing | COVERED by correlation; tracing backend N/A | UNASSESSED | NOT_APPLICABLE |
| quality.performance.resource-efficiency | UNASSESSED | UNASSESSED | COVERED |
| quality.maintainability.modularity | COVERED | COVERED | COVERED |
| verification.interface.human | MISSING | COVERED | NOT_APPLICABLE |

## What the comparison exposed

### NAPMS

The old coarse map overstated Quality and Reliability completeness.

Strong coverage:
- identity/authorization/trust boundaries;
- threat analysis;
- consistency and failure semantics;
- request correlation and dependency diagnostics;
- maintainability boundaries;
- verification strategy.

Visible gaps after decomposition:
- recovery/continuity;
- resource efficiency;
- secure-development/vulnerability lifecycle;
- human-interface quality and verification;
- data classification/lifecycle;
- privacy/external-obligation applicability.

### Nutrition

The old coarse map understated actual design coverage because evidence is distributed.

Previously hidden coverage:
- accessibility/usability baseline;
- coherent-read consistency;
- data quality/provenance/reproducibility;
- local-browser trust boundary;
- failure semantics;
- maintainability/testability.

Still genuinely unassessed:
- systematic threat analysis;
- privacy/data classification;
- broad data lifecycle/governance;
- availability/recovery;
- logging/metrics/tracing/health/alerting;
- performance targets.

### Tiny ETL

The model stays lightweight when explicit scope decisions collapse irrelevant branches.

Useful concerns remain:
- input/output data quality;
- deterministic/reproducible transformation;
- bounded resources;
- failure semantics;
- CLI/schema contract;
- simple diagnostic errors;
- dependency/supply-chain hygiene;
- verification.

Large subtrees disappear through explicit N/A:
- human interface;
- identity/authorization;
- service availability;
- distributed tracing/health/alerting;
- distributed consistency.

## Research automation estimate

Current design permits three derivation classes:

1. **Direct graph/lifecycle derivation** — provider, Authority, artifact path, Consumer, Questions/blockers, missing provider, lifecycle freshness.
2. **Catalog mapping + automatic graph derivation** — concern maps once to capability/knowledge kinds, then project evidence is resolved automatically.
3. **Explicit applicability judgment** — privacy, regulatory obligations, safety, whether a target is needed, or ambiguous scope-specific exclusions.

Estimated current pilot split:

| Project | Direct | Mapping then automatic | Human applicability |
|---|---:|---:|---:|
| NAPMS | ~58% | ~27% | ~15% |
| Nutrition | ~51% | ~31% | ~18% |

These numbers are directional research estimates over the current refined leaves. They should not become product claims until the next prototype derives rows from the actual graph and records provenance for each derivation.

## Main conclusion

The cross-project value appears only after decomposition to independently decidable semantic leaves.

The catalog is useful when the same concern id can legitimately be:
- COVERED in one project;
- NOT_APPLICABLE in another;
- UNASSESSED or MISSING in a third;

without requiring the same artifact type or engineering depth.
