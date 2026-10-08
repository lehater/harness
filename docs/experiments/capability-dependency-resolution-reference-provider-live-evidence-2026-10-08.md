# CDR Reference Model — provider-backed blind pilot, 2026-10-08

Status: **external experimental evidence; source-bound model hypotheses only, not an Authority verdict**.

Execution: [GitHub Actions 37833242228](https://github.com/lehater/harness/actions/runs/37833242228) — PASS; [raw evidence artifact](https://github.com/lehater/harness/actions/runs/37833242228/artifacts/11575005076) with `inputs.json`, `request.json`, `provider.json`, `contrast.json`.
Run branch: `experiment/cdr-reference-provider-once-20261008`; commit `f19429fb37de7348d5914c074d46f49a029106b8`, based on PR #220 experimental commit `1e768a457dbc3a14ef4f0ed7fb42ed42e0edd399`.

## Protocol and outcome

A one-time operator-authorized, branch-specific push workflow invoked the existing GitHub Copilot CDR adapter with CLI `1.0.86`. It ran with a fresh home/work session, disabled custom instructions, built-in MCPs and external tools. Adapter provenance reports one complete model response and no schema retries.

Three source-only cases, each with all other 39 research template providers labeled `CONTRACT_ONLY`; selected target `requires` and expert labels were withheld. The model response was frozen before reading actual reference links. Every case is marked `UNRESOLVED`; source-grounding checks report `REVIEW_REQUIRED`, no malformed references, and no accepted/authoritative output contract. The automated reconciliation says `PROVIDER_HYPOTHESES_REQUIRE_INDEPENDENT_ADJUDICATION`.

| Target | Declared direct sources | Model suggestions | Intersection | Model additions (unaccepted) | Declared not suggested (review only) |
| --- | ---: | ---: | ---: | --- | --- |
| INTERACTION-DESIGN | 2 | 4 | 1 | DOMAIN-USE-CASE, TASK-MODEL, USER-JOURNEY | INFORMATION-ARCHITECTURE |
| INTERFACE-TOPOLOGY | 2 | 4 | 2 | SCREEN-VIEW-DESIGN, USER-JOURNEY | None |
| DOMAIN-MODEL | 3 | 1 | 1 | None | DOMAIN-STRATEGY, PRODUCT-INTENT |

Details:

- Interaction Design: retained `CONCEPTUAL-INTERFACE-MODEL` as a model need. IA's missing proposal agrees with the separate SKILL-contract hypothesis, **but it is not a proof**: two output obligations remained unresolved; the model proposed three other upstream sources.
- Interface Topology: proposed both existing links `INFORMATION-ARCHITECTURE` and `INTERACTION-DESIGN`, also `USER-JOURNEY`; two output obligations unresolved.
- **Concrete incorrect structural proposal:** `INTERFACE-TOPOLOGY -> SCREEN-VIEW-DESIGN` would create a dependency cycle because `SCREEN-VIEW-DESIGN -> INTERFACE-TOPOLOGY` is already unconditional in frozen Reference Model v0. The agent's output is demonstrably unsound for graph adoption on this edge even if its semantic rationale sounds relevant. This is a falsifying counterexample to unguarded automated resolution, not an accepted change to the model.
- Domain Model: the agent selected `MODEL-CONTEXT-STRATEGY` but did not propose direct `PRODUCT-INTENT` or `DOMAIN-STRATEGY`. Tactical concepts and invariants remain unresolved. An omitted proposal **must not** be treated as evidence of redundant domain/product dependencies.

## Defect fix and further review

On PR #220 the read-only Phase B reconciler was extended after this real run to detect candidate cycles: it reports `invalid_new_edge_candidates` and `structural_candidate_status=BLOCKED_BY_CYCLE`, while retaining the exact original model `new_candidate_not_accepted`. The regression creates a cyclic `TOPOLOGY -> SCREEN-VIEW-DESIGN` test response and requires deterministic rejection. The provider-facing request builder remains unchanged.

The original GitHub Actions artifact is retained unmodified. The one-shot research workflow is on a separate non-PR branch and is **not** a production or accepted assurance gate. The prior accepted `live-calibration-copilot.yml` remains byte-identical; neither `main`, PREP, frozen v0 nor existing accepted Engineering Graph changed.

**Next quality question:** Why did the model elevate Screen/View composition (which is downstream of topology) as if it were a prerequisite for deciding the view inventory? Challenge the direction of semantic production independently of topic overlap. Assess producer-to-target role and graph-cycle consistency before even reviewing semantic necessity. In the next holdout, test both topologically reversed and justified direct-transitive edges. Never let model agreement, one missing suggestion or a valid graph substitute for accepted Authority-owned target and provider evidence.

## Adoption boundary

`authority_acceptance=false`, `independence_attested=false`, `semantic_directness_proven=false`, `automatic_writeback_allowed=false`. The full Harness gate PASS documented earlier applies to a prior commit; deterministic focused CI validates the new cycle guard, but no full-gate claim is made for this updated PR head.
