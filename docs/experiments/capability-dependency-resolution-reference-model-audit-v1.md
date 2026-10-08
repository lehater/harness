# CDR reference-model control audit v1

Status: **experimental, noncanonical, read-only**. Source: `spec/research/reference-engineering-model-v0.yaml`; source snapshots identified by SHA-256 of reference model, Authority catalog, and semantic proof contract.

## Purpose and boundary

Evaluate CDR against Harness's existing reusable engineering-knowledge model instead of only small PREP examples. Reference templates are **not project-owned, independently accepted Capability contracts**. The source model's `requires` entries are the subject of the audit, **not an oracle**. A source claim ID from the coverage proof catalog is vocabulary, not an accepted target-owned output obligation.

The canonical `docs/design/model-completeness-ownership-v0.md` remains unchanged: project Engineering Graph owns accepted topology; Coverage owns scope completeness; Reference Model proposes templates. The prior decision not to promote Reference Model v0 remains active. No project/Reference Model graph edits, semantic approval, or automatic edge removal occur.

## Two separate review phases

1. `make cdr-reference-prepare CDR_OUTPUT=/tmp/cdr-reference-blind.json` builds a snapshot-fingerprinted source-only corpus of the 40 templates with Authority, knowledge kind, primary/output claim vocabulary and applicability. **Every existing requires list is omitted**. Supply only this output to a provider-backed Phase A reviewer; do not permit repository access to the hidden graph. Existing source outputs are hypotheses, not an accepted semantic baseline.
2. `make cdr-reference-audit CDR_OUTPUT=/tmp/cdr-reference-audit.json` validates the unchanged model with the existing Reference Model validator and produces one source/target evidence packet **for every declared edge**. Packets include alternative structural paths and whether any hop has a conditional `when`. Predicate satisfiability, contract mediation and actual directness remain unproven.

Use `python -m evals.cdr_reference_audit prepare|audit --model ... --authorities ... --proof ... --output ...` to override input paths.

## Actual baseline observations

Inventory from the existing frozen v0 data (recheck by running command and test):

| Item | Count |
| --- | ---: |
| Templates | 40 |
| Direct template edges | 94 |
| Conditional edges | 41 |
| Direct edges with another possible path through a different immediate provider | 40 |
| Templates without explicit `primary_claims` | 12 |

The 12 without primary claims are USER-NEEDS, PRODUCT-ACCEPTANCE, MODEL-CONTEXT-STRATEGY, DOMAIN-USE-CASE, TASK-MODEL, QUALITY-DESIGN, OPERABILITY-DESIGN, REALIZATION-VERIFICATION-PLAN, ACCEPTANCE-SCENARIOS, TEST-DESIGN, IMPLEMENTATION-STACK and COMPLETION-CRITERIA.

Structural flags are review **priorities**, not confirmed defects:

- `INTERFACE-TOPOLOGY -> INFORMATION-ARCHITECTURE` is reachable through `INTERACTION-DESIGN` unconditionally. Navigation topology may still directly consume information organization, so removing this edge from reachability would be unjustified.
- `INTERACTION-DESIGN -> CONCEPTUAL-INTERFACE-MODEL` is reachable through `INFORMATION-ARCHITECTURE`. Whether interaction contracts need conceptual semantics independently remains an Authority review question.
- `DOMAIN-MODEL -> DOMAIN-STRATEGY` also has a path via `MODEL-CONTEXT-STRATEGY`, but both paths are conditional; simultaneous predicate satisfaction and sufficiency of intermediate semantics are **not proven**.
- `IMPLEMENTATION-PLAN` has many direct source templates and alternative routes. Its only explicit primary output claim is `engineering.delivery.release`; whether that captures all its independent obligations is itself unresolved. Audit this contract before trimming input edges.
- `COMPLETION-CRITERIA -> REALIZATION-VERIFICATION-PLAN` is reachable via `IMPLEMENTATION-PLAN`; there is no accepted proof that implementation planning fully replaces direct verification input.

## Test and decision boundaries

`tests/test_cdr_reference_audit.py` checks the real frozen corpus counts and no graph writes, Phase A blinding, conditional reachability caution, stable output, and fail-closed invalid model validation.

The evaluator must justify every proposed direct edge by an independently established target output, accepted provider claim, intermediate sufficiency, independent source change sensitivity and an owning Authority decision. This experimental corpus does not itself meet those acceptance criteria. No `REMOVE_CANDIDATE` or `ADD` is automatically authorized; silence about missing edges does not establish completeness.

## Next checkpoint

Review a bounded contrast set from interface, domain and implementation examples **without showing the accepted `requires` lists to the evaluator**, compare its results with the audit packets, and document contradictions. Only independently confirmed semantics should lead to a *separate* Reference Model revision; do not rewrite frozen v0 to make the audit green.
