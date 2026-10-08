# CDR atomic public semantic contract v1 — experimental source-first study

Status: **RESEARCH_DRAFT_NOT_AUTHORITY_ACCEPTED**. This work is not a new canonical Harness Knowledge kind, a change to PREP, or a new project-wide requirement. It is an intermediate, explicitly unpromoted way to make claimed semantic ownership reviewable, reusable and evidence-bound.

## Problem

The accepted and reviewed PREP `docs/domain/knowledge-model.md` contains two materially different claims in a single section:

1. Knowledge Model owns the `KnowledgeProposition` representation of a relational subject assertion.
2. It explicitly names **`docs/domain/relation-classification-catalog.yaml`** as the provider of the reusable predicate vocabulary and classifier.

With raw extracted paragraphs and with human-selected source sections, Copilot repeatedly treated the second claim as evidence that Knowledge Model itself provides the target's classifier. A genuine downstream producer can also own *different* independent knowledge; explicit delegation does not mean everything in its source is non-normative. The same source document can express both kinds.

## Atomic contract record

`spec/dependency-resolution/project-pilots/prep-public-semantic-contract-draft-v1.yaml` describes eight Core-registered PREP provider Capabilities with source-bounded atomic claims. Each entry has a unique ID, exact unmodified source quote and section/YAML field/accepted requirement anchor; role:

- `OWNED_EXPORT_CANDIDATE`: the source may own and publish this particular meaning, subject to Authority review.
- `DELEGATED_EXPORT_REFERENCE`: this source explicitly identifies another Capability and source artifact as an exporter of a different meaning. This is **not an edge** and does not imply the referring source lacks its own distinct exports.
- `CONTEXT_ONLY`: non-export text should not be used as a public semantic rule.

The source Git commit, Core artifact path, recorded semantic review revision and full source SHA256 are verified and surfaced by `evals/cdr_public_semantic_contract.py`. The manifest is itself SHA256-bound; SHA256 provides source consistency, **not identity certification, independent acceptance, or a digital signature**. Falsified quotes, duplicate IDs, incorrectly scoped Markdown sections, invalid structured YAML fields, misattributed delegation and any false claim of acceptance fail closed.

Model Phase A gets only atomically separated `OWNED_EXPORT_CANDIDATE` texts, each marked `CONTRACT_ONLY`. Delegated references are retained separately for **post-model review**, not supplied as target dependency labels or as model-visible provider claims. The target's existing `requires` is never read in the Phase A builder. No material graph edge may be inferred from ownership records alone.

Both the eight-provider catalog and the output obligation inventory remain **research-bounded and not exhaustively accepted**. All project documents used are actual, reviewed source artifacts; none of the operator-selected atomic export claims is independently Authority-approved as a separate atomic public contract.

## Actual provider-backed observation (third real PREP formulation)

External one-shot: [GitHub Actions #37850444500](https://github.com/lehater/harness/actions/runs/37850444500), [full source/response/reconciliation evidence](https://github.com/lehater/harness/actions/runs/37850444500/artifacts/11581363461). PREP source: `lehater/prep@d9adf4ca51049894437f1ed3d4f74fe94936c896`.

Technical execution: **PASS** with one tool-disabled Copilot response, 8 provisional provider exports and no discovered original target graph edges.

Model still reports `RESOLVED` and **only** proposes `prep.knowledge-model`. Its quoted source claim now correctly concerns `KnowledgeProposition` shape rather than wrongly assigning the classifier to Knowledge Model. But the original PREP graph contains `prep.knowledge-model -> prep.knowledge-relation-classification`, making the proposed reverse direct prerequisite cyclic, and the model skipped both of the target's declared immediate sources (`prep.model-context-strategy` and `prep.product-capabilities`). Missing proposals are **not removal evidence**.

The model provided direct needs for **two** target output obligations (`matched`, `candidate_needed`), but no direct input or justified nonapplicability for `insufficient_evidence`. That omission is not consistent with a fully grounded claim of output completeness. The existing provider response protocol lacks an explicit `not_applicable` justification field; the evaluator cannot silently invent one.

## Read-only Phase B direct consumption gate

`evals/cdr_atomic_consumption_review.py` emits a separate packet for every named output obligation. Each proposed need records the exact atomic claim ID, its unaccepted role and model consumption rationale, whether the provider also explicitly delegates the target's own export, and seven **UNVERIFIED** tests:

1. Target owns and independently accepts the output obligation.
2. Provider's specific atomic export ownership is accepted.
3. The exported rule materially constrains *this* output.
4. The supplier's meaning can be produced prior to the target output.
5. Direct source changes affect the target without intermediary changes.
6. Retained immediate provider contracts do not completely mediate the same rule.
7. Independent Authority review/adjudication exists.

A target obligation with no supported `input_needs` and no declared unresolved state is `UNACCOUNTED_NO_NONAPPLICABILITY_JUSTIFICATION`. Phase B blocks an otherwise structurally noncyclic V3 `RESOLVED` result with `BLOCKED_UNACCOUNTED_TARGET_OUTPUT_OBLIGATIONS`. Cyclic proposals remain `INVALID_PROPOSED_TOPOLOGY` with higher priority. Every verdict keeps `effective_resolution=NOT_RESOLVED`, `automatic_writeback_allowed=false`.

This is stricter than graph validity or artifact review alone. It **does not** mechanically prove semantic necessity, sufficiency or identity of an actual Authority decision.

## Verification

- Source-verification tests: `tests/test_cdr_public_semantic_contract.py`.
- Per-obligation proof packet tests: `tests/test_cdr_atomic_consumption_review.py`.
- PREP source-blind integration: `evals/cdr_prep_accepted_target_pilot.py --surface-mode ATOMIC_PUBLIC_CONTRACT_DRAFT_V1`.
- Both tests are registered in `make harness-check` and the focused Draft-safe CI.

Reconciliation of the **frozen real provider output** after the coverage improvement is preferred over generating a different response to prove the negative control. A repeat provider call could additionally test stability, but a single run does not support a reliability percentage.

Current outcome: a technically valid directness *hypothesis* repeatedly fails on real project graph and output-accounting evidence. No `ADD` or `REMOVE` is accepted, no PREP or Harness main writes, no modification to the frozen Reference Model, and Draft PR #220 remains Draft.

## Next admission gap

A governed canonical producer-owned public semantic export contract needs independently recognized reviewer identity, Authority acceptance events bound to exact claim and target obligation revisions, and a project-level authority for applying validated Engineering Graph changes. None is implemented or impersonated by the present research draft. Those require a separate explicit governance design and acceptance, not a metadata flag in this experiment.
