# Research — Artifact semantic acceptance experiment results

Status: research only. Not canonical. No main changes.

Companion hypothesis:
`docs/research/artifact-semantic-completeness-correctness.md`.

Executable prototype:
- `semantic_acceptance_experiment.py`;
- `validators/validate_semantic_acceptance_experiment.py`.

## Objective

Test whether a small, reusable artifact-semantic acceptance layer can prevent a
semantically defective artifact from becoming usable Engineering Coverage proof.

The experiment intentionally does not attempt arbitrary natural-language theorem
proving. It tests the deterministic boundary that Harness can own reliably before
agent/model semantic review.

## Artifact kinds exercised

Three artifact shapes were selected because they stress different semantics:

1. `domain-model/v1`
   - concepts;
   - responsibilities;
   - invariants.
2. machine interface contract
   - operations;
   - inputs;
   - outputs;
   - error semantics.
3. `test-design/v1`
   - test contracts;
   - preconditions;
   - operations;
   - observable oracles.

These shapes correspond to the current artifact-skill acceptance responsibilities.

## Tested semantic defect classes

For every artifact kind the validator exercised:

- missing required semantic obligation;
- incomplete subject coverage;
- contradicted upstream semantic value;
- invented assertion without provenance or owning-Authority decision;
- assertion kind outside the selected Authority responsibility;
- unknown provenance;
- internal contradiction on one semantic key;
- cross-artifact contradiction against accepted upstream knowledge;
- Coverage proof attempted from a rejected artifact.

Baseline accepted candidates were also tested.

## Result

Executable validation result:

```text
PASS 33 assertions across 3 artifact kinds
```

All injected defect classes were rejected.

Most importantly, the Coverage bridge returned proof only when:

```text
production declares semantic claim
AND semantic evaluation status == ACCEPTED
AND evaluation explicitly accepts that same semantic claim
```

A rejected artifact therefore cannot prove the concern in the experiment.

## What the experiment proves

The following architecture is viable:

```text
artifact skill / production contract
        ↓
derived semantic obligations
        ↓
candidate semantic assertions
        ↓
deterministic semantic acceptance
        ↓
accepted semantic claims
        ↓
Coverage proof
```

The deterministic layer can reliably own at least:

- obligation closure;
- subject cardinality/coverage;
- provenance reference validity;
- Authority assertion-kind boundary;
- exact structured source fidelity;
- internal structured contradiction;
- cross-artifact structured contradiction;
- gating of semantic claims before Coverage.

## What the experiment does not prove

The prototype deliberately uses structured `semantic_value` equality for
deterministic source fidelity.

It does not establish that arbitrary prose entailment can be proven
deterministically.

For example, these still require semantic interpretation unless represented more
structurally:

- whether a paraphrase preserves every condition of a requirement;
- whether a domain responsibility is subtly broader than accepted upstream truth;
- whether two differently worded architecture constraints are equivalent;
- whether an omitted qualification changes meaning.

The architecture therefore still needs a review tier for non-deterministic
semantic judgments.

That review tier should consume an explicit obligation set and bounded source set;
it must not be an unconstrained “review this document” prompt.

## Final responsibility split

### Core

Responsibility:
store accepted engineering truth and unresolved semantic gaps.

Inputs:
accepted canonical artifacts/capabilities and Questions.

Output:
current knowledge graph.

No change demonstrated.

### Artifact skill

Responsibility:
define how one knowledge kind is produced and what semantic obligations must be
satisfied.

Inputs:
CREATE expectation, Authority, prerequisite closure.

Output:
candidate artifact plus artifact-kind-specific semantic obligations/assertions.

This is the natural owner of artifact-specific acceptance rules.

### Semantic acceptance evaluator

Responsibility:
decide whether a candidate realization is sufficiently trustworthy to expose its
semantic claims.

Inputs:
- artifact-kind obligations;
- candidate semantic assertions;
- accepted upstream assertions;
- Authority boundary;
- deterministic validators;
- semantic review evidence where required.

Output:
generated `harness-artifact-semantic-evaluation` evidence with
`ACCEPTED|REJECTED` and accepted semantic claims.

This output is evidence/projection, not a new source of project truth.

### Engineering Coverage

Responsibility:
derive whether all activated engineering concerns are covered.

Input:
only semantic claims from accepted current realizations.

Output:
Coverage state and remaining engineering work.

Coverage must not infer semantic acceptance from artifact existence alone.

## Required acceptance pipeline

The tested end-to-end model is:

```text
Target State / CREATE
        ↓
artifact skill
        ↓
semantic obligations + bounded source closure
        ↓
candidate artifact
        ↓
structural validation
        ↓
deterministic semantic checks
        ↓
semantic review for residual non-deterministic assertions
        ↓
Questions for unresolved/conflicting semantics
        ↓
semantic ACCEPTED
        ↓
register CanonicalArtifact / realization
        ↓
expose accepted semantic claims
        ↓
Engineering Coverage
```

## Findings by priority

### P0 — add semantic acceptance before semantic claims become proof

A production contract declares intended semantic claims. Artifact existence does
not prove that an instance satisfies them.

Any future canonical implementation should require accepted semantic-evaluation
evidence before Coverage consumes a managed artifact's semantic claims.

### P0 — artifact skills need explicit semantic obligation contracts

Current skills already describe acceptance expectations in prose.

The next canonical design should make those expectations machine-addressable
without forcing all artifacts into one universal schema.

Minimum common dimensions demonstrated by the experiment:

- obligation id;
- assertion kind;
- optional subject/subject set;
- cardinality;
- provenance requirement;
- validator/review policy.

### P0 — semantic assertions need addressable provenance where correctness matters

Artifact-level `depends_on` remains useful for dependency closure, but it is too
coarse for assertion correctness.

Material assertions that establish a capability need enough identity/provenance
to relate them to accepted upstream assertions or to an explicit decision by the
owning Authority.

### P1 — deterministic and interpretive checks must remain separate

Deterministic checks can block obvious false acceptance reproducibly.

Semantic-model/agent review is still required for meanings that are not encoded
structurally.

Do not label model review as deterministic proof.

### P1 — subject-aware completeness is mandatory

Global boolean claims are insufficient when the semantic obligation applies to
all operations, aggregates, requirements, data classes, verification checks, or
other subject instances.

The artifact acceptance model should reuse the subject/cardinality principle
already established in Engineering Coverage research.

### P1 — semantic acceptance result must be generated evidence

Do not create a second manually maintained truth source such as
`artifact_is_correct: true`.

The evaluation must be derived from:
- accepted source state;
- current candidate;
- reusable/artifact-specific acceptance contracts;
- explicit review evidence when needed.

### P2 — contradiction search should use graph-bounded scope

Cross-artifact comparison should start from prerequisite/dependency closure and
same-Authority relevant truth, not from every file in the repository.

This keeps the search tractable and reduces false conflicts.

## Core impact

Experiment result: **no Core entity change is justified**.

No evidence requires adding:
- SemanticExpectation;
- Review;
- Gate;
- Approval;
- ValidationResult

as Core entities.

They belong in the artifact-production/acceptance mechanism above Core.

Core continues to receive only accepted knowledge and Questions.

## Canonicalization candidate

The research supports a future canonical change set, but this branch does not
perform it.

The smallest useful canonical slice would be:

1. define a common artifact semantic-acceptance contract;
2. add machine-addressable semantic obligations to a small number of artifact
   skills/contracts;
3. add generated semantic-evaluation evidence;
4. gate managed-artifact semantic claims on accepted evaluation;
5. make Engineering Coverage consume only accepted claims;
6. add defect-injection acceptance tests equivalent to this experiment.

Do not canonicalize a universal semantic ontology.

Start with existing structured artifact kinds and expand only from repeated
consumer evidence.

## Completion assessment

Research question: answered.

Defect-injection experiment: completed.

Representative artifact types: completed.

Coverage-gating hypothesis: confirmed in executable prototype.

Core-change hypothesis: rejected; no Core expansion demonstrated.

Unresolved blocking design question: none.

## Final conclusion

Semantic completeness and Engineering Coverage are related but independent
closures:

```text
artifact semantic completeness
= required artifact obligations - missing obligations

engineering coverage completeness
= activated engineering concerns - unresolved/uncovered concerns
```

Semantic correctness is a separate justification relation over material
assertions:

```text
assertion
-> valid provenance or owning-Authority decision
-> no applicable contradiction
-> deterministic invariants pass
-> semantic review passes where deterministic proof is impossible
```

The resulting invariant for Harness should be:

> A semantic claim is usable as Engineering Coverage proof only when a current
> artifact realization has successfully passed the semantic acceptance contract
> responsible for that claim.

The research is complete enough to proceed to a deliberate canonicalization
decision in a separate step. No changes from this research branch should be
merged into `main` automatically.
