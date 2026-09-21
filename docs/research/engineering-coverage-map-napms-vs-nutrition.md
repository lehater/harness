# Engineering Coverage Map — NAPMS vs Nutrition prototype

Status: research comparison.

This comparison uses the same baseline concern IDs for both projects.
It is intentionally conservative: if the research did not find accepted applicability evidence, the state is UNASSESSED rather than guessed NOT_APPLICABLE.

| Concern | NAPMS | Nutrition Management | Observation |
|---|---|---|---|
| problem.discovery | COVERED | COVERED | Both have accepted problem/product framing. |
| product.intent | COVERED | COVERED | Different artifacts, same concern. |
| domain.semantics | COVERED | COVERED | Both are domain-rich but use different Authority structures. |
| application.use-cases | COVERED | COVERED | NAPMS journey/use-case vs Nutrition application/user journeys. |
| architecture.structure | COVERED | COVERED | NAPMS includes canonical Structurizr C4; Nutrition uses accepted target/frontend architecture artifacts. |
| interface.machine | COVERED | COVERED | NAPMS HTTP/OpenAPI; Nutrition CLI + frontend application contracts. |
| interface.human | MISSING | COVERED | NAPMS has narrow UI artifacts but full frontend Human Interface capability is still missing. |
| data.persistence | COVERED | COVERED | Both have accepted persistence/data design. |
| security.architecture | COVERED | COVERED | NAPMS broad OIDC/admission boundary; Nutrition current accepted boundary is local-browser-specific. |
| security.analysis | COVERED | UNASSESSED | NAPMS has threat model; Nutrition has no equivalent accepted analysis in current graph. |
| privacy.governance | UNASSESSED | UNASSESSED | Silence is visible rather than interpreted as N/A. |
| obligation.external | UNASSESSED | UNASSESSED | Existing obligation research predicts this is conditional. |
| quality.attributes | COVERED | UNASSESSED | NAPMS has explicit quality constraints; Nutrition does not expose an equivalent current capability. |
| reliability.concurrency | COVERED | UNASSESSED | NAPMS explicitly owns consistency/snapshot/failure semantics. |
| operability.observability | COVERED | UNASSESSED | NAPMS has observability requirements; Nutrition does not expose them as accepted current knowledge. |
| engineering.policy | UNASSESSED | COVERED | Nutrition explicitly owns Engineering Policy; NAPMS first-MVP graph currently does not. |
| dependencies.supply-chain | UNASSESSED | UNASSESSED | Candidate for future applicability analysis, not automatic N/A. |
| build.reproducibility | UNASSESSED | UNASSESSED | Same. |
| component.design | MISSING | COVERED | NAPMS backend has module contracts but no general Component Design capability; frontend Component Design is not yet materialized. |
| implementation.design | COVERED | COVERED | Both explicitly cover implementation realization. |
| verification.strategy | COVERED | COVERED | Both expose accepted verification knowledge. |
| test.design | MISSING | COVERED | NAPMS backend has test intent but reusable Test Design capability is only in the incomplete frontend path. |
| change.transition | UNASSESSED | UNASSESSED | Conditional lifecycle concern. |
| accessibility | UNASSESSED | UNASSESSED | Human-interface presence alone must not imply applicability decision. |
| internationalization | UNASSESSED | UNASSESSED | Must be consciously assessed when locale/time presentation matters. |
| safety | UNASSESSED | UNASSESSED | Specialized concern; no inference from silence. |
| ai.risk | UNASSESSED | UNASSESSED | Specialized concern; no inference from absence of AI-specific files. |

## What the comparison proves

### Same rows do not require same artifacts

The concern catalog gives comparability while project-native models remain different.

Examples:
- architecture.structure can point to Structurizr DSL in NAPMS and Markdown/design artifacts in Nutrition;
- interface.machine can be HTTP/OpenAPI or CLI/application contracts;
- security.architecture can describe very different trust boundaries.

### UNASSESSED is high-value information

Many rows are not actually known to be NOT_APPLICABLE.

This is exactly the blind spot a normal file tree hides.

An empty privacy/accessibility/build row means:
> this concern has not yet been accepted as applicable or non-applicable.

That is much more useful than silently showing no file.

### Missing vs absent-file distinction

NAPMS demonstrates why a map cannot just scan paths.

Human-interface and Test Design are MISSING because the Engineering Graph says those capabilities are required for FRONTEND-IMPLEMENTATION and they do not yet have accepted providers.

The status comes from project semantics, not from guessing based on filenames.

### One concern may span several artifacts

Domain, architecture, security and verification all map many-to-many.

Therefore one concern != one document.

The dashboard should link to all relevant evidence and optionally to a generated Human Documentation section.

## Derived-vs-explicit target

The prototype maps are still mostly hand-authored research data.

The desired implementation should derive most fields:

Automatically derivable:
- Capability provider and Authority;
- provider CanonicalArtifact/path;
- Consumer target state;
- missing/create/wait;
- unresolved Questions;
- project graph dependencies;
- visual projections;
- lifecycle stale/current when supported.

Project-owned explicit input may remain necessary for:
- concern -> Capability mapping when not implied by knowledge_kind;
- applicability rationale;
- NOT_APPLICABLE evidence;
- DEFERRED rationale/reopening condition;
- concern specialization modules.

A key prototype metric should be the ratio of derived to manually duplicated data.

## Proposed UI symbols

Suggested Markdown presentation:

- ✓ COVERED
- ✕ MISSING
- ⧖ BLOCKED
- ↻ STALE
- — NOT_APPLICABLE
- ◷ DEFERRED
- ? UNASSESSED

These are presentation symbols only.

## Recommended generated navigation

The map can be rendered in three complementary views.

### By concern

```
Security
├── Architecture            ✓
│   └── mvp-security-architecture.yaml
├── Threat analysis         ✓
│   └── mvp-threat-model.yaml
└── Privacy/governance      ?
```

### By artifact

```
mvp-security-architecture.yaml
├── concern: security.architecture
├── capabilities: engineering.architecture.security
├── produced by: SECURITY-ARCHITECTURE-DESIGN
├── required by: Interface / Quality / Security Analysis / Operability / Implementation
└── freshness: CURRENT
```

### By project status

```
Missing
  - interface.human
  - component.design
  - test.design

Unassessed
  - privacy.governance
  - accessibility
  - build.reproducibility
  ...
```

This makes the map both a dashboard and a documentation index.

## Next experiment

Add a tiny ETL/script fixture.

The hypothesis to test:
- the same baseline catalog remains usable;
- many concerns are explicitly NOT_APPLICABLE or lightweight;
- operational/data/error/security concerns remain visible even for a small script;
- the map does not force architecture theater or dozens of meaningless artifacts.

If that works, the concern catalog is broad enough for cross-project comparison without becoming enterprise-only bureaucracy.
