# Capability Dependency Resolution — cross-authority obligation coverage v1

Date: 2026-10-08
Repository: `lehater/harness`
Experiment: `experiment/capability-dependency-resolution-v1` (draft PR #220)
Project snapshot: `lehater/prep@c52ff8ec1a4732285b2b299bf11dca9869fb2fee`
Status: **read-only protocol implemented; new real-provider run not yet executed**

## Why this work exists

The first real PREP oracle-free pilot discovered both Tactical Domain targets
from their Model Context Strategy headings only. It selected only
`prep.model-context-strategy` even though the accepted Engineering Graph also
contains `prep.product-capabilities` as a prerequisite. Omitting a provider
from a proposal with partial target obligations is **not** evidence that the
graph's direct dependency is unnecessary. The existing reconciler has already
blocked removal proposals under such incomplete coverage.

This revision improves target-context source coverage without assuming that
every accepted product behavior belongs inside a tactical domain model.

## Accepted source derivation

`evals.project_discovery_snapshot` checks out the pinned commit and verifies
clean tracked Git state. The actual Core, Engineering Graph and semantic
baseline identify the six accepted, reviewed Core Capability providers. It now
also uses project-specific **source selectors**, not hardcoded PREP text:

| Target | Accepted model scope | Accepted strategic scope |
| --- | --- | --- |
| `prep.preparation-information-model` | MC-01 | DS-01 |
| `prep.recorded-activity-history-model` | MC-02, TR-01 | DS-02 |

`docs/architecture/context-map.md` contains explicit `**Derived from:**`
references from strategic scopes to Product Capabilities requirement IDs.
The generator resolves these IDs against **only ACCEPTED** statements in the
Core-registered `.harness/knowledge/product-capabilities.yaml`, and checks
their exact public source references. It errors on missing accepted requirement
IDs, duplicate IDs, missing registered sources or invalid Git snapshot.

DS-01 explicitly traces four accepted Product Capability requirements:
`REQ-CAP-KNOWLEDGE-KINDS`,
`REQ-CAP-RELATIONSHIP-MEANINGS`,
`REQ-CAP-CROSS-INFORMATION-RELATIONSHIPS`,
`REQ-CAP-EXPLORE-PERSPECTIVES`.

DS-02 explicitly traces five accepted Product Capability requirements:
`REQ-CAP-RECORD-ACTIVITY`,
`REQ-CAP-RELATE-ACTIVITY`,
`REQ-CAP-PRESERVE-TIME`,
`REQ-CAP-PRESERVE-HISTORY-CONTEXT`,
`REQ-CAP-EXPLORE-HISTORY`.

All **15** accepted Product Capability requirements are inventoried for each
target, not just the 4 or 5 strategic references. The remaining 11 or 10 are
still candidates for semantic applicability review: they are not silently
excluded or assumed to be tactical domain obligations.

## Representation and proof limits

Each target receives:

- `output_obligations`: scoped accepted Model Context and strategic responsibility
  sections, with their source Capability, path and exact section heading;
- `upstream_constraint_candidates`: every accepted Product Capability
  requirement ID, statement, public claim index, provider, provenance as
  `EXPLICIT_STRATEGIC_DERIVATION` or
  `UNADJUDICATED_ACCEPTED_PRODUCT_REQUIREMENT`, and
  `applicability=REQUIRES_SEMANTIC_REVIEW`.

The Copilot prompt is instructed to classify **every** upstream requirement
as `DIRECT_CONSTRAINT`, `CONTEXT_ONLY` or `UNDECIDED`, with a rationale.
The adapter rejects missing, duplicate, unknown or malformed assessments.
The separate deterministic `evals.project_discovery_coverage` checker
validates complete candidate accounting and verifies that each claimed
`DIRECT_CONSTRAINT` is consistent with a proposed direct provider and an
exact cited public claim.

**This is completeness of source inventory and model response accounting,
NOT independently proven completeness of target obligations.** A model can
misclassify applicability, and an explicit Domain Strategy link shows accepted
strategic derivation, not automatically a direct tactical dependency.
`semantic_applicability_adjudicated=false` and
`complete_output_obligation_coverage_established=false` remain mandatory.

There is no acceptable project-snapshot-specific algorithm for treating
omitted existing accepted direct edges as unnecessary on these grounds.
The Phase B output still uses `UNASSESSED_EXISTING_EDGES` and
`REMOVE_CANDIDATE=[]`. All graph writeback is disabled.

## Assurance and next operation

The existing full CI suite includes a versioned synthetic Git-snapshot fixture,
explicit accepted strategic `Derived from` links, accepted and unaccepted
product requirements, and an accepted but untraced product candidate. Its
fake-provider Scenario Suite run returns exhaustive `coverage_assessments`;
incomplete Phase B coverage is deliberately rejected. The provider adapter
also has fail-closed tests for missing, duplicate and invalid candidate
assessments.

The disposable workflow branch `experiment/cdr-live-run` contains this
revision. A new **manually dispatched** GitHub Copilot run on that branch can
supply first actual evidence of product applicability classifications for
the two PREP Tactical Domain Capabilities, without exposing current
`requires` or a hand-authored oracle to the model.

Do not change PREP, enable agent routing, or merge this experimental work
until independent cross-authority review and project snapshot publication
consistency are established.
