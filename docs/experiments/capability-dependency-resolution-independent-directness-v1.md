# Capability Dependency Resolution — independent direct-necessity criterion v1

Date: 2026-10-08
Status: **review protocol and evidence packet implemented; no independent acceptance decision yet**
Repo: `lehater/harness`, experiment PR #220 (Draft)
Project reference: `lehater/prep@c52ff8ec1a4732285b2b299bf11dca9869fb2fee`
Scope: experimental read-only diagnosis; no route or graph writeback.

## Criterion: what is a direct dependency?

For target Capability T, provider P and specific target output obligation O,
`T requires P` is a warranted **direct** semantic prerequisite only if
the owner-reviewed target contract establishes all of the following:

1. **Independent target output**: O is an accepted, uniquely identifiable
   obligation of T, approved by its owning Authority **independently of any
   excerpt from P**. Repeating a statement from P as the definition of O
   is not adequate evidence; neither is an unaccepted agent or operator
   paraphrase. The independent accepted target scope and immutable project
   revision must be recorded.
2. **Material rule consumption**: P owns an accepted, cited semantic
   rule/invariant whose application genuinely constrains O's correct output,
   rather than merely sharing a topic, carrying an optional intent, or
   describing logging, presentation or transport.
3. **Alternative semantic sufficiency**: Evaluate every already-retained
   direct source that could supply the same rule (including its exact
   accepted public interface and available source claims). Would O remain
   fully specified by accepted immediately consumed contracts if the
   proposed *direct* P edge were omitted? A graph path to P establishes
   only reachability, **not** semantic sufficiency; absence of a path
   establishes neither independence nor necessity.
4. **Independent change sensitivity**: A reviewer can point to a concrete
   plausible future change to P's governed semantic rule that would require
   T's output to change **while the accepted public contracts of its
   immediate retained providers remain unchanged**. If that cannot be
   distinguished from a change already fully mediated by an accepted
   intermediate contract, directness is not established.
5. **Authority adjudication**: The relevant target-semantic Authority
   confirms the obligation, source ownership, alternative analysis and
   change impact against a pinned project revision. The evaluator's own
   explanation, syntactically valid citations or repeated agreement are not
   independent adjudication.

These are **cumulative questions**, not a guaranteed algorithm for semantic
truth. Multiple immediate providers of one obligation are legitimate if each
supplies a separately indispensable semantic rule. A model can propose an
edge when evidence is incomplete, but it may not autonomously certify or
publish it. The independent review may record `DIRECT_REQUIRED`,
`INHERITED_SUFFICIENT`, `NOT_DIRECT`, or `INDETERMINATE`.
"Unknown" is preferable to speculative graph simplification.

## Implementation

- `evals.project_discovery_directness.audit_additions`: existing read-only
  structural signals for source-text echo and graph paths via already-kept
  direct providers. Neither implies necessity or redundancy.
- **New** `evals.project_discovery_directness_review.review_packets`:
  produces per-ADD case-bound packets during Phase B **after the blind
  provider response**. Each packet retains:
  - specific target obligation, source provenance and its exact statement;
  - the model-cited candidate provider claim with claim index, source path,
    content digest and semantic review revision when available;
  - alternate model-cited retained-direct-provider claims for the *same*
    obligation, with "sufficiency UNDETERMINED";
  - the accepted graph's transitive paths, explicitly structural only;
  - all five reviewer questions, unfilled and defaulting to
    `AWAITING_INDEPENDENT_ADJUDICATION`;
  - `semantic_entailment_verified=false`,
    `automatic_writeback_allowed=false`.
- **New** `validate_review_record`: a non-authorizing format/consistency
  check for future externally obtained Authority review. It requires
  exact case, provider and project-commit matching; independent target
  approval and reviewer attestation; complete reasoned responses to
  all five tests. It blocks source-echo or operator-only target
  formulations rather than allowing self-attested acceptance. Even a
  structurally complete record receives only
  `RECORDED_FOR_GOVERNANCE_REVIEW` and
  `graph_mutation_authorized=false`.

All packets are attached to read-only reconciliation as
`ADD_DIRECTNESS_REVIEW_PACKETS`. The accepted PREP snapshot, current
graph's `requires`, reviewer packet and human findings must **not**
be inserted into the evaluated agent's blind Phase A request.

## What can be said about PREP Domain Strategy today?

The two preceding source-bound runs proposed a direct edge from each Tactical
Domain model to `prep.domain-strategy`, but their target obligation text
incorporated DS-01/DS-02 from that same provider. In the neutral contrast
[run #37807128717](https://github.com/lehater/harness/actions/runs/37807128717),
with otherwise unchanged accepted provider catalog and product requirement
inventory, neither of those two edges was proposed.

The existing accepted PREP Graph exposes
`Tactical Domain -> Model Context Strategy -> Domain Strategy`. The
accepted Domain Strategy document's "Consumers" section identifies
Model Context Strategy as consumer of the strategic responsibilities,
and Tactical Domain Design as consumer of refined model-context decisions.
Model Context Strategy's "Consumers" likewise directs Tactical Domain
Design to concepts, relationships and invariants inside accepted contexts.

No unique direct Domain Strategy rule that bypasses those accepted Model
Context meanings has yet been established for either tactical output.
Therefore **the two proposed ADD edges must not be adopted** on current
evidence. That does not prove that direct reliance is universally forbidden;
a future independently accepted tactical obligation could expose a unique
strategic dependency not currently represented in the intermediary contract.
The correct epistemic status for those additions is
`DIRECTNESS_UNPROVEN`.

The existing `prep.model-context-strategy` and
`prep.product-capabilities` direct edges remain intact. The separate
question of whether `REQ-CAP-EXPLORE-PERSPECTIVES` is direct to the
current information model remains unsettled; it varied across runs.

## Safety and next gate

The proof burden is intentionally asymmetric: a graph proposal can be
recorded on incomplete evidence, but neither **ADD** nor **REMOVE** is
approved by model similarity, topology reachability, synthetic oracle
agreement, generated rationales or deterministic reference validation.
This experiment includes no production writeback interface.

Next: identify an independently accepted target-output contract and a
reviewer authorized for its semantic Authority; adjudicate the existing
Domain Strategy proposal against accepted Model Context public semantics
and a concrete change-sensitivity case. Until then the review packets
remain unanswered and the PR remains Draft.
