# CDR — real PREP reviewed target pilot and falsifying counterexample (2026-10-08)

Status: **real provider-backed observation, read-only**. Source artifacts are genuinely Core-registered and baseline-reviewed; this does **not** establish independent acceptance of every target output obligation or every provider citation's normative sufficiency.

## Pinned project and isolation

Real project: `lehater/prep@d9adf4ca51049894437f1ed3d4f74fe94936c896`, pinned and checked out separately from experimental Harness. This is later than the historical planned-Tactical-Target snapshot `c52ff8ec...` and contains a fundamentally different, accepted Subject Knowledge / Capability & Performance / Learner Evidence model. It must not be treated as a continuation of the former planned `prep.preparation-information-model`/history model without a semantic revision.

Pilot target: `prep.knowledge-relation-classification` (Core artifact `docs/domain/relation-classification-catalog.yaml`, recorded target semantic review revision 4). Its *own* canonical YAML declares three distinct `classification_outcomes` with `meaning` and `required_output`: `matched`, `candidate_needed`, `insufficient_evidence`. These were transformed into source-anchored model obligations **without** copying upstream provider statements as target obligations; individual independent Authority adjudication of the transformed obligation IDs is **not proven**.

Bounded eight-provider catalog: `prep.model-context-strategy`, `prep.product-capabilities`, `prep.domain-strategy`, `prep.knowledge-model`, `prep.learning-design`, `prep.learner-model`, `prep.task-model`, `prep.application-design`. Each has a Core file and semantic review revision, and each was included independently of the target's existing `requires`. All are labeled `ACCEPTED_EVIDENCE` at source-document level, but no sentence-level entailment claim is implied.

Phase A reads only Core, semantic baseline, selected target-owned outputs and provider source files; it **never opens** `.harness/engineering-graph.yaml`. Copilot runs tool-disabled using the existing adapter. Only Phase B reads the graph. No credentials are added to output artifacts.

## Actual remote run

- [GitHub Actions #37837395704 — PASS](https://github.com/lehater/harness/actions/runs/37837395704), [source + provider + contrast archive](https://github.com/lehater/harness/actions/runs/37837395704/artifacts/11576680353).
- GitHub Copilot CLI 1.0.86, recorded provider model `gpt-6-luna`, one complete invocation and zero schema retries.
- The model returned `RESOLVED` and suggested exactly one direct supplier: **`prep.knowledge-model`**. It omitted both existing declared providers **`prep.model-context-strategy`** and **`prep.product-capabilities`**. Three output obligations were declared resolved by the model.
- Actual pinned graph contains `prep.knowledge-model -> prep.knowledge-relation-classification` as a direct edge. Adding the reverse `prep.knowledge-relation-classification -> prep.knowledge-model` would immediately create a two-node cycle. **Deterministic Phase B correctly blocked this candidate.**
- Of eight source surfaces, five were truncated at a fixed prefix of 48 claims: Model Context 48/83, Knowledge Model 48/117, Learning Design 48/233, Learner Model 48/167, Task Model 48/207. Product Capabilities 26/26, Domain Strategy 42/42 and Application Design 29/29 were untruncated. This is a material source-completeness limitation. The model's omitted edges are strictly **unassessed existing requirements**, not removal evidence.
- The model cited several `knowledge-model.md` claim snippets about `KnowledgeProposition` as if they directly controlled the classification procedure. Actual cited texts include bare `Conceptually:` and `Examples:` fragments and illustrative examples (CPU quota, right triangle). The citation references are real but semantically **non-entailing** evidence for a normative classifier outcome. Acceptance of a document does not certify every quoted paragraph as an independently consumed provider rule.

## Corrective implementation

Added `evals/cdr_prep_accepted_target_pilot.py` with anchored source-only real-output preparation, exact Git snapshot verification, bounded reproducible claim sampling, strict provider/source binding, an explicit nonacceptance barrier and post-model DAG cycle checking. Added synthetic pinned-Git fixture tests to the full gate and Draft-safe focused checks.

After the live run, tightened the read-only reconciliation:
- `INVALID_PROPOSED_TOPOLOGY` when any proposed new supplier closes a cycle, **even when the model says RESOLVED**.
- `BLOCKED_INCOMPLETE_PROVIDER_SURFACES` when evidence surfaces are truncated and no cycle is present; full input-set sufficiency cannot be claimed.
- `BLOCKED_NON_SUBSTANTIVE_SOURCE_CLAIMS` for transparent, unambiguous heading-only references such as `Examples:` or `Conceptually:` when no prior stronger block is present. This lexical guard is strictly a negative control, **not a general semantic entailment validator**; ordinary substantive text can also fail independent semantic review.
- `REVIEW_REQUIRED_TARGET_AND_DIRECTNESS_ACCEPTANCE` when structural blockers and these narrow evidence defects are absent. All paths keep `effective_resolution=NOT_RESOLVED`, `model_resolution_is_not_accepted=true` and `automatic_writeback_allowed=false`.
- Explicit malformed-response rejection for a `RESOLVED` label containing nonempty unresolved obligations. Tests cover cycle, truncation, non-substantive cited source, contradictory model status and source dirty-check fail-closed behavior.

The original full provider evidence artifact remains untouched. No new provider-backed run has been performed after the status-guard changes: these are deterministic post-model safety improvements, not a claim the agent was re-trained or that accepted semantics were newly adjudicated.

## Interpretation and next experiment

This is an important counterexample to inferring semantic directness solely from a provider document discussing a target's meaning. A downstream consumer can quote and explain the upstream source, and an LLM may incorrectly reclassify that downstream commentary as the upstream producer of the target's output.

Future provider catalog ingestion should distinguish **source-owned exported normative claims** from **context, examples, references to another Capability and downstream consumption**. Ownership and entailment cannot be proved by the original claim's location in a reviewed artifact. A more complete producer catalog and individually Authority-approved target obligations are needed before claiming direct-source completeness.

Do **not** delete `prep.model-context-strategy` or `prep.product-capabilities` links because the agent omitted them. Do **not** add `prep.knowledge-model` to the relation-classification target. No changes were made to PREP, Harness main or the frozen Reference Engineering Model. Draft PR #220 remains noncanonical.
