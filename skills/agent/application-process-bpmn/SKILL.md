---
name: application-process-bpmn
description: "Generate one source-bounded BPMN 2.0 process projection from accepted Application Process semantics without promoting BPMN notation to canonical truth."
---

# Application Process BPMN Projection

Status: canonical v1 slice.

## Trigger

Use only when the public `human-documentation-projection` operation has a
compiled plan section whose `renderer` is `application-process-bpmn`, the
section has an explicit process `scope`, and the coordinator resolves this
internal operation through `harness.application.skill_router` with
`invoked_by=human-documentation-projection`.

## Inputs

- current Human Projection manifest;
- current Human Projection plan;
- exact document id and section id;
- explicit process `scope-id` from that section;
- exact CanonicalArtifacts listed in that section;
- `spec/projection/application-process-bpmn-v1.yaml`;
- target repository root.

The normal primary source is an accepted
`application-process-design` CanonicalArtifact. Upstream application/domain/
task/product artifacts may be read only when they are already selected by the
plan and are needed to preserve referenced meaning without re-owning it.

## Read boundary

Read only CanonicalArtifacts listed in the selected plan section's `sources`.
Resolve source paths from the current Human Projection manifest.

Do not search the repository for process knowledge and do not use:

- `docs/generated/**`;
- previous BPMN output;
- workflow-engine definitions;
- implementation orchestration;
- queue/broker configuration;
- runtime traces;

as semantic authority unless a non-generated file is itself one of the exact
CanonicalArtifacts selected by the plan.

## Procedure

1. Confirm manifest freshness when source digests are present.
2. Confirm `renderer: application-process-bpmn` and a non-empty process
   `scope`.
3. Load `spec/projection/application-process-bpmn-v1.yaml`.
4. Read only selected CanonicalArtifacts and identify the accepted Process v1
   semantics for this occurrence boundary:
   - entry/trigger role;
   - referenced participating work;
   - explicit composition/control constraints;
   - accepted completion outcomes;
   - explicit choice/exclusion;
   - explicit concurrency/synchronization.
5. Map only supported semantics:
   - bounded process -> one BPMN `process`;
   - accepted entry -> generic `startEvent`;
   - semantic activity -> generic `task`;
   - explicit human task -> `userTask`;
   - strict accepted control precedence -> `sequenceFlow`;
   - explicit choice/exclusion -> `exclusiveGateway`;
   - explicit concurrency/synchronization -> `parallelGateway`;
   - accepted completion outcome -> named `endEvent`.
6. Keep branch labels on every outgoing flow from a divergent exclusive
   gateway. The labels describe accepted guard/outcome meaning; do not invent
   executable expressions.
7. Do not infer:
   - `SYSTEM` activity -> `serviceTask`;
   - Domain Event -> message event;
   - external dependency -> message flow;
   - unordered work -> parallel gateway;
   - ordinary condition -> exclusive gateway;
   - retry -> loop marker;
   - recovery -> compensation;
   - transaction scope -> BPMN transaction;
   - owner/context -> pool or lane.
8. v1 intentionally does not encode material wait/continuation events,
   repetition, subprocess decomposition, compensation/recovery or executable
   workflow semantics. If any of those are required to faithfully represent the
   accepted Process Capability, stop this specialized projection and retain the
   process in narrative documentation until a later projection profile supports
   that semantic surface.
9. Emit one standalone BPMN 2.0 XML document with
   `isExecutable="false"`, no extensions and no BPMN DI requirement.
10. Write the BPMN to
    `docs/generated/process/<scope-id>/process.bpmn`.
11. Generate deterministic provenance:

   ```sh
   python -m harness.workspace.application_process_bpmn_projection provenance \
     --manifest <manifest.yaml> \
     --plan <plan.yaml> \
     --document <document-id> \
     --section <section-id> \
     --scope <scope-id> \
     --profile spec/projection/application-process-bpmn-v1.yaml \
     --output docs/generated/process/<scope-id>/process.bpmn.provenance.yaml
   ```

12. Validate the source/provenance binding and supported BPMN subset:

   ```sh
   python -m harness.workspace.application_process_bpmn_projection validate \
     --manifest <manifest.yaml> \
     --plan <plan.yaml> \
     --document <document-id> \
     --section <section-id> \
     --scope <scope-id> \
     --profile spec/projection/application-process-bpmn-v1.yaml \
     --bpmn docs/generated/process/<scope-id>/process.bpmn \
     --provenance docs/generated/process/<scope-id>/process.bpmn.provenance.yaml
   ```

## Stop conditions

Stop without generating BPMN when:

- selected sources do not contain accepted Process semantics for the requested
  scope;
- process boundary, participating work, composition or completion is ambiguous;
- a required element would need a source outside the plan;
- the source baseline is stale;
- material waits, repetition, subprocess composition or recovery/compensation
  cannot be represented by the v1 profile without losing accepted meaning;
- generating a valid diagram would require inventing control flow.

Projection failure is not itself a Core Question. A Question exists only when
the underlying canonical Process knowledge is genuinely unresolved.

## Output contract

For `scope-id = <scope-id>`:

- `docs/generated/process/<scope-id>/process.bpmn`;
- `docs/generated/process/<scope-id>/process.bpmn.provenance.yaml`.

Both are disposable projections. They provide no CapabilityId and are never a
source of engineering truth.

## Acceptance checks

- operation is routed only from `human-documentation-projection`;
- scope is identical across plan, invocation, output path and provenance;
- every BPMN node/flow is supported by selected canonical sources;
- generated inputs are rejected;
- BPMN contains exactly one non-executable process;
- service/message/runtime-specific constructs are absent;
- branching/merging semantics are explicit gateways, never implicit task fanout;
- exclusive branch labels are explicit;
- all flow nodes are reachable from the start and can reach an end;
- cycles are rejected in v1;
- provenance exactly matches current manifest/plan/profile;
- generated outputs remain under `docs/generated/**`.
