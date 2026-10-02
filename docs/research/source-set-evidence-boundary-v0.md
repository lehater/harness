# Source-set / evidence-boundary completeness v0

Status: completed bounded-assurance proof; open-world evidence completeness is explicitly not claimed.

## Question

The preceding source-boundary work proves that no text disappears **inside one
selected immutable source artifact**.

That still leaves a more external failure:

```text
relevant evidence artifact / channel
        |
        X  never selected
        |
selected source baseline
        |
        v
source.boundary passes for every selected file
```

The question is:

> Can Harness prove that the selected evidence set itself is complete?

## Fundamental limit

Not in the open world.

No finite validator can prove that there is no unknown interview, document,
repository, stakeholder, external standard or other evidence source that should
have been consulted unless the acquisition universe has already been bounded by
an accepted scope.

Therefore two different claims must not be conflated:

```text
absolute evidence completeness
    impossible to prove generically

completeness relative to an accepted acquisition scope
    deterministically checkable
```

This is the same distinction that exists elsewhere in Harness between semantic
authority and deterministic enforcement of an already accepted contract.

## Minimal source-set contract

A small assurance-only validator was added:

`harness.evidence.source_set`.

Scenario driver:

`source.set`.

The validator consumes two documents:

1. a `harness-source-set-contract`, which declares arbitrary task/project-owned
   evidence channel ids and a minimum item count for each;
2. a `harness-source-set` inventory, which records whether each required
   channel was reviewed and which immutable source references were included.

Harness does not define a global taxonomy of evidence channels.

A contract may use ids such as:

- `problem-evidence`;
- `user-needs`;
- `product-requirements`;

or completely different project-native ids.

The validator checks only contract-relative closure:

- every required channel is represented;
- no required channel remains `QUESTION`;
- each channel satisfies its minimum source-item count;
- one source reference is not silently counted twice;
- the inventory is bound to the expected contract id.

It does not decide whether the contract itself contains the right channels.

## Real NAPMS proof

Pinned project:

`lehater/napms@42481577fab7f795cf3a2118b7b6f1c3c075d066`.

NAPMS already owns the canonical chain:

```text
FIRST-MVP-HCD-PROBLEM-EVIDENCE
        ->
FIRST-MVP-HCD-USER-NEEDS
        ->
FIRST-MVP-REQUIREMENTS
```

The project canonical graph records the same dependencies.

The proof therefore uses a task-specific acquisition contract with three
required channels:

- `problem-evidence`;
- `user-needs`;
- `product-requirements`.

Scenario:

`spec/scenario-suite/scenarios/source-set-evidence-boundary.yaml`.

### Missing channel

The inventory contains pinned problem evidence and product requirements but no
user-needs channel.

Result:

```text
status = REJECTED
finding = SOURCE_CHANNEL_MISSING
channel = user-needs
```

This failure is invisible to per-file `source.boundary`: every selected file
could be losslessly processed and the source set would still be semantically
incomplete relative to the accepted acquisition scope.

### Unresolved channel

The user-needs channel exists but remains `QUESTION` with no source item.

Result:

```text
status = REJECTED
findings:
  SOURCE_CHANNEL_QUESTION
  SOURCE_CHANNEL_UNDERSATISFIED
```

Uncertainty therefore cannot be converted into a false green source baseline.

### Complete declared set

All three required channels are COMPLETE and contain pinned source references.

Result:

```text
status = ACCEPTED
required_channel_count = 3
reviewed_channel_count = 3
findings = []
```

## Where the acquisition contract comes from

The validator does not invent acquisition scope.

Preferred sources for the contract, in order, are:

1. a project-owned canonical dependency/evidence graph when one already exists;
2. an accepted artifact-skill read boundary or experiment/reconstruction
   protocol that explicitly names required evidence classes;
3. a task-specific acquisition contract accepted by the Authority/research owner
   responsible for the source boundary.

For the NAPMS proof, the project-owned canonical graph already establishes the
problem-evidence -> user-needs -> requirements dependency chain, so the
three-channel contract is not an evaluator invention.

If no accepted source defines the evidence universe, that is not a validator
error. It is an unresolved acquisition-scope decision and must remain explicit.

## Resulting source assurance chain

The complete source-side chain is now:

```text
problem / reconstruction scope
        |
        v
acquisition contract admission                    semantic / Authority decision
        |
        v
source-set coverage against that contract         deterministic
        |
        v
selected immutable source artifacts
        |
        v
lossless source boundary per artifact             deterministic
        |
        v
covered source unit -> meaningful statements      local semantic review
        |
        v
statement disposition coverage                    deterministic
        |
        v
statement -> semantic atoms                       local semantic review
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

The model deliberately alternates accepted semantic boundaries with
deterministic enforcement.

## What is now closed

Relative to an **accepted acquisition contract**, Harness can now prevent:

- omission of an entire required evidence channel;
- unresolved source acquisition being treated as complete;
- omission of raw text inside a selected artifact;
- omission of meaningful statements inside a covered source unit;
- loss/weakening while admitting statements into semantic atoms;
- omission of consumed atoms downstream;
- unreviewed truth claims in declared semantic links.

## What remains genuinely open

The remaining outer question is not another coverage algorithm:

> Is the acquisition contract itself sufficient for the actual problem?

For an existing project, this may be answered by an accepted project-owned
canonical dependency/evidence graph.

For a new idea, interview/research effort or open-world investigation, it is a
research-design / Authority judgement. New evidence can always reopen it.

Therefore Harness must not expose a global `ALL_EVIDENCE_COMPLETE` claim.

The strongest valid claim is:

```text
SOURCE_SET_COMPLETE
relative_to = <accepted acquisition contract>
```

If the acquisition contract changes, source-set completeness must be recomputed.

## Research closure

The complete source-to-downstream trust-boundary investigation is closed in
`docs/research/source-to-derivation-assurance-closure-v1.md`.

The remaining acquisition-contract sufficiency question is deliberately treated
as the outer semantic/Authority boundary rather than another deterministic
coverage layer. New evidence may reopen that boundary; Harness does not claim
open-world omniscience.

## Architecture consequence

The new validator remains assurance above Core.

No Core Authority, CanonicalArtifact type, workflow state, universal evidence
ontology, source-channel registry, semantic DSL, scorer or provider registry is
introduced.

The only reusable machine concept is contract-relative coverage over arbitrary
project-owned channel ids.
