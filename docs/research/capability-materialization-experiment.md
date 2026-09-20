# Capability materialization experiment

Status: research only. No Core or canonical contract change is proposed.

## Question

Does Harness need a new representation abstraction, or are the existing concepts
Authority + production contract + CapabilityId + CanonicalArtifact + artifact skill
already sufficient when exercised against real repositories?

The experiment treats CapabilityId, not document type or knowledge_kind, as the
unit exposed to downstream consumers.

## Existing model under test

```text
Authority
  -> production contract
       -> CapabilityId
            -> accepted CanonicalArtifact provider

knowledge_kind (optional)
  -> routes CREATE work to an artifact skill
       -> output contract/schema
       -> structural validation
       -> semantic acceptance
       -> Core registration
```

A representation concern is a failure only if a consumer can resolve a CapabilityId
to an accepted provider but still cannot consume the knowledge promised by that
capability without unsupported semantic inference.

## Pilot A — Nutrition Management

Nutrition deliberately contains both weakly structured project-native Markdown and
Harness-managed typed YAML.

Observed samples:

| Capability | Provider shape | Existing production/acceptance contract | Observation |
| --- | --- | --- | --- |
| `nutrition-management.requirements` | project-native Markdown | Product Requirements skill defines required semantic content and acceptance checks | Human/agent consumption is supported; no deterministic field-level machine contract is promised. |
| `nutrition-management.architecture` | project-native Markdown | System Architecture skill defines required architecture knowledge and semantic acceptance | Sufficient for implementation-agent consumption, but not sufficient for deterministic C4 extraction. That extraction is not part of the capability contract. |
| `nutrition-management.component-design` | project-native Markdown | Component Design skill defines implementation-facing obligations and acceptance checks | The capability promises implementation-facing design, not a particular serialization. |
| `nutrition-management.redesign.verification-design` / verification strategy | typed Harness YAML where selected | Verification Strategy skill + `verification-plan/v1` validator | Deterministic structure is required because the selected representation contract promises it. |
| BLS source/classification capabilities | project-native data artifacts | specialized artifact skills + project validation | Machine structure is justified by the downstream data-processing consumer, not by canonicality alone. |

### Attempted falsification

Hypothesis tested: every canonical Capability must have a universal machine schema.

Result: falsified by current valid Nutrition consumers. Requirements, architecture
and component design are consumed by engineering agents from accepted project-native
artifacts without a universal Harness schema. Requiring a schema would add a second
representation without a demonstrated consumer failure.

Hypothesis tested: arbitrary canonical prose can support any deterministic projection.

Result: falsified. Nutrition architecture prose cannot deterministically produce a
C4 model without adding classification/containment semantics. The correct outcome is
that the proposed deterministic projection is unsupported by the current capability,
not that the existing architecture capability is invalid.

## Pilot B — NAPMS

NAPMS uses more machine-structured canonical representations.

Observed samples:

| Capability | Provider shape | Existing contract | Observation |
| --- | --- | --- | --- |
| `engineering.architecture.c4-model` | Structurizr DSL | project-native canonical graph + Structurizr syntax/model | Deterministic C4 consumers are supported naturally. |
| `engineering.interface.http-contract` | OpenAPI YAML | OpenAPI contract | Standard notation already is the representation contract; a Harness schema would duplicate it. |
| tactical/strategic domain capabilities | typed project YAML | project-owned artifact semantics and validators/generators | Deterministic projections can consume them without prose inference. |
| `engineering.verification.strategy` | typed project YAML | test-intent contract | Structured form exists because downstream traceability/verification needs it. |

NAPMS independently contains an artifact-type registry with canonical representation
rules, format families and validator requirements. This is evidence that representation
constraints can be useful, but it is project documentation-system policy, not evidence
that Core requires another entity.

## Cross-pilot result

The pilots separate four concepts that must not be collapsed:

1. **Authority atomicity** — who owns a coherent independently-changing decision boundary.
2. **Capability contract** — what accepted knowledge downstream may rely on.
3. **Materialization contract** — what an artifact must contain/prove before it may claim that CapabilityId.
4. **Serialization/representation** — how that accepted materialization is encoded.

The active Harness artifact skills already carry most of (3): read boundary,
procedure, output contract/schema, acceptance checks and registration. A typed schema
is one possible output contract, not the definition of canonical knowledge.

## Current hypothesis after falsification

Do **not** introduce a universal Representation Contract entity yet.

The narrower hypothesis is:

> A production Capability needs a sufficiently explicit **materialization contract**
> at the agent/skill boundary. That contract states what semantic content must be
> present and what structural validation is required before a CanonicalArtifact may
> register `provides: CapabilityId`. Representation is one property of that contract.

For stable reusable shapes, the materialization contract may select a Harness schema.
For standard-native contracts it may select OpenAPI, Structurizr, JSON Schema, etc.
For agent-consumed narrative knowledge it may define semantic acceptance checks over
project-native Markdown. For project-native typed data it may delegate to a
deterministic project validator.

This preserves the Core invariant: Core does not interpret arbitrary semantics.

## Consumer-failure criterion for a future extension

A new first-class Harness representation/materialization entity is justified only if
a real consumer demonstrates all of the following:

1. Core successfully resolves the required CapabilityId to an accepted provider.
2. The provider passed the artifact skill's current output and semantic acceptance.
3. The consumer legitimately requires a stronger deterministic interface than the
   capability currently exposes.
4. That requirement cannot be expressed by refining the CapabilityId/production
   contract or the artifact skill without duplicating canonical truth.
5. The same failure recurs across materially different projects.

Neither pilot currently demonstrates all five conditions.

## Findings

- **P0:** none.
- **P1:** the earlier phrase “canonical knowledge in arbitrary/project-native format”
  is too broad. The format is constrained by the capability's materialization needs
  and artifact-skill output contract.
- **P1:** `knowledge_kind` is routing metadata, not the canonical knowledge atom and
  should not become a storage taxonomy.
- **P2:** artifact skills express materialization contracts mostly as prose. This is
  an ergonomics/machine-discoverability limitation, but no current pilot proves that
  Core needs to model it.
- **P2:** deterministic projections must declare stronger input requirements and fail
  on unsupported provider representations rather than infer missing semantics.
- **P3:** NAPMS's artifact-type registry is useful prior art for a possible future
  machine-readable skill/output-contract registry, but promotion requires a consumer
  failure in Harness itself.

## Decision for this research stage

Keep Core, Engineering Graph and main unchanged.

Continue experiments at the artifact-skill/consumer boundary. The next useful test is
to implement a consumer that requests a deterministic projection from the same
semantic capability in both pilots and observe whether skill/output-contract metadata
is enough to select/reject providers without adding a new Core concept.
