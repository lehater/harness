# Harness Assurance Registry Design v0

Status: canonical assurance design; initial machine-readable seed implemented.

## Purpose

Define the future machine-readable relationship between Harness abilities,
failure modes, evidence requirements, and executable/inspectable evidence.

This design exists so that:

- green validators cannot hide an ability with no assurance obligation;
- higher-level tests cannot silently substitute for a required lower-level
  mechanism proof;
- evidence strength/oracle provenance remains visible;
- CI inventory and Scenario Suite coverage remain evidence providers rather than
  becoming the denominator of correctness.

The human-readable semantic owner remains
`docs/design/harness-ability-to-evidence-v0.md`.

## Ownership

~~~text
Harness Assurance Policy
    owns evidence selection and promotion rules

Ability-to-Evidence Model
    owns ability/failure-mode semantics

Assurance Registry
    machine-readable projection of required assurance slots and evidence refs

Evidence providers
    validators / tests / scenarios / eval records

CI Policy
    owns execution scheduling, not assurance completeness
~~~

The registry must not become a second independent semantic owner for ability
definitions.

## Implemented initial seed

The reviewed minimum implementation is:

- `spec/assurance/harness-assurance-registry-v0.yaml` — machine-readable Ability -> requirement -> evidence seed;
- `validators/validate_assurance_registry.py` — structural validation, admissibility/completeness report, and AR-M01..AR-M11 meta-self-tests.

The seed is intentionally incomplete. It includes HA-A04 Authority formation,
HA-A05 Capability formation, HA-A09 existing-project bootstrap/reconcile,
HA-A16 routing, and HA-A19 assurance self-test obligations. HA-A05 remains split
into separate TL1 discovery/granularity, TL3 Reference-vocabulary/novel-
Capability, and TL4 clean-context convergence proof slots. HA-A09 now exposes
separate TL2 controlled handoff, TL3 existing-project micro-project, TL4
clean-context/metamorphic, and TL5 known-project proof slots.

Provider-backed run `36928079710` is preserved as durable historical evidence
in `spec/assurance/evidence/first-wave-provider-run-36928079710.yaml`; it
remains stale for the current Harness because root `AGENTS.md` changed after
that run.

Provider-backed run `36942421201` executed the refreshed ten first-wave
cases plus TD-COMP-001 against Harness revision
`c1a45a1a618fe11e2b2b28a5d3184d177beb5d71` and remains preserved in
`spec/assurance/evidence/first-wave-provider-run-36942421201.yaml`. It
established A04-R01, A05-R01, A09-R01, and A16-R01 for that bound execution
surface.

The shared behavioral runner/adapter was subsequently extended for the TL3
existing-project suite TD-BOOT-E01..E05. Because those files are behavior-
relevant execution bindings, run `36942421201` is now intentionally stale for
the current branch until the expanded suite is executed again. Deterministic
A16-R02..R04 evidence remains current; judgement slots A04-R01, A05-R01,
A09-R01 and A16-R01 temporarily return to missing. This is the expected
currentness behavior rather than a regression in the historical run.

Suite manifests are scheduling/inventory surfaces, not per-case semantic
bindings: selected evidence is already bound by explicit `case_ids` plus
case/fixture/oracle hashes. Adding another case to a suite therefore does not by
itself stale existing case evidence; shared provider/runtime semantics and the
trusted instructions actually used by selected cases do.

Registry validity remains separate from release-claim completeness and
`release_claim_ready` remains false.

## Core model

The registry needs three kinds of records:

1. `ability` — stable assurance identity and release relevance;
2. `requirement` — one evidence obligation for a failure mode or failure-mode
   family;
3. `evidence` — one concrete proof artifact satisfying zero or more
   requirements.

Do not model assurance as one scalar maturity score.

## Ability record

Conceptual shape:

~~~yaml
id: HA-A05
title: Capability discovery and granularity
contract_ref:
  path: docs/design/harness-ability-to-evidence-v0.md
release_critical: true
execution_nature: judgement-dependent
failure_modes:
  - A05-F01
  - A05-F02
  - ...
requirements:
  - A05-R01
  - A05-R02
~~~

Rules:

- `id` is stable and unique;
- `contract_ref` points to the canonical human-readable owner;
- `release_critical` is explicit, not inferred from test count;
- execution nature is descriptive metadata, not runtime behavior;
- every material failure mode maps to at least one requirement.

## Requirement record

A requirement represents a **proof slot**, not a test file.

Conceptual shape:

~~~yaml
id: A05-R01
ability: HA-A05
failure_modes: [A05-F01, A05-F02, A05-F03, A05-F04, A05-F05]
purpose: isolated synthetic discovery/granularity falsification
required:
  test_levels: [TL1]
  methods_any: [EM-02, EM-05]
  oracle_minimum: O1
  judgement_execution: true
substitution:
  higher_level_alone_allowed: false
status: required
~~~

A second requirement may separately demand TL4 repeated agent evidence.

This is essential: requirements are **explicit slots** rather than a numeric
"minimum TL". A TL6 holdout cannot satisfy a TL1 mechanism slot merely because
6 > 1.

### Required fields

Each requirement declares:

- ability;
- failure modes;
- purpose;
- required test level(s);
- acceptable method(s);
- minimum oracle class;
- whether deterministic or judgement execution is required;
- whether a higher-level proof may substitute;
- release applicability.

## Evidence record

Conceptual shape:

~~~yaml
id: EVID-LIFECYCLE-PREREQ-CHANGE
providers:
  - validators/validate_capability_lifecycle.py
  - spec/scenario-suite/scenarios/selective-lifecycle-revalidation.yaml
satisfies:
  - A14-R01
test_level: TL1
methods: [EM-03, EM-06]
oracle_class: O1
execution_nature: deterministic
status: implemented
verified_at_revision: <commit>
limitations:
  - does not establish generic split/merge migration
~~~

### Evidence status

Allowed conceptual states:

- `designed` — design exists but no executable evidence;
- `ready` — design reviewed and implementation may start;
- `implemented` — evidence exists and can be executed/inspected;
- `verified` — evidence mapping has been independently re-audited;
- `stale` — evidence no longer proves the current contract;
- `retired` — superseded and not counted.

The registry should not automatically promote `implemented` to `verified`.

### Evidence provenance

Every evidence record declares:

- test level;
- evidence methods;
- oracle class;
- deterministic vs judgement-dependent execution;
- synthetic / known-project / independent-holdout source type;
- concrete source refs;
- Harness revision or version at verification;
- limitations.

Provider/model identifiers are included when the evidence is model-backed.

## Completeness algorithm

For each release-critical ability:

1. enumerate its required requirements;
2. for each requirement, find active evidence records declaring that
   requirement under `satisfies`;
3. verify each candidate meets the requirement's level/method/oracle/execution
   constraints;
4. reject stale/retired evidence;
5. mark the requirement SATISFIED only if at least one admissible evidence
   record remains;
6. mark the ability SATISFIED only when all release-applicable requirements are
   satisfied;
7. preserve all missing/insufficient requirement identities in the report.

The result is a set/vector of satisfied and missing proof slots.

Do not average them into a percentage by default.

## No implicit substitution

The validator must reject these patterns:

- TL6 evidence offered as the only proof for a required TL1 mechanism slot;
- O0 implementation-derived output offered where O1+ is required;
- deterministic router evidence offered where judgement execution is required;
- fixture-schema validation offered as behavioral execution;
- known-project O2 evidence offered as independent O3 holdout;
- a scenario's `covers` declaration offered without a registry evidence
  mapping.

Explicit policy may permit substitution for a particular requirement, but it
must be recorded in the requirement itself.

## Mapping existing evidence

Initial population should reuse existing evidence rather than creating new tests.

Examples likely to map directly after review:

- Core acceptance/validators -> HA-A01 requirements;
- graph validators/deep-DAG regression -> HA-A02;
- target-state scenarios -> HA-A03;
- Engineering Coverage validators/scenarios -> deterministic portions of HA-A06;
- semantic derivation/admission scenarios -> HA-A12;
- Question resolution/current-snapshot evidence -> HA-A13/HA-A14;
- Project Frontier/Publication -> HA-A15;
- deterministic skill/method/artifact routing -> deterministic portion of HA-A16;
- Consumer Pack validators -> HA-A18;
- CI policy validator -> HA-A19;
- calibration scorer/live binding protocol -> portions of HA-A20.

Formation/agent abilities remain unsatisfied until genuine behavioural evidence
exists.

## Relationship to Scenario Suite

Scenario requirements and assurance requirements are not the same objects.

A Scenario Suite case may become an evidence provider:

~~~text
Scenario case
    -> evidence record
    -> satisfies assurance requirement
~~~

The assurance registry validator may check that referenced scenario ids exist,
but it must not infer assurance satisfaction merely from scenario category,
filename, or self-declared `covers`.

## Relationship to CI registry

The CI registry answers:

> Will this executable check run at the appropriate time/cost?

The Assurance Registry answers:

> Does the evidence we have satisfy the required proof obligations?

A check may be correctly registered in CI while no assurance requirement points
to it.

Conversely, provider-backed TL4 evidence may be required for a release claim
while remaining operator-triggered under CI policy.

## Self-tests

The future registry validator must include at least these meta-cases.

### AR-M01 — missing requirement evidence

All referenced executable checks are green, but one release-critical
requirement has no evidence.

Expected: assurance INCOMPLETE.

### AR-M02 — wrong level substitution

Only TL5/TL6 evidence exists for a required non-substitutable TL1 slot.

Expected: requirement remains UNSATISFIED.

### AR-M03 — weak oracle

Evidence declares O0 while requirement needs O1.

Expected: UNSATISFIED.

### AR-M04 — wrong execution nature

A deterministic fixture points to a requirement that explicitly needs agent
judgement execution.

Expected: UNSATISFIED.

### AR-M05 — missing evidence ref

Evidence record points to a deleted/unknown validator/scenario/eval artifact.

Expected: registry validation failure.

### AR-M06 — orphan release-critical failure mode

A release-critical ability contains a failure mode mapped to no requirement.

Expected: registry validation failure.

### AR-M07 — unknown ability/failure/method/TL/oracle id

Expected: fail closed.

### AR-M08 — explicit limitation preserved

Evidence can satisfy one requirement while declaring a limitation that prevents
it satisfying another broader requirement.

Expected: no automatic broadening.

### AR-M09 — unchanged execution binding

A provider-run execution binding names a bound file whose Git blob identity
matches the current repository content.

Expected: binding remains admissible.

### AR-M10 — bound execution mutation

A provider-visible instruction/runtime file named by the provider-run binding is
mutated while the recorded Git blob identity remains unchanged.

Expected: binding is stale and active judgement evidence is rejected.

### AR-M11 — unrelated repository mutation

A repository file outside the provider-run execution binding is mutated while
all bound file identities remain unchanged.

Expected: binding remains admissible; unrelated repository churn does not stale
the judgement evidence.

## Report shape

A future validator/report should expose, at minimum:

~~~text
abilities:
  HA-A05:
    status: INCOMPLETE
    satisfied_requirements: [...]
    missing_requirements: [...]
    insufficient_evidence:
      - evidence_id
        reason
evidence:
  ...
summary:
  release_claim_ready: false
~~~

The report may count requirements for navigation, but counts are not a quality
score.

## Change impact

When a Harness change maps to an ability/failure mode:

1. inspect the assurance requirements for that failure mode;
2. identify existing evidence that can be reused;
3. add a new Test Design only for an uncovered proof slot;
4. implement the smallest READY design;
5. add/update evidence record;
6. re-run assurance-registry validation;
7. run CI according to CI Execution Policy.

This makes test design part of change design rather than an afterthought.

## Versioning

Ability/failure-mode semantics are versioned by their canonical model, not by
renaming evidence files.

Breaking changes to requirement semantics should create a new requirement
identity or explicit migration; silently changing what an old evidence record
means is not allowed.

## Non-goals

This design does not:

- mechanically encode every human-readable Ability/failure statement in the initial seed;
- automatically classify arbitrary tests;
- treat test counts as coverage;
- require every ability to have the same levels/methods;
- make TL order a scalar maturity score.

## Implementation gate

The initial implementation gate is satisfied by the reviewed Test Design
Catalog and the smallest useful registry seed. Expansion remains gated by the
same rule: add only reviewed Ability/failure/evidence relationships and map
existing evidence before introducing new proof infrastructure.

Do not mechanically transcribe every prose line into the registry.
