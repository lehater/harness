# Harness Assurance Policy v0

Status: canonical.

## Purpose

Define how evidence for Harness changes and release claims is selected, layered,
and interpreted.

This policy answers:

- what must be proven about a Harness ability or change;
- what test scope should be attempted first;
- when synthetic fixtures are preferable to project-scale tests;
- when agent/evaluator execution is actually required;
- what role real projects and independent holdouts play;
- how oracle strength and evidence gaps must be represented.

It does not define when CI executes existing checks. That is owned by
`docs/design/ci-execution-policy-v0.md`.

It does not replace subsystem acceptance contracts or the Scenario Suite. Those
are evidence providers governed by this policy.

## Core principle

Use the **smallest falsifiable surface** that can expose the failure mode under
test.

A larger, more realistic fixture is not stronger evidence merely because it is
larger. When a mechanism can be falsified with a small synthetic fixture, that
fixture is the preferred first proof because it provides the strongest failure
localization and the clearest oracle.

Evidence grows upward only when the lower level cannot exercise a material
interaction, judgement boundary, or portability risk.

## Assurance ownership

The assurance system has four separate responsibilities:

~~~text
Harness Assurance Policy
    owns evidence-selection principles and test levels

Ability-to-Evidence model
    owns what Harness responsibilities/failure modes require evidence
    (docs/design/harness-ability-to-evidence-v0.md)

tests / validators / scenarios / eval protocols
    provide concrete evidence

CI Execution Policy
    owns when registered deterministic evidence executes
~~~

Audit artifacts describe observed evidence and gaps. They are not normative
owners of future testing policy.

Provider-backed semantic assurance additionally follows
`spec/assurance/llm-execution-policy-v1.yaml`.

## Normative principles

### HA-P01 — smallest falsifiable surface

A Harness mechanism should first be tested at the smallest scope that contains
the behavior and its oracle.

Do not begin with a whole repository when a minimal structured fixture can prove
or falsify the same invariant.

### HA-P02 — bottom-up evidence promotion

Evidence should progress from isolated mechanisms toward larger system surfaces.

Skipping a missing lower level is not justified by a passing larger test unless
the lower level is genuinely incapable of expressing the interaction.

A project-scale pass cannot compensate for the absence of a mechanism-level
oracle.

### HA-P03 — synthetic-first mechanism evidence

Deterministic algorithms, state transitions, routing, validation rules,
dependency semantics, and similar mechanisms should prefer controlled synthetic
fixtures.

Synthetic evidence should include positive, negative, and material mutation
cases where applicable.

### HA-P04 — controlled composition before project realism

After isolated mechanisms have stable evidence, adjacent mechanisms should be
tested in short controlled chains before introducing a full project fixture.

Composition evidence should preserve failure localization: the fixture must make
the expected intermediate or final semantic contract explicit enough to identify
which boundary failed.

### HA-P05 — micro-project before real project

A bounded end-to-end procedure should first be exercised on a controlled
synthetic micro-project when its behavior depends on repository/project shape.

The micro-project should contain only enough structure to activate the intended
failure modes and should have an independently authored expected model or
invariants.

Exact repository size is deliberately not prescribed.

### HA-P06 — agent/evaluator evidence only for judgement-dependent behavior

Do not use repeated LLM/agent execution to prove behavior that a deterministic
oracle can establish.

Agent or evaluator execution is required when the ability being tested includes
material semantic judgement, natural-language operation selection, project-model
formation, or another nondeterministic responsibility that cannot be reduced to
a deterministic mechanism without bypassing the behavior under test.

### HA-P07 — independent oracle

Expected results should be independent from the implementation or model being
tested to the greatest practical extent.

An oracle produced by the same mechanism under test is weak evidence and must
not be presented as independent validation.

### HA-P08 — real projects have a distinct role

Known real projects are regression/system evidence after lower-level mechanisms
are understood.

Independent real projects are portability/generalization holdouts after
synthetic mechanism, composition, and bounded procedure evidence is credible.

Real-project size is not itself an assurance objective.

### HA-P09 — ability-driven coverage

Assurance completeness is defined from Harness responsibilities and their
material failure modes, not from raw test/scenario counts.

Every release-critical ability should eventually have an explicit mapping:

~~~text
ability
-> observable contract
-> material failure modes
-> minimum required evidence levels/classes
-> acceptable oracle class
-> current evidence references
-> release-critical flag
~~~

Scenario catalogs and CI inventories are evidence inventories. They must not be
treated as the independent denominator of Harness correctness.

### HA-P10 — heterogeneous evidence remains heterogeneous

Do not collapse structurally different evidence into one percentage or score
unless a separately accepted statistical model justifies that aggregation.

A deterministic Core invariant, an agent discovery judgement, and a provider
calibration corpus have different assurance semantics.

### HA-P11 — unknown evidence remains visible

Missing evidence, unsupported promotion, and unresolved oracle quality must be
reported explicitly.

A green higher-level scenario must not silently convert a missing lower-level
proof into "covered".

## Test-level hierarchy

The levels describe **scope of exercised system surface**, not importance.

### TL0 — structural/static contract

Typical evidence:

- schema validation;
- registry consistency;
- required/forbidden fields;
- static ownership/inventory rules.

Use when the failure class is representational rather than behavioral.

### TL1 — isolated mechanism

Typical evidence:

- minimal synthetic structured fixture;
- positive/negative cases;
- invariant/property/mutation cases;
- one deterministic algorithm or one bounded semantic decision surface.

This is the default starting level for a new or changed mechanism.

### TL2 — composed mechanisms

Exercise a small chain of adjacent responsibilities, normally two to a few
mechanisms.

Examples:

~~~text
accepted evidence
-> applicability
-> Capability selection
-> dependency formation
~~~

or:

~~~text
task intent
-> operation selection
-> deterministic router
-> selected skill identity
~~~

Use TL2 when the material risk lies at a boundary between mechanisms.

### TL3 — controlled synthetic micro-project

Exercise one bounded project-shaped use case using a small synthetic repository
or workspace with an independently authored oracle.

Use TL3 for procedure integration, bootstrap/reconcile behavior, project-shaped
source boundaries, and other behavior that cannot be represented faithfully by
a few structured values.

### TL4 — repeated clean-context agent/evaluator execution

Repeat the same frozen TL3 fixture in independent clean contexts when the tested
ability includes agent or semantic judgement.

Compare normalized semantic outputs rather than literal prose.

Potential dimensions include:

- omissions;
- inventions;
- Authority partition agreement;
- Capability identity agreement;
- dependency-edge agreement;
- applicability classification;
- Question ownership;
- Consumer closure.

The number of repetitions belongs to the specific eval protocol; this policy
does not prescribe a universal count.

### TL5 — known real-project regression

Use a pinned, understood project or project slice to verify that lower-level
evidence survives realistic complexity and integration.

Known projects that participated in Harness design remain valuable regression
evidence but are not independent holdouts for the mechanisms they helped shape.

### TL6 — independent real-project holdout

Use a frozen project/domain that did not materially shape the mechanism or its
oracle.

TL6 challenges portability/generalization. It is deliberately late because
failures at this level have the lowest diagnostic resolution.

## Promotion rules

Not every change must reach every level.

Choose the highest required level from the affected ability and failure mode.

Examples:

- a local parser/validator invariant may require only TL0/TL1;
- target-state precedence across mechanisms naturally requires TL2;
- bootstrap/reconcile procedure integration normally requires TL3;
- judgement-dependent project discovery requires TL4;
- portability claims require TL5/TL6.

Promote upward when at least one of these is true:

- the failure mode depends on interaction between separately proven mechanisms;
- project-shaped context changes the behavior materially;
- semantic/agent judgement is itself under test;
- realistic integration introduces a risk absent from controlled fixtures;
- a portability/generalization claim is being made.

Do not promote solely because a larger test appears more realistic.

## Oracle classes

Oracle strength is tracked independently from test level.

| Class | Meaning | Typical use |
|---|---|---|
| O0 | Implementation-derived or materially circular expectation | Diagnostic only; avoid as correctness proof |
| O1 | Hand-authored contract/invariant | Deterministic mechanisms and controlled synthetic fixtures |
| O2 | Accepted real-project truth | Known-project regression |
| O3 | Frozen independent holdout oracle | Portability/generalization evidence |
| O4 | Blinded independent expert/reference judgement | Semantic evaluator/agent calibration where appropriate |

A high test level with a weak oracle is not automatically strong evidence.

## Ability-to-Evidence contract

The canonical model is
`docs/design/harness-ability-to-evidence-v0.md`.

It preserves, for each material Harness ability:

- stable ability identity;
- observable contract;
- material failure classes;
- whether execution is deterministic or judgement-dependent;
- minimum required test levels;
- required evidence classes such as invariant, mutation, lifecycle,
  reproducibility, scale, or real-project regression;
- minimum acceptable oracle class;
- current evidence references;
- known gaps;
- release-critical flag.

The current canonical model is intentionally human-readable design. The exact
machine-readable registry format is not defined by this policy. Introducing or
changing that representation is a separate implementation change.

## Change procedure

For a Harness change:

1. identify the affected ability/responsibility;
2. state the failure mode or accepted architecture decision;
3. choose the lowest test level capable of falsifying it;
4. add/update that evidence before or with observable behavior changes when an
   oracle exists;
5. promote to a larger level only for a material interaction/risk;
6. preserve oracle independence and record evidence limitations;
7. use the CI Execution Policy to decide when registered checks execute;
8. before integration, run the full applicable deterministic gate on the exact
   candidate.

A change that only creates or clarifies this policy and does not alter
observable Harness behavior does not require inventing a behavioral regression
fixture.

## Relationship to Scenario Suite

`docs/design/scenario-suite-v0.md` remains the executable cross-layer
behavioral specification.

Under this policy:

- focused scenario cases may provide TL1/TL2 evidence;
- workspace/project-shaped scenarios may provide TL3 evidence;
- a scenario labelled agent-evaluation is not TL4 unless it actually executes
  the relevant agent/evaluator responsibility in clean contexts;
- real-project scenarios may provide TL5 evidence;
- a scenario becomes TL6 only when project/oracle independence is established.

Scenario coverage remains necessary but is not the independent definition of
Harness assurance completeness.

## Relationship to CI

`docs/design/ci-execution-policy-v0.md` governs execution cost, ordering,
draft behavior, and final deterministic gates.

This policy governs **evidence sufficiency**.

Therefore:

~~~text
Assurance Policy: what evidence is needed
CI Policy:        when registered evidence runs
~~~

Neither policy replaces the other.

External/provider-backed assurance may remain operator-triggered even when it is
required for a broader release claim; it does not have to become an ordinary
per-PR deterministic gate.

## Release claims

A claim that a Harness version performs a release-critical responsibility should
identify the evidence basis rather than rely on "all tests green".

At minimum:

- the responsibility has an observable contract;
- material failure modes are mapped to evidence;
- the required test level(s) and oracle strength are satisfied;
- known evidence gaps are explicit;
- no known open defect contradicts the claim;
- the exact integration candidate passes the required deterministic full gate.

No single global percentage is required or implied.

## Non-goals

This policy deliberately does not prescribe:

- a fixed number of files in a micro-project;
- a universal number of repeated agent runs;
- mandatory TL6 evidence for every local change;
- one mandatory project archetype list for all future versions;
- one scalar quality score;
- implementation details of a future Ability-to-Evidence registry.

Those parameters belong to the specific ability, eval protocol, experiment, or
release decision.

## Evolution

Weakening the smallest-falsifiable-surface principle, allowing higher-level
passes to substitute for missing lower-level evidence, or changing the role of
real-project/holdout evidence requires an explicit architecture decision.

New evidence mechanisms may be added without changing this policy when they
preserve these ownership and promotion rules.
