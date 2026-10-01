# Agent Instruction and Skill Routing Scalability Plan

Status: active audit-branch migration plan.

## Accepted distribution decision

`docs/design/agent-skill-surfaces-and-consumer-distribution-v0.md` is the normative architecture for Maintainer vs Consumer skill surfaces and physical Consumer Pack materialization. This plan implements that decision; it must not invent a different distribution model.

## Progress

- Phase 1: explicit skill surface/type/lifecycle registry implemented; full PR workflow passed.
- Phase 2: public bootstrap ambiguity removed with Consumer Operation Registry; full PR workflow passed.
- Phase 4/5: Maintainer capture/change operations extracted from `AGENTS.md`; full PR workflow passed.
- Phase 3: deterministic concern-driven Consumer Method Router implemented; full PR workflow run 953 passed.
- Phase 7: inactive pre-Core procedures quarantined as non-executable legacy documentation; full PR workflow run 955 passed.
- Phase 6: Consumer Pack definition/binding/materializer is being implemented in the current checkpoint.

## Goal

Move Harness from prose-distributed agent instructions to one scalable ownership
chain:

```text
AGENTS.md -> router/registry -> task SKILL.md -> canonical policy/spec
```

README/overview docs remain human-facing projections.

## Audit baseline

AUD-005 found:

- **HARN-017:** no explicit routing/precedence contract for active agent skills;
  project bootstrap/reconcile has overlapping entry procedures.
- **HARN-018:** inactive pre-Core `SKILL.md` files remain exposed in executable
  form.
- **HARN-019:** eleven non-owning `judgement_only` procedures are classified but
  have no explicit invocation/router contract.
- task procedures are duplicated across `AGENTS.md`, workbench docs and skills;
- generic artifact mechanics are repeated across dozens of artifact skills.

## Constraints

- No Core semantic change just to reorganize instructions.
- Preserve deterministic `knowledge_kind -> artifact skill` routing.
- Do not mass-move files before routing ownership is stable.
- Keep always-on repository invariants available before skill selection.
- Skills execute procedures; canonical specs/policies own semantics.

## Phase 1 — Active skill type and surface registry

Before routing logic, represent every executable procedure with explicit `surface + route_class + lifecycle` metadata. Directory location is not sufficient type information.

1. Classify every executable skill with explicit `surface` (`maintainer` / `consumer`), `route_class` (`operation` / `method` / `artifact-production`) and lifecycle (`active` / deprecated / archived).
2. Record trigger class, exclusions and explicit composition/precedence for non-capability routes; preserve `knowledge_kind` for artifact-production routes.
3. Extend `validate_agent_layer.py` to require registry coverage.
4. Add positive, negative and overlap routing fixtures.

**Done when:** every active agent skill has one registered routing boundary and
ambiguous overlap fails validation.

## Phase 2 — Collapse bootstrap ambiguity

Prefer one public entry skill: `project-bootstrap-reconcile`.

Absorb/compose the useful behavior from `bootstrap-existing-project` so the
entry workflow handles:

```text
no realization        -> bootstrap minimal projection
compatible realization -> reuse/validate
outdated/unknown       -> reconcile conservatively
all cases              -> applicability/coverage diagnostics -> status
```

Retire `bootstrap-existing-project` as a separately routable skill after
coverage is preserved.

## Phase 3 — Non-owning analysis/method routing

Do not leave `judgement_only` skills as manually discoverable exceptions.

1. Define a route class for non-owning analysis/method procedures.
2. Route from explicit Coverage/Application findings or user intent, not from
   project `CapabilityId` ownership.
3. Move these procedures to a clearer namespace if the Method / Procedure
   Library experiment validates that boundary.
4. Extend validation so every active procedure is reachable through exactly one
   declared route class.

Do not assign fake `knowledge_kind` values to non-owning analyses just to make
the artifact router accept them.

**Done when:** all eleven current `judgement_only` skills are either explicitly
routable, promoted to a real capability provider, or retired.

## Phase 4 — Route audit/evolution capture through a skill

Create `skills/agent/capture-harness-observation/SKILL.md`.

Procedure:

1. read `docs/audit/README.md`;
2. search HARN/EVO ledgers;
3. classify defect vs evolution vs accepted decision;
4. reuse IDs by root cause/direction;
5. update/cross-link the correct owner.

Then reduce the detailed audit procedure in `AGENTS.md` to a bootstrap routing
rule.

## Phase 5 — Route Harness behavior changes through a skill

Create one active agent workflow for changing observable Harness behavior:

1. identify canonical contract;
2. reproduce consumer failure;
3. add/update Scenario Suite coverage;
4. implement;
5. run focused validators;
6. run aggregate gates.

Move Scenario Suite and Core-extension procedural text out of `AGENTS.md`.
Keep `core-v0.md` and `scenario-suite-v0.md` as contract owners.

## Phase 6 — Consumer Pack boundary and materialization

1. Define the smallest pinned Harness distribution identity for target repositories.
2. Define/build the Consumer Pack export boundary.
3. Materialize the exact pack locally before consumer routing.
4. Support an explicit local Harness checkout override for dogfooding without changing the pinned project identity.
5. Verify that maintainer-only and inactive skills are absent from Consumer discovery.

**Done when:** a clean consumer checkout can resolve one pinned Harness Consumer Pack locally and a fresh agent can enter the Consumer Registry without remote per-skill reads.

## Phase 7 — Quarantine inactive skills

For `skills/core/**`, `skills/ddd/**`, and
`skills/software-product/**`:

1. classify each as promote/archive/delete;
2. promote only with an active consumer;
3. move historical material out of executable `SKILL.md` form;
4. fail validation on unregistered active-looking skills.

## Phase 8 — Clarify documentation ownership

Refactor without semantic change:

- `AGENTS.md`: bootstrap + universal invariants;
- `README.md`: product overview and entry links;
- `agent-artifact-workbench-v0.md`: Application-layer concepts/invariants;
- `SKILL.md`: task procedure;
- canonical design/spec: normative semantics.

Prefer links over copied procedural paragraphs.

## Phase 9 — Pilot common artifact-production procedure

Do not deduplicate all artifact skills at once.

Pilot `product-requirements`, `domain-model`, and
`verification-strategy`:

1. extract only genuinely generic candidate/admission/registration/projection
   mechanics;
2. keep domain judgement and stop conditions local;
3. load the common procedure progressively;
4. compare context size, duplication and behavioral quality.

Reject the abstraction if it merely moves complexity.

## Phase 10 — Review remaining conditional global policies

For large root instruction blocks such as provider-backed LLM execution policy,
apply:

```text
needed before routing?      -> minimal AGENTS invariant
task-specific procedure?    -> skill
Harness policy/semantics?   -> canonical policy/spec
```

## Phase 11 — Fresh-context verification

Add behavioral/routing fixtures for at least:

1. project with no Harness realization;
2. outdated realization;
3. "record this defect";
4. "save this improvement idea";
5. observable Harness behavior change;
6. artifact CREATE routed by `knowledge_kind`.

## Definition of done

- no task workflow is independently maintained in both `AGENTS.md` and an
  active skill;
- every active agent skill is registered and routing-tested;
- artifact skills remain deterministically routed;
- no inactive historical `SKILL.md` looks active;
- skills reference canonical policies instead of copying them as new owners;
- a fresh agent can select the correct procedure from repository state alone;
- README/workbench are not needed to resolve workflow precedence.

## Order

Implement Phases 1-7 first because they establish the accepted routing/distribution boundary and remove demonstrated discovery defects. Phases 8-11 are scalability cleanup and should follow after the active routing surface is stable.
