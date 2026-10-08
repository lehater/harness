---
name: capability-dependency-resolution
description: "Resolve and review the necessary direct semantic prerequisites of a Capability production contract, without treating existing requires as proof or mutating canonical project truth."
---

# Capability Dependency Resolution (experimental v1)

## Purpose

Determine the complete *known, scope-relative* set of direct semantic inputs required for a target Capability production contract. A direct `requires` edge means the target production materially consumes the source Capability's public accepted knowledge. Reachability, temporal ordering, topic similarity, a common file, and mere read access do not establish an edge.

This is an agent procedure above existing Engineering Graph, Semantic Derivation, Semantic Admission, Capability Lifecycle and Project Publication. It does not introduce a new Core concept, store authoritative dependencies separately, or authorize automatic mutation of project truth.

## Trigger

Use when a Capability production contract is created; its output obligations, semantic scope, owner or subject coverage change; a production is suspected of consuming undeclared knowledge; or an explicit dependency audit requests re-resolution. Do not run merely because an existing prerequisite artifact changed without changing the topology contract; ordinary Lifecycle handles that case.

## Inputs

**Phase A — independent discovery only:**

- target CapabilityId, Authority boundary, `knowledge_kind` where known, and selected subject/scope;
- target public output contract, explicit output obligations, applicable artifact skill and accepted project/consumer coverage policies;
- bounded catalog of possible Capability providers, their owning Authorities, public contracts, subjects and semantic surfaces where accepted;
- source acceptance/provenance status, distinguishing accepted knowledge from contract-only planned knowledge;
- applicable accepted project decisions and known blocking Questions.

Never show Phase A the target production's current `requires`, its accepted dependency baseline, an expert oracle, or target-specific edge labels. Do not pass a whole unfiltered Engineering Graph if it exposes those edges. An evaluated agent must also not be able to retrieve the hidden target edges or oracle through repository search, external tools or connected context during the blind phase. Provider-to-provider links may be shown where needed to test direct versus indirect consumption; they are *not* target dependencies.

**Phase B — reconciliation only:** Phase A output; declared target `requires`; structural graph/context available for validation. Preserve Phase A unmodified when beginning Phase B.

## Procedure

### A. Discover inputs without declared target edges

1. Establish the precise output contract and Authority-owned decisions. Separate product requirements, domain meaning, application orchestration, infrastructure, execution context and non-applicable concerns.
2. Enumerate material output obligations for the selected scope. Derive needs from each obligation: which *external accepted knowledge* must be consumed to establish it without inventing upstream decisions? Distinguish a knowledge dependency from background context, operational access, scheduling or illustrative material.
3. Seek providers from the bounded Capability catalog. Match semantic content, owner and subject — never choose solely by `knowledge_kind`, Authority label, shared artifact or nearby graph path. If no provider is modeled, report a missing provider / contract and do not create fictitious CapabilityIds.
4. For each candidate, state the consumed semantic surface and the exact output obligation it constrains or enables. Ask the counterfactual: without this input or an explicitly valid alternative, can the target output obligation be responsibly produced? For competing providers, determine whether they are alternatives or independently necessary inputs.
5. Independently test direct consumption. Retain a direct dependency even when a separate transitive path exists, when the target itself consumes the source's public meaning. Do not add an edge to a remote producer merely because its ideas influenced an intermediate accepted contract.
6. Distinguish `ACCEPTED_EVIDENCE` (concrete accepted semantic surface supports the claim), `CONTRACT_ONLY` (producer public contract is defined but not accepted), and `UNRESOLVED` (provider, scope or needed meaning remains indeterminate). A planned provider can be a legitimate prerequisite, but its unaccepted assertions may not be treated as accepted proof.
7. Check input-set sufficiency obligation-by-obligation and record unresolved needs explicitly. Do not infer sufficiency from graph validity or lack of findings. If project policy/coverage obligations are missing, mark their absence as a scope limitation rather than claiming general completeness.

### B. Reconcile and validate proposal

8. Freeze the Phase A need-to-obligation-to-provider mapping. Only now inspect current target `requires`.
9. Classify existing and proposed direct edges as `KEEP`, `ADD`, `REMOVE_CANDIDATE`, or `REVIEW_REQUIRED`. A lack of positive support is not by itself proof that a dependency can be removed. A `REMOVE_CANDIDATE` must cite positive evidence that the checked output scope remains satisfied without that direct input.
10. Build a *candidate* Engineering Graph using existing Production Contract `requires` syntax. Run existing structural validators, authority/subject/provider uniqueness and DAG checks. Do not substitute a transitive-reduction algorithm for semantic judgement.
11. If evidence is incomplete, report `UNRESOLVED` and route owner-specific Questions by existing project procedures. If contradictory evidence or a violated invariant exists, report `INVALID`. Only report `RESOLVED` when all identified material needs have grounded providers or justified non-applicability and the proposed topology passes applicable validation.
12. Return a structured, noncanonical result. Recommend updates, never write Engineering Graph, Core, accepted artifacts, Lifecycle or Project Publication. A separate project-owned adoption step must handle version-consistent topology publication and downstream invalidation.

## Output contract (experimental, not Core)

Return at least:

- `target_capability`, `status`: `RESOLVED | UNRESOLVED | INVALID`;
- `input_needs`: stable need identifier, required output obligation IDs, semantic surface needed, provider CapabilityId or null, certainty (`ACCEPTED_EVIDENCE | CONTRACT_ONLY | UNRESOLVED`), direct-consumption rationale and source references where available;
- `proposed_requires`: unique CapabilityIds for all positively established direct inputs, including planned providers when warranted;
- `reconciliation`: `KEEP | ADD | REMOVE_CANDIDATE | REVIEW_REQUIRED`, with evidence-oriented rationale;
- `unresolved`: material provider/obligation/ownership/subject gaps and owner routing where known;
- `scope_limitations`: unchecked obligations, unavailable policy sources or incomplete discovery catalog;
- `validation`: structural and semantic findings from existing checks.

`proposed_requires` is a proposal, never a canonical authority. A `RESOLVED` result means verified against the explicit discovered scope and available policy, not a mathematical proof that no unknown dependency exists.

## Acceptance checks

- Every proposed edge maps to a specific output obligation and directly consumed semantic input.
- Each material identified external input has an accountable provider or an unresolved disposition; no knowledge is invented.
- Direct-and-transitive edges are not removed merely for reachability.
- Same-Authority source artifacts receive explicit Capability prerequisite edges if materially consumed.
- A single CanonicalArtifact providing multiple Capabilities does not force identical input contracts.
- The target's declared `requires` and any expert answers were hidden from Phase A.
- `REMOVE_CANDIDATE` is never interpreted as permission to delete without semantic confirmation.
- Partial designs produce honest uncertainty; changes do not bypass existing acceptance and lifecycle authority.
- No canonical project state is mutated by this skill.

## Non-goals

Not a graph-theoretic transitive reduction, repository-wide context mining, implementation dependency resolver, acceptance substitute, publication mechanism, ontology expansion, or universal guarantee of dependency completeness.