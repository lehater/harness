# Source-to-derivation assurance closure v1

Status: completed research closure.

## Question

Can Harness provide a defensible assurance chain from selected raw source
evidence to downstream Capability derivation without pretending that an LLM or
deterministic validator can prove open-world semantic completeness?

## Answer

Yes, with one explicit boundary:

> completeness is always relative to an accepted acquisition scope.

Harness can deterministically enforce the consequences of that scope and can
localize semantic judgement to small review boundaries. It cannot prove that no
unknown evidence source exists outside the accepted acquisition contract.

That is a fundamental epistemic boundary, not a missing validator.

## Closed assurance chain

The completed chain is:

```text
problem / reconstruction scope
        |
        v
acquisition contract admission                    semantic / Authority decision
        |
        v
source-set coverage relative to contract          deterministic
        |
        v
selected immutable source artifacts
        |
        v
lossless source boundary                          deterministic
        |
        v
source-unit -> meaningful statements              local semantic review
        |
        v
statement disposition coverage                    deterministic
        |
        v
statement -> semantic atoms admission             local semantic review
        |
        v
accepted semantic surface
        |
        v
consumed-atom accounting                          deterministic
        |
        v
declared atom -> atom link truth                  narrow semantic review
        |
        v
downstream derivation coverage                    deterministic
```

The pattern intentionally alternates:

```text
accepted semantic boundary
        ->
deterministic enforcement
```

rather than asking one evaluator to infer everything at once.

## What each layer proves

### 1. Acquisition contract admission

Defines which evidence channels/classes belong to the selected problem scope.

Examples of acceptable basis:

- project-owned canonical dependency/evidence graph;
- accepted artifact-skill read boundary;
- reconstruction/experiment protocol;
- explicit Authority/research-owner decision.

This is the outer semantic boundary.

It does not produce a universal claim that every possible source in the world
has been discovered.

### 2. Source-set coverage

Validator:

`source_set.py`.

Proves, relative to the accepted acquisition contract:

- every required source channel was reviewed;
- unresolved channels remain blocking;
- minimum source-item requirements are satisfied;
- one source reference is not silently double-counted.

Valid claim:

```text
SOURCE_SET_COMPLETE
relative_to = <accepted acquisition contract>
```

Invalid claim:

```text
ALL_RELEVANT_EVIDENCE_IN_THE_WORLD_COMPLETE
```

### 3. Lossless source boundary

Validator:

`source_boundary.py`.

Proves that no line/item disappears inside one selected immutable source before
semantic review.

It is intentionally syntactic.

### 4. Statement enumeration

One bounded source unit is reviewed into independently meaningful statements.

This is a local semantic task.

Real NAPMS calibration showed:

- every tested statement-enumeration omission was detected by both scorable
  evaluator runs;
- evaluator false rejection of a complete enumeration remained possible.

Therefore the evaluator is evidence, not the oracle.

### 5. Statement disposition coverage

Validator:

`source_coverage.py`.

Proves that every enumerated source statement has exactly one explicit
disposition.

It does not prove the statement list itself was complete and does not prove an
ADMITTED rewrite preserved every material clause.

Those questions are handled by the adjacent boundaries.

### 6. Semantic-surface admission

One canonical statement is compared with the candidate semantic atoms extracted
from it.

Existing `semantic_acceptance.py` then deterministically rejects:

- missing required atoms;
- weakened machine-addressable values;
- wrong source/Authority direction.

Two independent scorable GPT-6 Luna sessions on the current extraction corpus
matched the expert oracle 8/8.

That is repeat evidence, not a universal model-quality claim.

### 7. Consumed-atom accounting

Existing `semantic_derivation.py` proves that every applicable accepted source
atom is either:

- linked to downstream semantics; or
- explicitly dispositioned.

Missing source semantics become deterministic
`UNDISPOSITIONED_SOURCE` findings.

### 8. Atom-link truth

A declared source-atom -> target-atom relation may still be false.

That truth boundary remains semantic, but the task is now narrow:

```text
one source atom
        vs
one target atom
        under
one declared relation
```

On the real NAPMS omission corpus, reducing whole-artifact judgement to atomic
link judgement raised omission detection from 0.50 per whole-oracle run to 1.00
in every scorable atomic run.

The model still produced an occasional false positive on a valid control, so it
remains a calibrated detector.

### 9. Downstream derivation coverage

Once accepted atoms and reviewed links exist, downstream semantic omission
coverage is deterministic.

This is the original Capability Derivation Testing objective.

## Main empirical result

The investigation moved the difficult question from:

```text
"Read two large artifacts and tell me whether any meaning was lost."
```

to:

```text
1. Which source units/statements/atoms are in scope?
2. Is every accepted atom accounted for?
3. Is this one proposed atom-link semantically justified?
```

The first and second questions are mostly deterministic after admission.
Only the local semantic boundaries require judgement.

That is the major practical result.

## Real defects found during the research

The method found real canonical NAPMS defects, including:

- request-authority scope drift:
  source-only authority became source+destination authority in Security
  Architecture;
- application materialization partial loss:
  INCOMPLETE policy rows lost explicit non-deployable semantics;
- several Verification Design cases where `verifies: [REQ-X]` existed but the
  executable/observable oracle omitted mandatory requirement semantics.

Therefore the method was not validated only against synthetic mutations.

## Structural traceability result

A key result is:

```text
declared traceability
    !=
semantic coverage
```

Examples:

- a requirement id can appear in `verifies` while mandatory semantics are not
  checked;
- an artifact can depend on another artifact while one consumed semantic atom is
  lost;
- a selected source set can be internally lossless while a required evidence
  channel was never selected.

Each layer needs the assurance appropriate to its own boundary.

## Evaluator result

The evaluator must not define correctness.

Observed behavior across the research:

- explicit contradiction / constraint drift: generally strong;
- whole-artifact omission detection: materially weaker;
- same observed model can change verdict across fresh sessions;
- atomic link judgement performs substantially better on the tested omission
  class;
- provider output protocol remains operationally unreliable at times;
- GPT-6 Luna is the repository cost baseline, but current GitHub Actions identity
  cannot explicitly pin it and may only reach it through `auto` research
  fallback.

Therefore:

```text
canonical / expert-reviewed semantics = oracle
deterministic Harness checks          = accounting/enforcement
LLM evaluator                         = calibrated semantic detector
```

No consensus/majority mechanism changes that authority model.

## Why the trust-boundary search stops here

One could ask another question:

> Who proved that the acquisition contract itself included every possible
> evidence channel?

In an open world, that question has no finite deterministic closure.

Any answer would require another prior evidence universe, producing an infinite
regress.

The valid engineering response is to bind completeness claims to an explicit
accepted scope and make new evidence capable of reopening that scope.

Therefore the stop condition is:

```text
accepted acquisition contract
        +
contract-relative deterministic closure
        +
explicit reopen-on-new-evidence semantics
```

not a global claim of omniscience.

## Reopening rule

Source assurance is not permanent.

Reevaluate affected source and derivation closure when:

- acquisition scope changes;
- a new required evidence channel is accepted;
- a new source artifact appears in a required channel;
- an immutable source revision changes;
- source statement/atom admission is revised;
- upstream canonical semantics change.

The existing capability lifecycle/currentness model remains the downstream
mechanism; no separate global source-workflow state is needed.

## Architecture conclusion

The research does **not** justify:

- a new Core Source entity;
- a universal Evidence ontology;
- a fixed global channel registry;
- a workflow/status engine;
- a universal semantic DSL;
- LLM consensus;
- a second canonical truth graph.

The reusable assurance mechanisms are sufficient:

- `source_set.py`;
- `source_boundary.py`;
- `source_coverage.py`;
- semantic acceptance;
- semantic derivation;
- request-bound semantic judgement;
- calibration/evidence scenarios.

Project-owned graphs, skills and protocols define the acquisition scope.

## Research closure

The original question was whether Harness can test whether design derivations
are semantically correct and complete.

The answer is now more precise:

> Harness can test semantic derivation completeness relative to an explicitly
> admitted source/evidence scope, and can reduce most omission detection to
> deterministic accounting over accepted semantic atoms. Semantic judgement
> remains only at small admission/link boundaries and is calibrated rather than
> treated as authoritative.

Further work should now be adoption/scale work, not another abstract
trust-boundary layer.

Useful next directions are:

- apply the complete assurance chain to additional real projects/slices;
- automate source-set contract derivation from existing project-owned graphs
  when repeated evidence justifies it;
- expand expert-reviewed atom/link corpora across more defect classes;
- improve provider protocol reliability separately from semantic assurance.
