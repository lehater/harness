# Consumer Contract v0

## Status

Consumer Contract v0 is an application layer over Harness Core v0. It is not a Core extension.

Its purpose is to answer one downstream question:

> Which canonical capabilities and representations must be available so this consumer can perform its responsibility without deciding semantics owned elsewhere?

## Responsibility

A consumer contract:

- names the capabilities a downstream consumer requires;
- states the Authority expected to own each capability;
- declares the representation the consumer needs;
- allows explicit `NOT_APPLICABLE` only through canonical evidence;
- detects missing knowledge as `DESIGN_GAP`;
- includes unresolved Core Questions that block selected providers;
- projects a satisfied contract into a source/representation plan.

It does not define workflow stages, roles, approvals, readiness levels or architectural quality scores.

## Inputs

The evaluator receives two inputs.

First, an ordinary valid Core v0 model:

- `Authority`;
- `CanonicalArtifact`;
- `CapabilityId`;
- `Question`;
- dependencies.

Second, a consumer-specific contract:

```yaml
id: IMPLEMENTATION-CONSUMER
consumer: implementation
requirements:
  - id: http-contract
    capability: example.http-contract
    expected_authority: ARCHITECTURE
    representation:
      standard: OpenAPI
      format: yaml

  - id: async-contract
    capability: example.async-contract
    expected_authority: ARCHITECTURE
    representation:
      standard: AsyncAPI
      format: yaml
    not_applicable:
      evidence_capability: example.async.not-applicable
```

`representation` is opaque metadata. Harness does not infer whether C4, UML, OpenAPI, Markdown or another format is semantically appropriate.

## Evaluation

For each requirement:

1. resolve the required `CapabilityId` through Core;
2. verify that its Core owner equals `expected_authority`;
3. collect unresolved Core Questions blocking any provider;
4. if the capability is absent and `not_applicable` is declared, resolve its evidence capability and verify the same ownership;
5. otherwise emit `DESIGN_GAP`.

The result status is:

- `PROVIDED` — canonical providers exist;
- `NOT_APPLICABLE` — the requested capability is absent, but canonical evidence for non-applicability exists;
- `DESIGN_GAP` — neither the required capability nor acceptable non-applicability evidence exists.

A contract is satisfied only when every requirement is `PROVIDED` or `NOT_APPLICABLE` and none of the selected providers is blocked by an unresolved Question.

## Question routing

For a `DESIGN_GAP`, the evaluator emits a Core-compatible Question draft with:

- a deterministic suggested ID;
- the `expected_authority`;
- text describing the missing capability.

This draft is routing metadata, not the answer.

The target project may persist the Question in its Core model. Resolution still follows normal Core semantics: the addressed Authority changes one of its canonical artifacts, the Question references that artifact as its resolution, and the consumer contract is evaluated again.

## Package projection

`project_package` accepts only a satisfied contract.

Its output contains, per requirement:

- status;
- canonical source artifact IDs;
- canonical source paths;
- the consumer-requested representation.

The projection is a build plan, not a generated Developer Package. Rendering, exact copying and format-specific validation remain consumer/project-specific until another acceptance case proves a reusable mechanism.

Generated package content must never become a second owner of product/domain/architecture semantics.

## Place in the chain

The dependency direction is:

```text
target canonical truth
        ↓
Harness Core v0
        ↓
Consumer Contract v0
        ↓
package projection plan
        ↓
consumer-specific materializer, if one is justified
```

A missing downstream requirement routes a Question back to the owning Authority. Canonical repair then propagates forward through normal Core dependency/capability resolution.

## Pilot 3 evidence

The executable case `spec/consumer-acceptance/napms-architecture-to-implementation.yaml` is based on the NAPMS Architecture → Implementation handoff problem.

It covers:

- multiple canonical providers for one domain capability;
- required runtime, deployment, persistence, HTTP, security, quality and verification knowledge;
- explicit asynchronous-contract `NOT_APPLICABLE` evidence;
- a simulated regression where security knowledge disappears;
- `DESIGN_GAP` routing to the Architecture Authority;
- refusal to project a package while the contract is unsatisfied.

The result supports Hypothesis A: Core v0 stays unchanged.
