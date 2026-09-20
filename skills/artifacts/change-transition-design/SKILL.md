---
name: change-transition-design
description: "Use when an accepted engineering state must change to another and the path has material coexistence, compatibility, ordering, irreversible, rollout, recovery or retirement semantics that must be decided before implementation."
---

# Change Transition Design

## Trigger

Use only when moving from accepted state A to accepted state B creates independently meaningful transition knowledge.

Typical triggers:
- old/new runtime versions can coexist;
- schema/data migration is executed separately from runtime replacement;
- external clients/producers/consumers upgrade independently;
- partially migrated state can be observed;
- progressive/canary/blue-green exposure has semantic gates;
- an irreversible point changes rollback/recovery options;
- compatibility shims need an explicit retirement condition.

Do not use for ordinary dependency updates or atomic replacement when endpoint design plus implementation mechanics fully determine a safe transition.

## Inputs

- accepted source-state capabilities/artifacts;
- accepted target-state capabilities/artifacts;
- Product/Domain/Application/System/Interface/Data/Quality constraints;
- applicable Security and Operability requirements;
- required availability/recovery expectations.

## Read boundary

Accepted endpoint design is authority. Existing scripts, pipeline YAML, framework migration behavior, deployed topology and legacy runbooks are not accepted transition semantics unless explicitly canonicalized.

Do not use production code to infer missing design decisions.

## Procedure

1. Identify source state A and target state B by accepted capabilities/artifacts.
2. Enumerate every intermediate/coexistence state reachable under the proposed change mechanism.
3. For each state verify preservation of accepted product/domain/application/system/interface/data/security/quality constraints.
4. Define directional compatibility obligations only where participants or representations coexist.
5. Define ordering constraints between schema/data/runtime/interface/release changes.
6. Identify irreversible points.
7. For each phase define permitted progression, halt and recovery actions.
8. Define rollout/release gates from accepted Verification/Operability/Quality evidence.
9. Define treatment of in-flight work and partially migrated authoritative state.
10. Define retirement conditions proving old readers/writers/contracts/representations are no longer required.
11. Route missing endpoint semantics as Questions to their owning Authorities. Never repair endpoint design inside this artifact.
12. Derive transition-specific Verification/Test and Operability obligations.
13. Leave concrete scripts, pipeline syntax and tooling to Implementation unless a higher-level policy makes them normative.

## Stop conditions

Create/route a blocking Question when implementation would otherwise decide:
- whether A and B may coexist;
- old/new schema read/write compatibility;
- producer/consumer version compatibility;
- authoritative meaning of partially migrated data;
- whether rollback is safe after B-state writes/effects;
- required roll-forward/restore/reconciliation behavior;
- in-flight work semantics at cutover;
- user-visible progressive-release behavior;
- progression/abort gate meaning;
- retirement/removal condition for compatibility mechanisms.

## Output contract

Produce the smallest project-native transition contract containing:
- source and target accepted states;
- applicability rationale;
- permitted intermediate/coexistence states;
- compatibility matrix/window;
- ordered transition constraints;
- irreversible points;
- progression gates;
- abort/rollback/roll-forward/restore/reconciliation rules as applicable;
- in-flight/partial-state rules;
- retirement conditions;
- blocking Questions;
- Verification/Test obligations;
- Operability evidence obligations;
- explicit implementation freedoms.

## Acceptance checks

- every reachable material intermediate state is either accepted or prohibited;
- compatibility is directional, scoped and time-bounded where possible;
- rollback is not assumed to be the inverse of deployment;
- irreversible points are explicit;
- endpoint semantics are referenced, not duplicated/re-owned;
- transition ordering is sufficient for implementation without pipeline defaults inventing semantics;
- gates are tied to accepted evidence;
- retirement conditions prevent permanent accidental compatibility burden;
- trivial changes can correctly classify this Authority as NOT_APPLICABLE.

## Registration

Register under CHANGE-TRANSITION-DESIGN only when the transition contract has independent value.

Do not create DEPLOYMENT-DESIGN, RELEASE-DESIGN, MIGRATION-DESIGN or COMPATIBILITY-DESIGN merely to split mechanisms from this boundary. Re-evaluate atomicity if future evidence demonstrates a genuinely independent public contract.
