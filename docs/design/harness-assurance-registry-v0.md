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
- `checks/validate_assurance_registry.py` — structural validation, admissibility/completeness report, and AR-M01..AR-M13 meta-self-tests.

The seed is intentionally incomplete. It includes HA-A01 Core structural truth,
HA-A02 Engineering Graph topology, HA-A03 Target-state action semantics,
HA-A04 Authority formation, HA-A05 Capability formation, HA-A06 Engineering Coverage,
HA-A07 Project Authority migration, HA-A08 Design target selection,
HA-A09 existing-project
bootstrap/reconcile, HA-A10 Greenfield bootstrap, HA-A11 Source acquisition/completeness,
HA-A12 Semantic derivation/admission, HA-A13 Questions/blockers, HA-A14 Lifecycle/currentness, HA-A15 Frontier/publication, HA-A16 routing, HA-A18 Consumer distribution/compatibility,
and HA-A19 assurance self-test obligations. HA-A05 remains split
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
existing-project suite TD-BOOT-E01..E05, making run `36942421201` historical
for the newer execution surface.

Provider-backed run `36947887869` is the current accepted record for Harness
revision `8641130437862f06319f111a412847ae1e61d934`. It executed all 16
registered cases successfully, including the two-step TD-BOOT-E04
bootstrap/reconcile sequence. The evidence record binds all 17 provider calls;
run 2 of TD-BOOT-E04 is cryptographically linked to run 1 and to the injected
Core realization. Provider-auto resolved 10 calls to `gpt-6-luna` and 7 to
`mai-code-1.1-flash`; the run consumed 117860 input and 4429 output tokens.

Provider-backed TL4 run `36949909315` then executed TD-COMP-003 and
TD-BOOT-E06 three times each in independent clean contexts. All six provider
calls passed their frozen semantic oracles. TD-COMP-003 selected
`project-bootstrap-reconcile` in all three runs despite hostile
instruction-like project data; TD-BOOT-E06 converged on the same normalized Core
realization and BLOCKED Target State in all three runs.

Provider-backed TL4 run `37073140125` added TD-QST-001 to the same campaign.
All three clean-context TD-QST-001 calls passed. Provider-auto resolved all three
to `mai-code-1.1-flash`; each normalized result contained exactly one
REFUND-DESIGN Question blocking only `refund.window-policy`, while the related
retryable repository-scan timeout created no semantic Question.

The current admitted proof state remains deliberately partial: HA-A01 satisfies
A01-R01 through a focused TL1 ownership/reference mutation matrix, A01-R02
through deterministic structural interpretation, and A01-R03 through explicit
Question acceptance-transition evidence. HA-A02 satisfies A02-R01 through
topology/dead-production validation, A02-R02 through exact Consumer closure plus
declaration-reorder metamorphic evidence, and A02-R03 through the 1200-node
deep-DAG regression. HA-A03 satisfies A03-R01 through Target State truth-table,
provider-removal/blocker, multi-provider, and lifecycle-gap composition evidence,
and A03-R02 through explicit representation-order invariance. A04-R01 and
A05-R01 are satisfied; HA-A06 satisfies A06-R01 through explicit
disposition/subject-completeness evidence and A06-R02 through scope-root
activation isolation. HA-A07 satisfies A07-R01 through fail-closed
retire/split/merge/rename migration evidence and A07-R02 through unchanged
assessment preservation. HA-A08 is explicitly INCOMPLETE: A08-R01 requires
a judgement-backed bounded selection/anti-template-bias case, A08-R02 requires
the TL3 project-shaped minimal-target proof, and A08-R03 requires repeated
clean-context convergence. HA-A09 satisfies A09-R01 (TL2),
A09-R02 (TL3), and A09-R03 (TL4); HA-A10 is explicitly INCOMPLETE with
A10-R01/A10-R02 waiting on the blocked TD-BOOT-G01..G04 TL3 greenfield cases
and A10-R03 waiting on TD-BOOT-G05 repeated clean-context execution. HA-A11
satisfies A11-R01 through deterministic source-set/boundary/statement
completeness; A11-R02 source relevance/noise selection and A11-R03 repeated
trust-boundary execution remain missing because their current provider records
are stale or their designs are not yet implemented. HA-A12 satisfies A12-R01 through deterministic
semantic derivation/admission evidence; A12-R02 remains missing because the
current provider-auto calibration refresh did not meet the frozen O4 protocol. HA-A13 satisfies A13-R01/A13-R02 through deterministic
Question routing, blocking, resolution-identity and stale-snapshot evidence, and
A13-R03 through provider run `37073140125`: TD-QST-001 passed three independent
clean-context executions, preserving exactly one semantic blocker while a
related transient repository-scan timeout remained process evidence only. HA-A14 satisfies A14-R01 through selective
prerequisite/policy currentness and replay fail-closed evidence, A14-R02 through
conservative remove/rename/split/merge plus prerequisite-topology evolution, and
A14-R03 through the explicit depth=1200, fan-out=512 and cardinality=2000
lifecycle correctness envelope. HA-A15 satisfies A15-R01 through the
cross-layer precedence/deduplication matrix, A15-R02 through persisted
FAILED_VALIDATION plus explicit retry/prerequisite evidence, and A15-R03 through
coherent terminal publication, CAS, idempotence and simulated crash/retry
evidence at the direct-file publication boundary. HA-A16 satisfies A16-R01..R06; and HA-A18
satisfies A18-R01 (current public-pack closure) plus A18-R02 (immutable pin/API
compatibility). A04-R02/R03, A05-R02/R03, A09-R04, and A18-R03 remain missing. TD-BOOT-E06 does not satisfy raw Capability- or
Authority-formation convergence because those identities are inputs to the
bootstrap-realization fixture rather than outputs of formation judgement. The
previous TD-CAP-003 disagreement in run `36947239747` therefore remains
relevant evidence that lower-level Capability formation has not established TL4
convergence.

Suite manifests are scheduling/inventory surfaces, not per-case semantic
bindings: selected evidence is bound by explicit `case_ids`,
case/fixture/oracle hashes, frozen run-plan cardinality, and immutable
provider/runtime bindings. Adding another case to a suite does not by itself
stale existing case evidence; shared provider/runtime semantics and trusted
instructions actually used by selected cases do.

Registry validity remains separate from release-claim completeness. Because the
seed does not yet register every canonical HA-A01..HA-A21 ability, the report
must expose `denominator_complete: false` plus the missing canonical ability
identities, and `release_claim_ready` must remain false even if every currently
registered seed requirement becomes satisfied.

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
  - tests/test_capability_lifecycle.py
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

Before evaluating proof slots, compare the registered Ability IDs with the
canonical Ability IDs owned by `harness-ability-to-evidence-v0.md`. A partial
registry remains structurally valid as an implementation seed, but its assurance
denominator is incomplete and cannot authorize a release claim.

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
7. preserve all missing/insufficient requirement identities in the report;
8. set `release_claim_ready=true` only when the canonical Ability denominator is
   complete and every registered release-critical Ability is SATISFIED.

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

HA-A01 is now SATISFIED for its current three proof slots. The A01-R01 mutation
matrix exercises representative invalid ownership/provider/dependency/Question
reference shapes. This is bounded O1 evidence; it does not claim exhaustive
property generation across every representable Core document shape.

HA-A02 is SATISFIED for its three proof slots. Its depth evidence is an
explicit tested envelope (1200 nodes), not a claim of unbounded graph scale.

HA-A03 is SATISFIED for its two proof slots. Lifecycle currentness remains
owned by HA-A14; HA-A03 evidence proves the action consequence only, including
that an existing provider with missing lifecycle evidence is surfaced as a gap
rather than recreated.

HA-A06 is SATISFIED for its deterministic applicability/completeness proof
slots. Independent holdout evidence remains relevant only if Harness later makes
a portability/generalization claim about project fact or template discovery.

HA-A07 is SATISFIED for its deterministic migration-safety proof slots.
Accepted applicability is never inherited by a replacement Authority without
evidence; unmapped retirement is now an explicit conflict rather than silent
loss. The evidence is synthetic O1 and does not claim TL5 real-project
generalization.

HA-A08 is now present in the denominator but remains INCOMPLETE. Existing
deterministic closure evaluation and historical/stale provider runs do not
substitute for target-selection judgement. TD-CAP-005 and TD-BOOT-G01/G04/G05
remain the relevant designed evidence paths; TL4 convergence must use repeated
clean-context execution.

HA-A10 is present in the denominator and remains INCOMPLETE by design.
Greenfield bootstrap cannot be proven from pre-authored graph fixtures because
that would bypass the ability itself. TD-BOOT-G01..G04 own the TL3
minimality/unknown/frontier obligations and TD-BOOT-G05 owns TL4 convergence.

HA-A11 is partially satisfied. A11-R01 reuses deterministic source-set,
lossless boundary, and statement-disposition evidence. A11-R02/R03 remain
missing: source relevance/noise selection is judgement-dependent, the relevant
TD-BOOT-E05/E06 provider records are stale after bound runtime changes, and
TD-ROUTE-007 trust-boundary execution is not yet implemented at the required
level.

HA-A12 is partially satisfied. A12-R01 reuses deterministic derivation,
admission, contradiction, semantic-loss, and real-project atom evidence; the
remaining TD-SEM-005 metamorphic gap is now covered by an irrelevant-source
invariance regression. A12-R02 remains missing. Current-surface live calibration
run `37071325425` used provider-auto: its first scorable run resolved to
`mai-code-1.1-flash` and produced one false negative on
`semantic-enforcement-gap` (13/14 correct), while the second provider response
violated the versioned JSON envelope and was rejected as INCOMPLETE. This is
evidence against an A12-F06 PASS, not a reason to weaken the oracle.

HA-A18 deliberately remains INCOMPLETE: current deterministic evidence proves
pack closure/integrity and immutable pin/API handling, while A18-F06 still lacks
a reviewed cross-revision published-identity compatibility proof.

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

### AR-M12 — multi-run provider case binding

A provider-backed case whose reviewed run plan requires a derived sequence
records every provider call under one case entry. The recorded run count must
match the frozen case, every run must be a clean-context PASS, and a
`bootstrap-idempotence` second run must cryptographically bind to the first run
record plus the injected Core model.

Expected: the complete linked sequence is admissible; a missing run or broken
derived-input link is rejected.

### AR-M13 — incomplete canonical Ability denominator

Every requirement in the currently registered seed is satisfied, but at least
one canonical Ability from the semantic owner is absent from the registry.

Expected: registry structure remains valid for incremental adoption,
`denominator_complete=false`, the missing Ability identities are reported, and
`release_claim_ready=false`.


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
  denominator_complete: false
  missing_canonical_abilities: [...]
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
