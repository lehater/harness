# CDR atomic Authority review bridge — nonauthorizing draft v1

State: **experimental, read-only, noncanonical; no Authority acceptance mechanism has been introduced or impersonated.**

## Why a bridge is needed

A Core-registered and semantically revised artifact establishes a reviewed published *document*, but does not automatically establish independently accepted *per-claim export ownership*, target-obligation completeness or material direct consumption.

The PREP Knowledge Model example proves the distinction: the model genuinely owns KnowledgeProposition representation, while the classifier itself is published by a separate, named relation-classification artifact. Even when the model cites only its correctly owned representation clause, the proposed direct edge is cyclic and the model omits a third target output obligation. Any mechanism promoting LLM `RESOLVED`, reviewer role labels or matching hashes straight to an accepted Engineering Graph edge would be unsound.

## Four independently reviewed facets

`evals/cdr_authority_review_bridge.py` builds a content-addressed packet, grounded in the **unchanged, frozen** Phase A provider response, PREP pinned git commit, Core ownership records, semantic review revisions and V3 atomic source-quote manifest.

| Facet | Object | Routed review Authority | Meaning of a positive *draft* interpretation |
| --- | --- | --- | --- |
| Target output | One named target-owned obligation | Producing target Authority | The stated obligation appears within the target's material responsibility |
| Owned exported claim | One source-owned, source-quoted claim ID | Provider's own Authority | The source is plausibly the semantic owner of that **specific** output claim |
| Direct consumption | One target obligation / source claim pair | Target Authority, with provider claim review separate | A provider claim might be materially consumed **directly**, not fully mediated by another prerequisite |
| Input coverage | The bounded target contract and candidate provider universe | Target Authority | A preliminary scope might be sufficiently accounted for; cannot claim if source set is partial, outputs unaccounted or declared direct links unreviewed |

Source-grounded claims and target output obligations are separately identified; one positive facet does not implicitly decide the others. A tentative `LIKELY_DIRECT` row requires **separate** `LIKELY_OWNED` and `LIKELY_IN_SCOPE` draft rows. It remains a draft, never evidence of accepted directness. Each proposed direct need records its structural cycle status; a cyclic proposal cannot even be tentatively marked `LIKELY_DIRECT`.

The current PREP source scope is incomplete: eight providers with individually selected candidate exports, missing independent acceptance of target obligations and source ownership; existing direct requires omitted from the model response remain unassessed. Therefore a `DRAFT_SCOPE_PLAUSIBLE` coverage decision is rejected in this run.

The review packet retains original model request/response SHA256, source manifest SHA256, original project commit and the explicit diagnostic blockers. Its packet SHA256 ensures content consistency, **not reviewer identity, trusted signature, or Authority acceptance**.

## Operational process

1. Build the packet **by regenerating the whole original case** from a clean, exact PREP git snapshot and frozen Copilot evidence. Never trust a submitted contrast or unverified packet.
2. Emit a nonauthorizing, complete draft with separate decisions and review questions for each facet. Human or agent-supplied suggestions can propose `LIKELY_IN_SCOPE`, `LIKELY_OWNED`, `LIKELY_DIRECT`, `LIKELY_MEDIATED` and similar provisional decisions with substantive evidence.
3. Validate the draft, **again regenerating** the packet from PREP and the frozen provider response. Reject stale source, missing/duplicated decisions, forged acceptance fields, authority routing mismatch, graph-cyclic likely-direct proposals, and provisional scope-completeness assertions with unaccounted outputs or unreviewed existing edges.
4. Output only `DRAFT_CONSISTENT_NOT_AUTHORITY_DECIDED` with all non-trust fields false. It does not write PREP, Core, baseline, Engineering Graph or lifecycle.
5. A future trusted Authority decision system must separately establish reviewer identity/authorization, independently accepted exact provider claim revision and target obligation revision, material and unmediated consumption, appropriate cross-Authority review, accepted source coverage, valid project graph-update rights, and publication/revision events. **That future transition is explicitly outside this PR.**

Usage after a provider response has already been frozen (from PREP V3 source-only pilot):

```sh
python -m evals.cdr_authority_review_bridge prepare \
  --project-root /path/to/pinned-prep \
  --inputs evidence/inputs.json \
  --request evidence/request.json \
  --response evidence/provider.json \
  --packet review/packet.json \
  --draft review/draft.json

python -m evals.cdr_authority_review_bridge check \
  --project-root /path/to/pinned-prep \
  --inputs evidence/inputs.json \
  --request evidence/request.json \
  --response evidence/provider.json \
  --packet review/packet.json \
  --draft review/draft.json \
  --output review/validation.json
```

This bridge is a research review artifact, not a separate Authority, a new canonical Knowledge kind, a policy loosening or a fork of Semantic Admission. Existing Harness Semantic Admission and Decision Governance remain the authoritative pathway for ordinary project artifact production. Any actual CDR graph write/change admission needs its own governed design and permission.

## Safeguards and limitations

Tested with synthetic source-bound packets and rejection controls (cyclic proposed directness, source/target ownership promotion by declaration, missing facets, tampered hashes, route mismatch, scope omission, spoofed acceptance). Also run a full Harness check and a remote Phase B replay against the original PREP atomic provider response, with no second model invocation. These checks prove consistency of a draft packet; they do not themselves demonstrate independently accepted semantic truth.

Evidence baseline: [atomic Copilot run #37850444500](https://github.com/lehater/harness/actions/runs/37850444500), [frozen provider evidence #11581363461](https://github.com/lehater/harness/actions/runs/37850444500/artifacts/11581363461). Project snapshot: `lehater/prep@d9adf4ca51049894437f1ed3d4f74fe94936c896`.

No `main`, PREP or canonical graph changes; Draft PR #220 remains Draft.
