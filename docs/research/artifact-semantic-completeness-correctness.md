# Research — Artifact semantic completeness and correctness

Status: research only. Not canonical. No main changes.

## Question

How can Harness control that a canonical engineering artifact is not only present and structurally valid, but also:

1. semantically complete for the capability it claims to provide;
2. semantically correct with respect to accepted upstream knowledge;
3. free of invented decisions, silent contradictions and accidental ownership transfer;
4. suitable as trusted input for downstream algorithmic planning.

This research deliberately separates artifact semantic validation from Engineering Coverage.

## Existing baseline

Current Harness already proves a different property:

```text
activated Engineering Concern
  -> accepted semantic claim
  -> producing Capability
  -> valid canonical realization
  -> COVERED
```

That answers:

> Is there accepted project knowledge that proves this concern is covered?

It does not fully answer:

> Does the content of the realizing artifact actually contain every required semantic element, and are those elements correct?

A declared semantic claim can therefore be structurally valid while the artifact body is incomplete, contradictory or semantically wrong.

## Core distinction

Three properties must remain independent.

### 1. Engineering coverage

Subject: project/scope.

Question:

> Have all activated engineering concerns been decided or explicitly dispositioned?

Existing owner: Engineering Coverage evaluator.

### 2. Artifact semantic completeness

Subject: one produced capability / artifact instance.

Question:

> Does this artifact contain all semantic claims and instances required by its artifact contract for this scope?

Example:

A domain model may declare `engineering.domain.model`, but be incomplete if a required domain concept, invariant or subject instance is absent.

### 3. Artifact semantic correctness

Subject: each semantic assertion in an artifact.

Question:

> Is this assertion supported by accepted inputs and compatible with all applicable upstream constraints?

Example:

An artifact can mention every required concept and still assign the wrong responsibility, invent an invariant or contradict an accepted requirement.

Therefore:

```text
coverage != completeness != correctness
```

A completion gate is sound only when all three are satisfied.

## Required semantic validation chain

Preferred conceptual chain:

```text
accepted upstream canonical knowledge
        ↓
artifact production contract
        ↓
required semantic obligations
        ↓
candidate artifact assertions
        ↓
semantic completeness validation
        ↓
semantic correctness validation
        ↓
accepted CanonicalArtifact realization
        ↓
Capability / semantic_claims become usable proof
        ↓
Engineering Coverage
```

The important ordering is that semantic claims must not become usable Coverage proof merely because they were declared in the Engineering Graph.

They become proof only after the realizing artifact passes semantic acceptance.

## Finding P0 — current semantic_claim declaration is too trusting

Current Coverage logic can derive `COVERED` from a realized capability whose production contract declares an accepted semantic claim.

That mechanism assumes that artifact acceptance already guaranteed the claim.

For managed artifacts this assumption is partly implemented through artifact-specific skills, but it is not represented as a uniform machine-verifiable semantic acceptance contract.

Risk:

```text
declared semantic_claim
+ structurally realized artifact
-> COVERED
```

may produce a false positive when the artifact content does not actually satisfy the claim.

Required correction at architecture level:

> Capability realization used as semantic proof must carry evidence that the artifact passed the semantic acceptance contract applicable to that production.

This should initially be modeled above Core rather than by adding a new Core entity.

## Finding P0 — completeness requires obligations, not prose inspection

Semantic completeness cannot be defined as “document looks complete”.

It requires an explicit set of expected semantic obligations.

For each artifact kind / production contract, Harness needs to derive a finite expectation set such as:

```text
required obligations =
  artifact-kind baseline obligations
  + capability-specific obligations
  + subject instances required by scope
  + upstream requirements/constraints that must be represented
```

Examples:

Domain Model:

- required concepts;
- required identities where applicable;
- required responsibilities;
- required invariants;
- terminology consistency.

Machine Interface Contract:

- required operations;
- inputs and outputs;
- error semantics;
- compatibility/versioning rules;
- security-relevant boundary semantics.

Test Design:

- selected requirements;
- expected behavior;
- failure semantics;
- verification method;
- required quality/security/reliability obligations.

Completeness then becomes set closure:

```text
expected semantic obligations
-
satisfied semantic obligations
=
missing semantic obligations
```

This is algorithmically controllable.

## Finding P0 — correctness requires provenance at assertion level

Artifact-level dependency links are insufficient to prove correctness.

They answer:

> Which upstream artifacts were relied upon?

They do not answer:

> Which upstream accepted statement supports this particular assertion?

For high-confidence semantic validation, candidate artifact assertions should expose provenance sufficient to evaluate:

```text
assertion
  -> supporting accepted upstream assertion(s)
  -> transformation/derivation rule
  -> deciding Authority
```

Not every prose sentence needs an ID. The requirement applies to semantic assertions that materially establish the capability.

Minimal useful representation:

```yaml
semantic_assertions:
  - id: domain.order.unique-number
    kind: invariant
    subject: Order
    statement: ...
    derived_from:
      - requirement: REQ-123
      - decision: ADR-17
```

Exact schema is not yet recommended for canonicalization; this is a research direction.

## Semantic correctness classes

Correctness is not one check. At least five classes are required.

### A. Source fidelity

The artifact must preserve accepted upstream meaning.

Failure examples:

- changing MUST into SHOULD;
- narrowing or widening scope;
- losing a condition;
- replacing a business rule with an implementation convention.

### B. Non-invention

Every material assertion must be one of:

- directly accepted upstream knowledge;
- a derivation permitted by the selected Authority;
- a new decision explicitly owned and accepted by that Authority.

Unknowns must become Questions rather than implicit truth.

### C. Internal consistency

Assertions inside one artifact must not contradict each other.

This is partly machine-checkable for structured artifacts and typed relationships.

### D. Cross-artifact consistency

The artifact must not contradict applicable accepted upstream or sibling canonical truth.

The existing dependency/Authority graph provides the search boundary; semantic assertion bindings provide the comparison unit.

### E. Ownership correctness

An artifact must not silently decide semantics owned by another Authority.

This can be validated by mapping assertion kinds / semantic claims to Authority competence.

## Semantic completeness model

Recommended research abstraction:

```text
SemanticExpectation
  concern/claim
  obligation kind
  subject selector
  cardinality
  provenance requirement
  validator
```

Examples:

```yaml
- expectation: domain.invariant
  subject: Order
  cardinality: one_or_more
  source: accepted requirements

- expectation: interface.operation
  subject_set: public application commands
  cardinality: all
  source: application design
```

This is deliberately an acceptance/checking abstraction, not a proposed Core entity.

The expectation set may be derived from:

- the artifact skill;
- the production contract;
- selected upstream capabilities;
- selected requirements;
- subject/scope closure;
- reusable engineering policy.

## Semantic correctness proof levels

Arbitrary natural-language correctness is not fully decidable. Harness should therefore use a layered proof model.

### Level 0 — structural validity

Schema, references, ownership and graph consistency.

Existing mechanisms already cover much of this.

### Level 1 — obligation completeness

Every required semantic obligation has a candidate assertion.

Machine-verifiable when obligations and assertions are structured.

### Level 2 — deterministic semantic invariants

Typed relationships and domain-specific validators.

Examples:

- every error code is documented once;
- all selected requirements have verification coverage;
- every public operation has declared failure semantics;
- dependency direction obeys accepted architecture constraints.

Machine-verifiable.

### Level 3 — provenance consistency

Each material assertion has acceptable upstream support and no unresolved blocker.

Mostly machine-verifiable when source assertions are addressable.

### Level 4 — semantic entailment/review

Does the assertion actually preserve the meaning of the cited source?

For unrestricted prose this requires semantic interpretation. An LLM/agent may evaluate it, but such evaluation is evidence, not mathematical proof.

Reliability can be increased through:

- constrained artifact schemas;
- structured assertions;
- independent reviewer pass;
- adversarial contradiction search;
- deterministic validators where patterns stabilize.

### Level 5 — executable witness

Where semantics can be operationalized, executable tests/models provide stronger evidence.

Examples:

- state-machine invariants;
- API examples against schema;
- property-based tests;
- architecture dependency tests;
- requirement acceptance tests.

This is the strongest available evidence for applicable assertions, but not every design decision has an executable witness.

## Recommended acceptance state

A capability realization should be semantically usable only when:

```text
structural_valid
AND obligations_complete
AND deterministic_checks_pass
AND no unresolved semantic conflict
AND required provenance present
AND semantic review accepted where deterministic proof is unavailable
```

Conceptually:

```text
artifact created
  -> DRAFT
  -> structurally valid
  -> semantically evaluated
  -> ACCEPTED
  -> register as usable canonical realization
```

Harness Core itself should still store accepted knowledge state, not workflow stages.

The acceptance lifecycle belongs in the managed-artifact/workbench layer.

## Relationship to Questions

A semantic validator must produce a Question instead of “best-effort fixing” when:

- required input meaning is ambiguous;
- two accepted sources conflict;
- a required decision is absent;
- correctness depends on an Authority outside the current artifact;
- a semantic obligation cannot be satisfied without inventing knowledge.

This matches existing Core semantics and avoids adding an Error/Review/Gate entity.

## Relationship to Coverage

Coverage should consume only accepted semantic realization.

New conceptual rule:

```text
semantic claim declared by production contract
AND artifact realization exists
AND artifact semantic acceptance is valid
AND lifecycle is current
AND no blocking Question
=> claim is usable coverage proof
```

Therefore Coverage remains a derived project-level projection.

Semantic validation remains artifact-level acceptance.

Neither should duplicate the other's state.

## Candidate implementation direction

Do not begin by creating a universal semantic ontology.

Use the existing artifact-skill boundary.

Each artifact skill should eventually define:

1. **input contract** — which accepted canonical inputs may be used;
2. **semantic obligations** — what must be present for the requested capability;
3. **forbidden invention rules** — what may not be inferred;
4. **deterministic validators** — assertions that can be mechanically checked;
5. **review obligations** — semantic judgments still requiring model/human review;
6. **proof output** — machine-readable acceptance result.

Common acceptance policy can aggregate those outputs.

Candidate research-only result:

```yaml
kind: harness-artifact-semantic-evaluation
artifact: DOMAIN-MODEL
capability: engineering.domain.model
status: ACCEPTED
obligations:
  expected: [...]
  satisfied: [...]
  missing: []
checks:
  deterministic: PASS
  provenance: PASS
  consistency: PASS
review:
  required: true
  result: ACCEPTED
semantic_claims:
  accepted:
    - engineering.domain.model
```

This result should be reproducible/generated evidence, not a second semantic source of truth.

## Why a generic LLM review alone is insufficient

A prompt such as “check whether this document is complete and correct” has no stable proof boundary.

It lacks:

- explicit expected obligations;
- exact source boundary;
- ownership rules;
- stable failure categories;
- reproducible acceptance criteria.

LLM review is useful only after Harness has constrained:

```text
what must be checked
against which accepted inputs
under which Authority
for which capability
with which stop conditions
```

## Recommended control loop

```text
Target State / CREATE expectation
        ↓
artifact skill
        ↓
derive semantic obligations
        ↓
produce candidate
        ↓
extract/register candidate assertions
        ↓
deterministic completeness + consistency checks
        ↓
semantic provenance/review
        ↓
Question(s) if unresolved
        ↓
accepted artifact
        ↓
register realization
        ↓
Engineering Coverage re-evaluation
```

This gives Harness an end-to-end algorithmic loop:

```text
plan missing knowledge
-> produce it
-> prove artifact acceptance
-> expose accepted semantic claims
-> recompute remaining engineering coverage
```

## P1 — requirement traceability is necessary but not sufficient

Requirements are one major correctness source, but not the only one.

Artifact correctness may depend on:

- requirements;
- domain decisions;
- architecture constraints;
- security obligations;
- external policy/standards;
- upstream artifact invariants.

Therefore semantic validation should use the complete prerequisite closure, not a requirements-only matrix.

## P1 — semantic claims need acceptance provenance

A production contract states what a capability intends to prove.

It should not by itself assert that a particular artifact instance successfully proves it.

Preferred separation:

```text
production semantic_claims = intended semantic capability
artifact semantic evaluation = accepted realization evidence
coverage evaluator = consumes accepted realization
```

This avoids circular proof.

## P1 — completeness must be subject-aware

Many claims are not global booleans.

Examples:

- every externally visible operation needs error semantics;
- every persisted aggregate needs integrity decisions;
- every sensitive data class needs handling rules;
- every selected requirement needs verification.

Therefore expectation derivation must support subject instances/cardinality.

The existing Coverage work already discovered the same issue at concern level; artifact validation should reuse the same subject-aware principle.

## P2 — contradiction detection should be incremental

Do not compare every artifact with the entire repository.

Use graph boundaries:

```text
candidate artifact
  -> declared dependencies / required capabilities
  -> applicable upstream semantic assertions
  -> sibling assertions owned by same Authority where relevant
```

This keeps validation tractable and reduces false conflict detection.

## Core impact hypothesis

No Core change is currently justified.

Existing Core concepts remain sufficient:

- Authority — owns semantic decisions;
- CanonicalArtifact — accepted truth after validation;
- CapabilityId — accepted provided knowledge;
- Question — unresolved semantic gap;
- dependencies — establish semantic input boundaries.

The missing mechanism is an **artifact semantic acceptance layer above Core**.

Core should receive only accepted results.

## Proposed next experiment

Validate this model against three artifact kinds with different semantic shapes:

1. `domain-model/v1` — concept/invariant-heavy;
2. machine interface contract — enumerated subject coverage and compatibility semantics;
3. test design — requirement/behavior traceability and executable witness potential.

For each artifact kind:

1. derive semantic obligations from current skill + selected prerequisites;
2. build one valid candidate;
3. inject controlled defects:
   - missing required semantic element;
   - contradicted upstream decision;
   - invented decision;
   - wrong Authority ownership;
   - incomplete subject coverage;
4. verify the evaluator catches each defect;
5. identify checks that are deterministic vs semantic-model review;
6. measure false positive/false negative behavior.

Success criterion:

> Coverage must never become `COVERED` from a semantically defective managed artifact in the experiment.

## Research conclusion

Harness already has the project-level mechanism for deciding whether engineering concerns are covered.

The missing layer is artifact-level semantic acceptance.

The preferred architecture is:

```text
Core truth
  -> production expectation
  -> artifact-specific semantic obligations
  -> candidate artifact
  -> semantic acceptance evidence
  -> accepted canonical realization
  -> usable semantic claims
  -> Engineering Coverage
```

The central design principle is:

> Semantic completeness is closure over explicit obligations; semantic correctness is justified consistency of each material assertion with accepted upstream knowledge and ownership.

Do not canonicalize this yet. The next step should be the defect-injection experiment on representative artifact kinds.
