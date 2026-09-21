# Research — Quality decomposition for Engineering Coverage Map

Status: research only. Not canonical.

## Decision

Treat **Quality** as a cross-cutting navigation lens over canonical Engineering Concerns, not as a second semantic owner.

Reason: the current ISO/IEC 25010 product-quality model deliberately includes reliability, security and interaction-related characteristics. Harness already needs those as independently navigable engineering concerns with their own applicability, evidence, Authorities and verification. Persisting both `quality.security` and `security.*` would create duplicate state and contradictory coverage.

## Quality lens v1

| Quality area | Canonical state owner |
|---|---|
| Functional suitability | `intent.behavior`, `verification.functional` |
| Performance efficiency | `quality.performance.*` |
| Compatibility | `interface.machine.compatibility`, `quality.compatibility.*` |
| Interaction capability | `interface.human.*` |
| Reliability | `reliability.*` |
| Security | `security.*` |
| Maintainability | `quality.maintainability.*` |
| Flexibility | `quality.flexibility.*` |
| Safety | optional `specialized.safety` module |

Quality-only leaves exist only where no stronger semantic concern already owns the question.

### Performance efficiency

- `quality.performance.latency`
- `quality.performance.throughput`
- `quality.performance.resource-efficiency`
- `quality.performance.capacity`

These must stay separate because a project can explicitly decline a latency SLO while still needing bounded memory or capacity behavior.

### Compatibility

- `interface.machine.compatibility` — version/contract compatibility at the interface boundary.
- `quality.compatibility.interoperability` — ability to exchange/use information with other products/systems.
- `quality.compatibility.coexistence` — ability to share environment/resources without unacceptable impact.

Do not merge compatibility with transition/migration: transition describes change over time; compatibility describes simultaneous or cross-version interaction properties.

### Maintainability

- `quality.maintainability.modularity`
- `quality.maintainability.reusability`
- `quality.maintainability.analysability`
- `quality.maintainability.modifiability`
- `quality.maintainability.testability`

Implementation principles such as SOLID/Clean Architecture can be evidence or design mechanisms for these qualities, but are not themselves quality attributes.

### Flexibility

- `quality.flexibility.adaptability`
- `quality.flexibility.scalability`
- `quality.flexibility.installability`
- `quality.flexibility.replaceability`

Portability is best represented through these more specific leaves rather than one ambiguous `portability` flag.

## Explicit overlap rules

### Security

`security.*` owns state.

Quality renders a Security subsection by reference. It never stores `quality.security = COVERED`.

Security standards/lenses such as STRIDE, ASVS, SSDF, SAMM and NIST CSF map to these concerns but do not create duplicate project states.

### Reliability

`reliability.*` owns failure semantics, availability, fault tolerance, recovery, consistency, retry/idempotency, durability and dependency-failure behavior.

Quality renders Reliability from that subtree.

SRE SLI/SLO/error-budget practice links:
- latency/throughput -> performance leaves;
- availability -> reliability.availability;
- measurement -> operability.metrics;
- alerts/operations -> operability.alerting/incident.

This prevents `observability` from being mislabeled as a reliability attribute.

### Human Interface, usability and accessibility

`interface.human.*` owns user interaction, usability and accessibility.

Quality references those leaves under interaction capability.

WCAG success criteria can become requirement/verification mappings for `interface.human.accessibility`; WCAG itself does not require a parallel quality state.

### Operability and observability

Operability is an engineering/operations concern, not a generic quality characteristic.

- logs -> `operability.logging`
- metrics -> `operability.metrics`
- traces/correlation -> `operability.tracing`
- health/readiness -> `operability.health`
- alerts -> `operability.alerting`
- diagnosis/response -> `operability.incident`

OpenTelemetry is a signal/instrumentation lens over logging/metrics/tracing, not a proof that observability is covered.

### Data quality

`data.quality` owns correctness/completeness/validity/known-vs-unknown semantics of project data/evidence.

It is not automatically part of product-quality aggregation unless the product's quality requirements explicitly depend on data quality. The quality dashboard may show it as a related concern.

### Reproducibility

Separate:
- `data.reproducibility` — same accepted source/evidence transformation can reproduce derived data/results;
- `delivery.reproducible-build` — build reproducibility;
- `delivery.provenance` — verifiable build/artifact origin.

SLSA provenance is not equivalent to reproducible builds.

## What COVERED means for Quality

Quality is derived, never persisted.

`Quality = COVERED` only when every **applicable activated quality-lens leaf** is COVERED and all other activated leaves are explicitly NOT_APPLICABLE.

Examples:

- An unassessed resource-efficiency leaf makes Quality PARTIAL even if security and reliability are covered.
- An explicit decision that no numeric latency target is required may make the latency-target leaf NOT_APPLICABLE for that scope; silence cannot.
- A formal WCAG conformance claim is not necessary to cover a narrower accepted accessibility baseline. The map must show the scope/evidence so readers do not infer a stronger claim.

## Quality scenarios

Quality attributes should be grounded in scenario-shaped requirements when material:

- context;
- stimulus/change/failure;
- affected system element;
- expected response;
- measurable or otherwise testable response criterion.

This is compatible with arc42's quality-scenario approach without turning every quality leaf into a mandatory document.

## Pilot implication

### NAPMS

The existing `quality.attributes = COVERED` should disappear as semantic truth.

The quality lens is mixed:
- latency/throughput/capacity/scalability targets: explicit NOT_APPLICABLE for first MVP;
- resource efficiency: UNASSESSED;
- maintainability: mostly covered;
- reliability: strong consistency/failure semantics but recovery UNASSESSED;
- security: strong architecture/threat coverage but lifecycle vulnerability-management/secure-development coverage UNASSESSED;
- human-interface quality: incomplete/unassessed because frontend design is not complete.

So the human dashboard should render Quality as PARTIAL.

### Nutrition

There is no dedicated quality artifact, but substantial quality knowledge exists:
- maintainability through architecture/component/engineering policy;
- testability through verification/test design;
- accessibility/usability baseline through frontend requirements/interface/verification;
- deterministic/provenance semantics through domain/data/verification.

Performance objectives, availability/recovery and several operability concerns remain UNASSESSED.

Therefore the old `quality.attributes = UNASSESSED` is also misleading: Quality should be PARTIAL with visible covered and unassessed branches.

## Recommendation

Keep ISO 25010/25019 as **taxonomy sources and comparison lenses**, not as the persisted Harness tree.

Canonical state should live in semantic concerns with one owner of coverage truth. Generated Quality documentation composes those states into an ISO-inspired view.
