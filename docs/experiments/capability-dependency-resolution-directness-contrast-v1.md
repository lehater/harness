# Capability Dependency Resolution — directness contrast and source-echo audit v1

Date: 2026-10-08
Status: **experimental control prepared; no actual neutral-contrast Copilot result yet**
Branch: `experiment/capability-dependency-resolution-v1` (PR #220, Draft)
Disposable execution branch: `experiment/cdr-live-run`
Immutable source: `lehater/prep@c52ff8ec1a4732285b2b299bf11dca9869fb2fee`
No PREP or `harness/main` changes.

## Motivating observation

Two oracle-free source-bound real PREP Copilot attempts
([GitHub Actions run 37804487025](https://github.com/lehater/harness/actions/runs/37804487025))
produced identical direct-provider sets for both Tactical Domain targets:

- KEEP `prep.model-context-strategy`
- KEEP `prep.product-capabilities`
- ADD `prep.domain-strategy`, for review only
- no proposed removal

They differed on whether `REQ-CAP-EXPLORE-PERSPECTIVES` is directly consumed
by the current-information tactical domain model (4 vs 3 product direct
requirements). Full accepted-target-obligation coverage and independent
semantic correctness were not established.

Crucially, the source-bound generator included the accepted `DS-01` and
`DS-02` strategic source sections as explicit **target obligations** while
also listing `prep.domain-strategy` as the supplier of the same source
statements. A model can easily cite the inserted section back to its source.
That is a valid structural reference, **not evidence that direct access to the
strategic supplier is necessary**.

Moreover, the accepted PREP Engineering Graph already has
`prep.model-context-strategy -> prep.domain-strategy`. Existing transitive
access is relevant context, but a transitive path does not by itself prove
that a direct Tactical Domain prerequisite is redundant.

## Source-aware preliminary necessity review (not independent certification)

The accepted PREP `docs/architecture/context-map.md` explicitly assigns
strategic responsibility selection to Domain Strategy; its **Consumers**
section says Model Context Strategy consumes the strategic responsibilities
to choose model languages, while Tactical Domain Design consumes the
*model-context decisions that refine those responsibilities*.

The accepted `docs/architecture/model-context-map.md` then defines
MC-01/MC-02 scope and TR-01's cross-context constraints and states that
Tactical Domain Design defines concepts, relationships and invariants
**inside those accepted model contexts**. This corresponds to the existing
`Tactical -> Model Context -> Domain Strategy` dependency path.

**Provisional finding:** No unique tactical semantic constraint from Domain
Strategy has yet been demonstrated that must be read directly *in addition
to* the accepted Model Context contract. The two new direct DS dependencies
should therefore be treated as **unsupported for adoption**, even though
their contextual relevance is undisputed. This is not a proof they are
redundant in every possible design, and the accepted PREP graph should not
be changed based solely on this argument.

The neutral contrast is intended to investigate whether the model's DS
preference persists **without** the obvious source echo. It cannot
substitute for an authoritative direct-consumption necessity decision.

## New Phase B directness confound audit

`evals/project_discovery_directness.py` audits every model-proposed **new**
direct edge after the provider returns, when the exact pinned graph is known.

For each proposed ADD it reports:
- which cited target obligation sections came directly from that provider
  (`source_echo_obligations`);
- which proposed need citations were *not* that provider's own copied section
  (`non_echo_obligations`);
- existing transitive paths through retained immediate suppliers, if any;
- an explicit `DIRECTNESS_UNPROVEN` status and independent-review requirement.

It detects source echo and pre-existing graph reachability; **it never claims
to test semantic entailment, completeness or causal necessity**. Even an
unconfounded non-echo citation is still a model hypothesis.
`ADD_PROMOTION_ALLOWED=false` and `automatic_writeback_allowed=false`
remain hard boundaries.

This information is surfaced as `ADD_DIRECTNESS_AUDIT` in Phase B. The
original `ADD` field continues to mean *the model's candidate suggestion*,
not an accepted change.

## Controlled neutral formulation

The pinned project source generator now supports an explicit opt-in
`--formulation NEUTRAL_CONTRAST`. It holds constant:
- the PREP Git SHA and clean-checkout verification;
- two exact real target Capability IDs and their production Authorities;
- the entire accepted Core-registered and semantically-reviewed provider
  catalog, semantic surface claim indices and review revisions;
- the explicit DS-to-Product-Requirement trace inventory;
- all 15 accepted Product Capability statements per target and the mandatory
  model coverage-assessment protocol;
- model request blinding of the original target `requires`.

Only the **target obligation formulation** changes.

Instead of inserting MC and DS upstream sections directly into the target
obligations, the operator supplies short target-output paraphrases of tactical
semantic meaning and invariants. The generator rejects duplicate/short
obligation IDs, references to provider Capability IDs and exact source-bound
obligation copies; the output obligations have **no source-provider backpointer**.

These paraphrases are labeled
`target_formulation_authority=EXPERIMENTAL_OPERATOR_PARAPHRASE_NOT_ACCEPTED`.
They are **not independently authorized requirements**, not a rewrite of PREP,
and not proven more accurate than the source-bound formulation. This is a
controlled ablation of the most obvious circular citation route, not a claim
of unbiased ground truth.

Operator paraphrases for Preparation Information cover current preparation
concepts/distinctions and meaningful relationships without fixing a taxonomy
or inferring learner state. For Recorded Activity History they cover retained
activity/result facts, time, historical references and meaning through later
information changes without learner-state conclusions.

## Decision logic after the contrast run

Compare the neutral-contrast provider set against **both** existing real
source-bound attempts (same PREP SHA, same accepted provider inventory) and
inspect the exact source claims/rationales.

| Result for `prep.domain-strategy` | Correct interpretation |
| --- | --- |
| Proposed only with DS sections copied into target obligations | Strong indication of source-echo sensitivity; no direct edge decision |
| Proposed with neutral obligations too | Candidate has some robustness to source-echo removal; directness STILL UNPROVEN |
| Proposed in neither formulation | Candidate absent under these prompts; does not prove the dependency unnecessary |
| Varies across neutral reruns | Evidence of formulation/run sensitivity, requiring review |

A direct-source claim must ultimately identify an independently required
Tactical Domain invariant that cannot be fully discharged by accepted Model
Context meaning already directly consumed, **without** relying purely on
transitive graph reachability or the source being quoted in target scope.
This judgment must be reviewed with the relevant Authority owner, not decided
by the model's own similarity rationale.

No change to the existing PREP edges is permitted. Even if the contrast
no longer suggests `prep.domain-strategy`, the two existing Product and
Model Context Strategy edges remain independently governed.

## Validation and execution

- Full-gate regression: `tests/test_dependency_resolution_directness.py`
  validates source-echo detection, kept-provider transitive path reporting,
  source-neutral evidence, and the non-promotion invariant.
- `tests/test_dependency_resolution_project_snapshot.py` checks that
  neutral target paraphrases remove source backpointers, preserve the
  original pinned source/provider/product inventory, reject missing
  contrast statements, and remain oracle-free.
- The disposable `experiment/cdr-live-run` workflow selects
  `--formulation NEUTRAL_CONTRAST` and saves its full generated context,
  model result rows and Phase B audit. GitHub Actions requires manual
  `workflow_dispatch` under Harness provider-evaluation policy.

**No new neutral contrast model observation should be claimed before the
workflow actually runs.** All prior findings remain the original source-bound
observations, preserved unmodified for comparison.
