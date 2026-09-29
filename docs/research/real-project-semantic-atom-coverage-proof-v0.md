# Real-project semantic atom coverage proof v0

Status: completed; existing semantic-derivation atom accounting was validated on real NAPMS verification omissions and compared with whole-oracle live judgement.

## Question

Can Harness make semantic omission detection less dependent on a live LLM by
decomposing a consumed upstream Capability surface into explicit semantic atoms
and accounting for each atom separately?

The preceding verification-oracle audit established a difficult failure class:
a downstream verification scenario can list a requirement in `verifies` while
its observable `expect` text omits mandatory requirement semantics. On the
focused paragraph-level corpus the live evaluator detected only half of those
omissions per run and changed verdict on two cases even when both runs resolved
to the same observed model.

## Existing mechanism was sufficient

No new semantic-atom framework was required.

`semantic_derivation.py` already treats accepted upstream
`semantic_assertions` as individually addressable semantic atoms and requires
each applicable source assertion to be either:

- covered by an explicit derivation link; or
- explicitly dispositioned.

A required source assertion with neither becomes
`UNDISPOSITIONED_SOURCE`.

The experiment therefore used the existing model rather than adding a new Core
entity, ontology or DSL.

## Real-project proof

Pinned project:

`lehater/napms@42481577fab7f795cf3a2118b7b6f1c3c075d066`.

Direct Capability edge:

```text
engineering.requirements.acceptance
        ->
engineering.verification.acceptance-scenarios
```

Scenario:

`spec/scenario-suite/scenarios/real-project-semantic-atom-coverage.yaml`.

Eight expert-reviewed requirement atoms were extracted from the already audited
canonical requirements:

- four atoms with direct verification counterparts;
- four atoms corresponding to the known Verification Design omission defects.

The four omitted atoms are:

1. first Allowed materialization starts the Rule ACTIVE;
2. each Endpoint has at most one current host/prefix address realization;
3. organizational responsibility is not an authorization scope;
4. effective conditions determine contribution at evaluation time without
   periodic stored ACTIVE/INACTIVE rewriting.

With honest derivation evidence only the four actually represented atoms are
linked.

Deterministic result:

```text
required = 8
covered = 4
unresolved = 4
```

Harness localizes all four missing atoms as
`UNDISPOSITIONED_SOURCE` owned by `VERIFICATION-DESIGN`.

No live semantic evaluator is needed for this absence check.

## Important boundary: a link can lie

The same scenario deliberately adds four false derivation links from the
missing source atoms to nearby but semantically insufficient verification
atoms.

Without semantic judgement, structural accounting becomes complete:

```text
required = 8
covered = 8
unresolved = 0
status = ACCEPTED
```

This is expected. Deterministic coverage proves that a link was declared, not
that arbitrary natural-language meanings are actually equivalent.

When the existing request-bound `semantic_judgement` contract is enabled,
those same false links require review and the expert rejection is bound to the
exact source atoms, target atoms and links.

The useful split is therefore:

```text
missing link / missing disposition
        -> deterministic Harness check

truth of a proposed semantic link
        -> narrow semantic judgement
```

Atomization removes the LLM from omission discovery when evidence is honestly
constructed; it does not make false semantic mappings deterministically
provable.

## Atomic live calibration

Corpus:

`spec/semantic-derivation/real-project-atomic-link-calibration-v1.yaml`.

Scenario:

`spec/scenario-suite/scenarios/real-project-atomic-link-calibration.yaml`.

The corpus contains eight real NAPMS atom-sized link claims:

- four valid source-atom -> target-atom links;
- four invalid nearest-target links corresponding to the same omission defects.

The negative wording is not a synthetic mutation. Each target is semantic
content actually present in the pinned Verification Design but insufficient for
the selected source atom.

### Baseline: whole-oracle omission task

The preceding focused paragraph-level probe
(`verification-oracle-partial-loss-v1`) produced, on two complete
`mai-code-1.1-flash` runs:

- TP=2, TN=4, FN=2, FP=0;
- detection recall=`0.5`;
- false-positive rate=`0.0`;
- two omission cases changed verdict across the runs.

See workflow `36516544966` and
`docs/research/verification-oracle-partial-loss-audit-v0.md`.

### Atomic task: workflow 36517967477

Corpus fingerprint:

`LCCORPUS-73a962918e4105467984a5aacad408035f41f5dd902894a15986822bee95f92a`.

Attempt 1:

- run 1 resolved to `mai-code-1.1-flash`;
- TP=4, TN=4, FN=0, FP=0;
- accuracy=`1.0`;
- detection recall=`1.0`;
- false-positive rate=`0.0`;
- run 2 failed before scoring because the provider violated the versioned
  response envelope.

Artifact `11011478044`,
digest
`sha256:4fa290c73391cc30f7eea907b44814d8aae9fce4355cc226d09636033e735d4b`.

Attempt 2 produced two complete runs.

Run 1:

- resolved model: `mai-code-1.1-flash`;
- TP=4, TN=4, FN=0, FP=0;
- accuracy=`1.0`;
- detection recall=`1.0`;
- false-positive rate=`0.0`.

Run 2:

- resolved model: `gpt-6-luna`;
- TP=4, TN=3, FN=0, FP=1;
- accuracy=`0.875`;
- detection recall=`1.0`;
- false-positive rate=`0.25`;
- sole miss: valid `atomic-no-heavy-async` was rejected.

Artifact `11011428276`,
digest
`sha256:646f608211516bd94fc3071f7f0f61885c7cd3f6c1645c4378e08efc9ac5167f`.

The attempt-2 stability result is `UNSTABLE` only because the valid
`atomic-no-heavy-async` control changed verdict while `model:auto` routed
the two runs to different observed models.

Most importantly, all four atomic missing-link cases were detected in every
scorable atomic execution:

- `mai-code-1.1-flash` attempt 1: 4/4;
- `mai-code-1.1-flash` attempt 2: 4/4;
- `gpt-6-luna` attempt 2: 4/4.

## Interpretation

The experiment supports the hypothesis that task formulation materially affects
semantic-evaluator quality.

For the same four underlying real omissions:

```text
whole verification oracle vs requirement
    omission recall per complete run = 0.50

one source atom vs one candidate target atom
    omission recall per scorable run = 1.00
```

This small corpus is not a statistical estimate of universal model quality, but
the controlled contrast is strong enough to reject the idea that evaluator
variation is only a question of one model being globally "smarter" than
another.

The judgement task itself matters.

Whole-artifact omission detection asks the evaluator to:

1. decompose the source;
2. decide which source semantics matter downstream;
3. decompose the target;
4. align meanings;
5. notice what is absent;
6. decide materiality.

Atomic link judgement asks mainly:

1. compare one source claim with one target claim;
2. decide whether the declared relation is semantically justified.

The second task removes several inference steps.

## Resulting testing model

For semantic derivation testing, the preferred evidence shape is now:

```text
canonical upstream knowledge
        |
        v
accepted source semantic atoms
        |
        v
deterministic consumed-atom accounting
        |
        +-- no link/disposition -> deterministic omission defect
        |
        v
explicit source-atom -> target-atom links
        |
        v
semantic review only where link truth is not structurally provable
```

This is a refinement in how the already implemented derivation mechanism should
be used, not a new framework.

## Remaining trust boundary

The experiment does not prove that semantic atom extraction is automatically
complete or correct.

If an upstream canonical statement contains two mandatory meanings but the
accepted semantic surface extracts only one, deterministic downstream coverage
cannot detect the omitted atom because the atom never entered the derivation
contract.

Likewise, target-atom extraction must faithfully represent the canonical target
artifact.

Therefore the next unresolved problem is **semantic-surface extraction and
admission quality**, not another derivation engine:

- how source atoms are derived from canonical knowledge;
- how completeness of that extraction is reviewed;
- how atom provenance remains bound to the canonical source;
- when extraction can be deterministic and when it requires expert judgement.

No Core, scorer, provider registry, consensus mechanism or new orchestration
framework is justified by the current evidence.
