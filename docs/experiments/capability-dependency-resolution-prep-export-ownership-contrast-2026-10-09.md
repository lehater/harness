# CDR — PREP public-output ownership selection: negative A/B evidence

Status: **research only**; target source and provider source documents were Core-registered and semantically reviewed, but provider ownership and target's individual output obligations are **not independently accepted** here. No accepted Engineering Graph edits.

## Frozen project and evidence

Project: `lehater/prep@d9adf4ca51049894437f1ed3d4f74fe94936c896`.
Target: `prep.knowledge-relation-classification`.
Owned target artifact: `docs/domain/relation-classification-catalog.yaml` (`matched`, `candidate_needed`, `insufficient_evidence`).

- Prior naive 48-claim prefix input: [Copilot run #37837395704](https://github.com/lehater/harness/actions/runs/37837395704); [frozen evidence](https://github.com/lehater/harness/actions/runs/37837395704/artifacts/11576680353).
- New research-owned-section selection: [Copilot run #37846899346](https://github.com/lehater/harness/actions/runs/37846899346); [frozen evidence](https://github.com/lehater/harness/actions/runs/37846899346/artifacts/11579399202).
- Both use same pinned project, target, eight candidate providers and production-direction evaluator protocol. The **source selection/payload** changed; this is **not** a byte-identical input intervention nor a provider quality estimate from repeated trials.

Source mode `CANDIDATE_OWNED_SECTIONS_V2` is implemented by `evals/cdr_provider_owned_surfaces.py` and the source-bound `prep-provider-owned-surface-selectors-v1.yaml`. It extracts explicit markdown section text and structured YAML requirements instead of indiscriminate initial 48 fragments. The selected source text includes all 17 individually accepted product requirements (not all generic YAML scalar fragments), plus research-selected purpose/meaning/boundary sections for the other seven providers. It **does not claim the whole source has been inventoried**; all eight source scopes are declared `selection_scope_partial=true`. These are operator-authored selector hypotheses, not Authority-certified semantic exports.

## Actual Copilot result: failure repeated

Both real provider runs passed their orchestration/evidence format, but each returned `status=RESOLVED` and proposed **only `prep.knowledge-model`**, omitting both existing target prerequisites `prep.model-context-strategy` and `prep.product-capabilities`.

The proposed link is structurally invalid: current graph contains `prep.knowledge-model -> prep.knowledge-relation-classification`, so the reverse link would form a cycle. Phase B sets `INVALID_PROPOSED_TOPOLOGY`, `effective_resolution=NOT_RESOLVED`, and never approves a graph mutation. **No omission is removal evidence.**

The new model answer specifically cited `knowledge-model.md`'s *Relational Subject Knowledge* section (index 1) as direct supplier of all three classifier outputs. But the same source section unambiguously states that **`docs/domain/relation-classification-catalog.yaml` provides the reusable predicate vocabulary and classifier**. It is therefore false to treat this passage *alone* as proof that Knowledge Model owns/publishes those target outputs. The section also discusses its own KnowledgeProposition representation, so an entire source section may **mix owned meaning with explicit delegation to another semantic exporter**.

This counterexample falsifies treating *section selection* or a valid source `claim_index` as sufficient proof of exported ownership. It does **not** prove every underlying model relation; the supplier might own other distinct meanings, and an independent owner must decide any purported direct consumption.

## Defensive output-contract correction

Added `evals/cdr_contract_owner_conflicts.py`: a **narrow, auditable, source-quoted Phase B negative check**. For a model-cited source claim, it detects a *literal exact reference to the target Core artifact* immediately followed by explicit export verbs such as *provides*, *defines* or *owns*. It then records `BLOCK_PROVIDER_AS_TARGET_EXPORT_OWNER_EVIDENCE` with the original quote, provider, claim index, target artifact identity and an explicit independent-review requirement.

This does not derive the full ontology from regexes. A generic document mention, topic overlap or unrelated filename never proves or disproves ownership. If a proposed edge is cyclic it remains `INVALID_PROPOSED_TOPOLOGY`; in a noncyclic setting an explicit target-as-export owner citation produces `BLOCKED_PROVIDER_CITES_TARGET_AS_EXPORT_OWNER`. Other source-selected inputs still produce `BLOCKED_OPERATOR_SELECTED_PROVIDER_SURFACES`. All outputs remain `NOT_RESOLVED` and `automatic_writeback_allowed=false`.

The source-only builder never opens the original Engineering Graph. The new diagnostic is computed only **after** the provider reply has been frozen and semantic source-citation validation has run. Original Copilot output and archives remain unchanged.

Coverage: deterministic tests exercise positive explicit delegation, non-owner document references, negated phrases, ambiguous quotation, fake Core/semantic-revision sources, mode-swapping and partial-source blocks. This check is a **necessary negative proof on observed examples**, not an affirmative semantic-entailment or independent Authority acceptance mechanism.

## Next meaningful frontier

Represent individually reviewable *owned exported contract claims* with separate source text, claim author/Authority, explicit delegation/exclusion, accepted revision, target output obligation and consuming context. A peer-reviewed claim export can be reused across multiple target dependencies, whereas a raw Markdown paragraph cannot serve as a canonical atomic contract just because its parent document was accepted.

Before graph ADD/REMOVE decisions, require accepted target-owned output obligations, accepted exported provider meaning, a producer/consumer proof with counterfactual mediation and Authority review. No main/PREP edits or promotion of Reference Model v0.
