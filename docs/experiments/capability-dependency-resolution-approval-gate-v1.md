# CDR decision governance — review-only evidence gate v1

Status: **experimental, unpromoted, nonauthorizing**
Context: Harness PR #220 (Draft), PREP pinned at `c52ff8ec1a4732285b2b299bf11dca9869fb2fee`

## Why automatic adoption is blocked

Harness's canonical decision protocol distinguishes *accepted* from
*proposal*, *hypothesis*, *unknown* and *conflict*. Tactical DDD requires
one accountable semantic owner per invariant. Consequently an evaluator
that cites a reviewed source cannot by itself decide which *target-owned*
obligation is accepted or whether an apparent provider is **directly**
necessary rather than fully mediated by an existing immediate provider.

The current PREP target Capabilities are Engineering Graph productions
without independently accepted target Core artifacts and target-specific
semantic revisions. The v2 six-output/two-constraint description is an
operator-authored proposal, not a project source of acceptance.

## New nonauthorizing gate

The operational CDR sequence is:

```text
Pinned project/Core/baseline/Engineering Graph
    + draft owned output obligations/constraints
           |
           v
    cdr-prepare  -- label-blinded, source-accepted providers only
           |
           v
    external evaluator (separate execution; source citations required)
           |
           v
    cdr-reconcile -- evidence checks, ADD/KEEP and independent-review questions
           |
           v
    cdr-dossier   -- target-own-contract readiness + immutable source references
           |
           v
    cdr-check-review -- regenerate dossier from exact pinned source
                        + validate completeness of an operator review draft
           |
           v
    DRAFT_COMPLETE_FOR_AUTHORITY_CONSIDERATION, never graph mutation
```

Five tests are required *for each proposed added direct provider*:

1. `INDEPENDENT_TARGET_OUTPUT_OBLIGATION`: the target really owns and
   separately accepts the obligation, rather than having copied supplier text.
2. `MATERIAL_ACCEPTED_RULE_CONSUMPTION`: an exact accepted provider
   rule or invariant materially affects that target output.
3. `INTERMEDIATE_CONTRACT_SUFFICIENCY`: determine whether retained
   direct providers already completely supply that semantic rule.
4. `DIRECT_PROVIDER_CHANGE_SENSITIVITY`: identify a change in the
   candidate direct provider that requires target reconsideration *while
   the retained immediate suppliers' public contracts remain unchanged*.
5. `AUTHORITY_REVIEW_AND_REVISION`: independent Authority ownership,
   actual source review revision, and a governance-valid reviewer decision.

These are evidence questions, not conditions a text validator can
prove true. Existing source claims, copied clauses, graph reachability,
and reviewer role strings cannot self-authorize adoption.

The code generates `harness-cdr-governance-decision-dossier` with every
output obligation, its claimed accepted source rules, governing constraints,
target-own Core/baseline readiness blockers, proposed ADD directness
review tests and current KEEP/unknown existing edges.

It is bound by a SHA256 digest for consistency. **A digest is not a signature**:
the actual command `cdr-check-review` therefore re-creates the complete
dossier against the exact clean pinned project and accepted source files,
rather than trusting a submitted packet + matching user-recomputed hash.

The review draft format `harness-cdr-independent-review-draft` requires:
- matching dossier digest, source Git commit and target Capability;
- every output obligation accounted for with a substantive rationale;
- every suggested direct supplier accounted for with all five tests,
  evidence and a proposed interpretation;
- explicit `status=PROPOSED_NOT_ACCEPTED`, and
  `automatic_writeback_allowed=false`.

A passing review draft **does not** establish independent reviewer
identity, semantic necessity, adoption eligibility, or permission
to update `.harness/engineering-graph.yaml`.

## Operator commands

After an existing `cdr-prepare` and separately evaluated
`cdr-reconcile` prediction:

```sh
make cdr-dossier PROJECT_ROOT=/path/to/project PROJECT_COMMIT=<sha> \
  CDR_INTAKE=/path/to/intake.yaml CDR_PREDICTIONS=/path/to/predictions.json \
  CDR_OUTPUT=/tmp/cdr-dossier.json

make cdr-check-review PROJECT_ROOT=/path/to/project PROJECT_COMMIT=<sha> \
  CDR_INTAKE=/path/to/intake.yaml CDR_PREDICTIONS=/path/to/predictions.json \
  CDR_DOSSIER=/tmp/cdr-dossier.json CDR_REVIEW=/path/to/operator-draft-review.yaml \
  CDR_OUTPUT=/tmp/cdr-review-consistency.json
```

Both are *explicit* commands and read the project snapshot; neither
writes any project files. They use real source paths, not merely a
claimed Git revision in an untrusted YAML proposal.

## Remaining production admission decisions

The following cannot be bypassed mechanically:

- Accept the target's **own** output contract through its proper
  project's normal semantic governance, independently of CDR prompts.
- Verify one semantic owner per invariant and review the accepted
  cross-context boundary where outputs consume the same rule.
- Establish a trusted, project-governed reviewer identity and
  acceptance event, and bind it to current target and provider revisions.
- Define canonical Engineering Graph update authority, changeset
  verification and rollback semantics, **separately** from operator
  review drafts and LLM output.
- Validate dependency change impacts against existing accepted
  downstream contracts; missing edges cannot be inferred solely
  from graph reachability.

Until these exist, CDR's outputs are `REVIEW_REQUIRED` /
`DRAFT_COMPLETE_FOR_AUTHORITY_CONSIDERATION`. Source-reference
verification, local review-draft consistency, and passing Harness CI
do not discharge the semantic gate.

## Test coverage

The full-gate no-network test builds a pinned synthetic project,
blinds existing graph edges from the evaluator, creates a review
dossier, verifies all five questions for each proposed ADD,
rejects missing obligations and a forged approval conclusion,
and exercises `cdr-dossier` and `cdr-check-review` Make targets.
The latter command independently regenerates project-backed evidence
before checking the supplied review.

No PREP or `harness/main` mutation; PR #220 stays Draft.
