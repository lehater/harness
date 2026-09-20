# Deployment / release / migration / compatibility / change-transition boundary research

Status: research hypothesis. No Harness Core or canonical Authority change is made by this document.

## Research question

When an accepted system changes from version/state A to version/state B, which engineering decisions must exist before implementation, who owns them, and is the transition itself an atomic Authority boundary?

The study separates five often-conflated subjects:

- **target-state design** — what B must be;
- **compatibility** — which old/new participants, data and interfaces may coexist;
- **transition semantics** — which intermediate states are permitted while moving A -> B;
- **release/deployment control** — how exposure to B is staged, gated, halted or reverted;
- **migration mechanics** — concrete scripts, commands and implementation sequencing.

## External reference model

Established guidance is used as a coverage lens, not as Harness ontology.

Relevant recurring facts:
- rolling deployments intentionally create periods where old and new runtime revisions coexist;
- safe progressive exposure requires explicit health gates and a halt/recovery path;
- blue/green keeps old and new environments side by side until traffic transition is accepted;
- schema/application evolution can require backward compatibility across simultaneously active versions;
- rollback is not universally equivalent to deploying the old binary: irreversible data/state transitions can make backward execution unsafe.

These facts imply that "deployment" is not only a CI/CD implementation detail when mixed-version behavior, data transformation, externally visible exposure or irreversible state changes are material.

## Decision ownership map

| Decision | Semantic owner |
| --- | --- |
| Target product behavior after change | Product/Domain/Application according to semantics |
| New runtime/component topology | System Architecture |
| New external contract | Interface Design |
| New physical schema/storage representation | Data Design |
| Required availability/latency during change | Quality Design |
| Which old/new external contract versions must interoperate | Interface Design, constrained by Product |
| Which old/new runtime components may coexist | System Architecture |
| Which old/new persisted representations may coexist | Data Design |
| Meaning-preserving transformation of domain state | Domain/Application; Data owns physical realization |
| Intermediate business states visible during migration | Product/Domain/Application |
| Order constraints between schema/runtime/interface changes | owner of the dependency plus transition orchestration |
| Progressive exposure population/ring semantics when user-visible | Product/System Architecture |
| Deployment unit, traffic switch, rollout topology | System Architecture |
| Release health evidence/gates | Verification + Operability, constrained by Quality/Product |
| Roll-forward/rollback semantic safety | owners of changed state/contracts |
| Concrete migration script/tool/command | Implementation freedom after transition contract |
| CI/CD engine syntax | implementation/engineering tooling freedom unless project policy makes it normative |

## Key distinctions

### Target state is not transition state

A valid design for A and a valid design for B do not prove that every intermediate A/B mixture is valid.

Examples:
- old application + new schema;
- new application + old schema;
- old producer + new consumer;
- new producer + old consumer;
- two API versions simultaneously receiving traffic;
- partially migrated records;
- feature enabled for only part of the population.

If any such state can exist during the chosen rollout, its validity must be derivable before implementation.

### Rollback is not a universal inverse

Traffic can often be redirected to an old runtime, but durable writes performed under B may no longer be readable or semantically valid under A. Therefore rollback safety is a property of the accepted transition, not a generic deployment mechanism.

A transition must explicitly distinguish:
- reversible before exposure;
- reversible while mixed versions coexist;
- roll-forward-only after an irreversible point;
- recovery by restore/reconciliation rather than old-version execution.

### Compatibility is directional and scoped

"Backward compatible" is underspecified. Analysis must identify:
- producer version;
- consumer version;
- data/schema version;
- direction of compatibility;
- coexistence window;
- retirement condition.

Compatibility that is unnecessary because versions never coexist should be NOT_APPLICABLE rather than imposed as a universal rule.

### Release is not deployment

Deployment makes a version available in an environment. Release changes who/what is allowed to depend on or observe it. They can coincide, but feature flags, canaries and parallel environments demonstrate that they need not.

## Atomicity test — candidate CHANGE-TRANSITION-DESIGN Authority

### 1. Semantic cohesion — provisionally passes

There is a coherent decision class not owned by either endpoint: validity of the path from accepted state A to accepted state B.

Its invariant is:

> Every reachable intermediate state during an accepted change must preserve explicitly accepted product/domain/data/interface/architecture/quality constraints, or have an accepted bounded exception and recovery path.

This is narrower than "DevOps" and does not own target-state semantics.

### 2. Independent change — passes in non-trivial cases

The transition plan can change while A and B remain unchanged:
- rolling -> blue/green;
- one-step schema replacement -> expand/migrate/contract;
- global release -> progressive exposure;
- rollback-capable -> roll-forward-only after a migration point.

Therefore transition knowledge can have an independent lifecycle.

### 3. Public producer/consumer contract — provisionally passes

Implementation, Verification/Test, Operability and release automation can consume a stable transition contract containing:
- source and target accepted states/capabilities;
- permitted coexistence states;
- compatibility obligations;
- transition ordering;
- irreversible points;
- gates;
- abort/recovery semantics;
- retirement conditions.

This contract can remain stable while scripts, pipeline syntax and deployment tooling change.

### Provisional verdict

A conditional **CHANGE-TRANSITION-DESIGN** Authority is plausible and materially different from IMPLEMENTATION-DESIGN.

However, canonicalization is premature until validated against at least:
1. a local single-process/schema migration;
2. a long-running HTTP service with database evolution;
3. a synthetic mixed-version/distributed rollout.

The candidate must be rejected if those cases show that the contract is only a convenient aggregation of Data/System/Interface decisions rather than independently accepted knowledge.

## Pre-code blocking Questions

Implementation must not invent answers when an applicable change leaves any of these unresolved:

- Can A and B execute concurrently?
- Can old code read/write the new physical schema?
- Can new code read/write the old schema?
- Which producer/consumer interface versions interoperate?
- Can partially migrated data be observed?
- What is the authoritative state while migration is incomplete?
- What is the irreversible point?
- Is rollback semantically safe after writes under B?
- If rollback is unsafe, what roll-forward/recovery path is accepted?
- What gates permit expansion to the next rollout population?
- What evidence stops the rollout?
- What happens to in-flight work across cutover?
- When may compatibility shims/old fields/old endpoints be removed?
- What condition proves the old state is no longer reachable?

## Implementation freedoms

After the transition contract is accepted, implementation may choose details that cannot alter it, including:
- migration framework;
- script/module decomposition;
- CI/CD product;
- pipeline YAML structure;
- exact batch size inside accepted capacity/latency constraints;
- temporary table/index names;
- deployment command syntax;
- internal feature-flag SDK.

## Validation case 1 — Nutrition Management

Nutrition is a useful negative/minimal case: local CLI + SQLite means no rolling fleet or cross-service mixed-version window is inherently required.

Pressure points still exist:
- physical schema migration can transform durable user data;
- old and new application versions need not be simultaneously supported unless the selected upgrade procedure requires it;
- rollback after a destructive schema/data migration is not automatically safe;
- a migration can require backup/restore or roll-forward semantics even in a single-process application.

Expected routing:
- meaning of preserved domain data -> Domain/Application;
- target schema and physical transformation constraints -> Data Design;
- whether upgrade must preserve availability -> Product/Quality;
- concrete SQLite migration mechanics -> Implementation;
- transition ordering/reversibility/retirement contract -> candidate Change Transition boundary if independently useful.

Accepted Nutrition evidence sharpens the case:

- Data Design requires forward schema changes to preserve accepted provider semantics and requires upstream reopening when a schema change changes domain meaning, ownership or planning consistency.
- ADR-010 permits ordinary dependency upgrades only when tests prove compatibility and accepted architecture/domain semantics remain unchanged.
- Neither artifact requires old/new application coexistence, rolling deployment, zero-downtime migration or arbitrary downgrade support.

Result:

- CHANGE-TRANSITION-DESIGN is **NOT_APPLICABLE by default** to ordinary dependency maintenance and trivial forward migrations whose transition has no independently meaningful intermediate state.
- It becomes applicable when a proposed change introduces a material coexistence window, irreversible data transformation, user-visible migration state, availability constraint, or recovery/retirement decision not derivable from the endpoint designs.
- This is positive evidence for a *conditional* Authority: absence is legitimate and must not force transition bureaucracy onto a local application.

The case also shows why the candidate cannot own target persistence semantics: Data Design already owns preservation of provider meaning. The residual transition contract only exists when moving between two accepted representations creates additional states/ordering/recovery knowledge.

## Validation case 2 — NAPMS

NAPMS is a stronger positive case because a long-running HTTP application with PostgreSQL can have separate runtime and schema change lifecycles.

Legacy repository material mentions a supported forward-upgrade procedure and explicitly does not claim arbitrary application/database downgrade compatibility. That material is not accepted current design evidence, but it is useful as a discovery signal: upgrade semantics can be independently important and cannot be replaced by a generic "rollback" assumption.

The accepted current design must be checked for:
- mixed old/new application instances during deployment;
- database schema compatibility window;
- API/client compatibility during rollout;
- in-flight protected mutations at cutover;
- irreversible migrations;
- restore/roll-forward behavior;
- release health gates.

Accepted NAPMS evidence provides a stronger boundary test:

- current System Architecture says schema migrations are one backend deployment concern while preserving module ownership;
- current persistence design owns module schema/repository boundaries and migration organization;
- current accepted material does **not** establish arbitrary old/new runtime coexistence, downgrade compatibility, progressive release, or rollback safety;
- the source ledger classifies the legacy local upgrade procedure as downstream S4/operations evidence rather than current domain truth.

Therefore current NAPMS does not authorize inventing rolling/blue-green/rollback semantics. For the present implementation slice, migration organization can remain System/Data/Implementation knowledge.

But the legacy upgrade evidence demonstrates a historically real consumer contract: forward-upgrade ordering and recovery can be independently documented while endpoint architecture remains stable. It is discovery evidence, not authority for current semantics.

Result:

- do not manufacture a CHANGE-TRANSITION-DESIGN instance for the current NAPMS slice unless the selected deployment/upgrade scope makes transition states material;
- if NAPMS adopts mixed runtime versions, independently executed schema migration, zero-downtime upgrade, progressive release or a non-trivial recovery boundary, existing endpoint Authorities are insufficient by themselves to own the **path validity**;
- at that point the transition contract is independently consumed by Implementation, Verification, Operability and deployment automation.

Missing answers must be routed as Questions rather than inferred from Docker/PostgreSQL/framework behavior.

## Validation case 3 — synthetic mixed-version rollout

Assume:
- v1 API writes records with schema S1;
- v2 introduces a new required representation S2 and new behavior;
- rolling deployment creates v1+v2 coexistence;
- database migration is executed separately;
- external clients do not upgrade atomically;
- v2 writes may be irreversible for v1.

A safe path cannot be derived solely from the endpoint designs.

A possible transition shape is:
1. expand storage/interface so v1 and v2 can coexist;
2. deploy code that tolerates both representations;
3. migrate/backfill authoritative data;
4. verify convergence and health;
5. release v2 behavior progressively;
6. stop old writes;
7. prove old readers/writers are absent;
8. contract obsolete representation.

The exact sequence is not canonical. What matters is that the selected sequence has an independently reviewable contract for coexistence, gates, irreversible points and retirement.

Failure experiments:
- v2 deployed before S2 compatibility exists -> transition invalid although v2 target design is valid;
- rollback to v1 after v2-only writes -> runtime rollback may violate data semantics;
- old client sends v1 contract after server contraction -> interface retirement occurred before its accepted condition;
- backfill partially completes -> authoritative mixed-state semantics must be defined;
- health gate fails during 10% exposure -> rollout must halt/recover according to accepted transition policy;
- pipeline retries a non-idempotent migration -> migration execution semantics must be accepted, not defaulted.

This fixture strongly supports an independent transition contract.

## Atomicity resolution after project validation

The two real projects and the synthetic fixture distinguish applicability from atomicity.

### Semantic cohesion — PASS

The residual knowledge is exactly path validity between accepted engineering states: coexistence, ordered transition constraints, irreversible points, gates, recovery and retirement.

It does not own either endpoint.

### Independent change — PASS

Nutrition can change migration mechanism without creating a transition Authority when no material transition state exists. Conversely, the synthetic case can change rolling to blue/green or alter migration/release ordering while endpoint A and B remain unchanged.

This demonstrates a lifecycle independent from endpoint design and from concrete implementation mechanics.

### Public producer/consumer contract — PASS

When applicable, the contract has concrete consumers:
- IMPLEMENTATION-DESIGN consumes permitted ordering and irreversible boundaries;
- VERIFICATION/TEST consumes transition-state and gate oracles;
- OPERABILITY consumes evidence required to decide progression/recovery;
- deployment/release automation consumes gates and allowed actions;
- endpoint Authorities consume routed Questions when a transition reveals missing compatibility semantics.

The contract remains meaningful if the CI/CD product, migration framework or scripts change.

### Final research verdict

**Create a conditional CHANGE-TRANSITION-DESIGN Authority.**

Do not create separate DEPLOYMENT-DESIGN, RELEASE-DESIGN, MIGRATION-DESIGN or COMPATIBILITY-DESIGN Authorities from this evidence. Those names describe mechanisms or subconcerns of one transition-validity boundary, while their endpoint semantics remain with Product/Domain/Application/System/Interface/Data/Quality.

Applicability rule:

> Instantiate CHANGE-TRANSITION-DESIGN only when moving between accepted engineering states introduces material intermediate/coexistence states, ordering constraints, irreversible points, rollout gates, recovery choices or retirement conditions that are not fully derivable from the endpoint designs.

For a trivial atomic replacement with no material intermediate state, it is NOT_APPLICABLE.

## Current conclusion

Unlike Reliability, Change/Transition currently shows a plausible residual atomic boundary after existing owners keep their native semantics.

Candidate responsibility:

> Own the validity of transitions between accepted engineering states: permitted coexistence, compatibility window, ordering, irreversible points, gates, abort/recovery path and retirement conditions, without re-owning either source-state or target-state semantics.

Candidate inputs:
- accepted source-state capabilities/artifacts;
- accepted target-state capabilities/artifacts;
- Data/System/Interface/Application/Product/Quality constraints;
- release/availability expectations.

Candidate outputs:
- permitted transition states;
- compatibility matrix/window;
- ordered constraints/dependencies;
- irreversible points;
- rollout/release gates;
- abort/rollback/roll-forward/recovery contract;
- retirement conditions;
- Questions routed to endpoint semantic owners;
- verification and operability obligations.

## Priority findings

### P0

1. Endpoint design completeness does not imply transition completeness.
2. Rollback must never be assumed safe after durable or externally visible B-state effects.
3. Mixed-version states need explicit applicability and validity.
4. Project validation and the mixed-version fixture satisfy the atomicity test for a conditional CHANGE-TRANSITION-DESIGN Authority.

### P1

1. Release/deployment mechanics should not become an Authority by themselves.
2. Compatibility is a property of a concrete coexistence relation, not a universal requirement.
3. Implementation Design should consume an accepted transition contract when one is applicable rather than invent migration order.
4. Verification and Operability need transition-specific gates/evidence but do not own transition semantics.

## Next research step

Canonicalize the conditional CHANGE-TRANSITION-DESIGN Authority and its reusable artifact skill in this research branch. Then run repository checks before considering merge. After that, continue to the next uncovered P0/P1 engineering area rather than expanding transition mechanics further.
