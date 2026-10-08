# CDR — Reference Engineering Model source-contract contrast v1

Date: 2026-10-08
Status: **exploratory, operator-authored, non-blind, noncanonical**
Branch: experiment/capability-dependency-resolution-v1
Reference model pinned Git blob: `7761bac5afbe6f6de061e5408b1ea59da122ee8a`
Audit corpus: [CDR reference-model control audit](capability-dependency-resolution-reference-model-audit-v1.md)

## Method and limits

This assessment cross-checks a bounded set of **declared** Reference Model template edges against the artifact producer SKILL output contracts. In the same conversation, existing edge identities were visible during prior structural analysis. **Do not call this independent or provider-blind Phase A evaluation.** No external semantic evaluator was invoked.

Every finding is an operator hypothesis, not an Authority-accepted project decision. Reference templates are reusable knowledge types rather than accepted project outputs. Their `claim_surface` labels do not establish complete independently accepted output obligations. Even a strong skill-to-edge correspondence does not certify semantic directness for every project instance.

We evaluate independent output consumption, mediation by other producers, a change-sensitivity contrast, and what remains to be reviewed. Findings are *review priorities*, not replacement edges or authority to edit the frozen source.

Sources (all at experimental HEAD `83acd7b2a8f95b82486c6dd34316cda56022adec`):
- Interaction Design SKILL: blob `9ac47607ee7adbff95d0a57df8bed2988178a939`
- Information Architecture SKILL: `8698d0c78c9358bece1a3d856bc09bac8bcfa324`
- Interface Topology SKILL: `ffb45bed5862d0a5da73c136ca0da3a66470ad8f`
- Conceptual Interface Model SKILL: `362af77a1f23b4a78f3922bb4adab34999de2b87`
- Screen/View Design SKILL: `bc511b9f4e6950cc6f1cbc48582c66479d2a8a43`
- Model Context Strategy SKILL: `56145221d495950eaf85a91b0652ce85e5f0059d`
- Domain Model SKILL: `580ba29b4d5a19753e367b40b18861819dd7217f`
- Domain Strategy SKILL: `f30d888a2ec540e10d9f805e93fa5184076232b4`
- Implementation Design SKILL: `7c620aec0a1d922d5578a4b080620949b74cc25b`
- Verification Strategy SKILL: `25c12f950aac42a681e4eef220ed6e72170c1be1`
- Authority catalog: `4f4b28ba5566ef14fc9c88a06e8c2acd7e095aaf`

## Focused semantic contrasts

### REF-CDR-01 — INTERACTION-DESIGN -> INFORMATION-ARCHITECTURE

**Disposition: POSSIBLE_UNNECESSARY_DIRECT_EDGE — highest review priority, NOT accepted deletion.**

Target SKILL output: interaction contexts, task/concept references, actions/inputs, user-visible system outcomes, state transitions/recovery, and role requirements. Its declared **Inputs** and **Read boundary** do not list accepted IA locations as necessary. Its procedure explicitly says to *leave placement into IA locations to Interface Topology*.

Supplier SKILL output: information locations, conceptual grouping, taxonomy/labels and findability. These outputs are directly referenced by the *Topology* output, not evidently by the *Interaction* output.

**Counterfactual:** IA reorganizes locations and labels while task goals, conceptual meanings, observable actions/states and server outcomes remain unchanged. Interaction output can plausibly remain unchanged; Topology must re-map contexts to changed IA locations. This weakens the necessity claim for a direct Interaction->IA edge. Conversely, if accepted Interaction output really contains IA-bound findability or location-specific user decisions, exhibit their independently approved stable obligation IDs and show why Topology cannot mediate them.

This is stronger than a reachability warning: the production SKILL's own contract assigns the suspected consumption to another producer. It does not prove the link wrong for every possible project. Owning Human Interface Authority must decide whether this v0 generic template should omit, condition or retain the edge.

### REF-CDR-02 — INTERFACE-TOPOLOGY -> INFORMATION-ARCHITECTURE

**Disposition: DIRECT_CONSUMPTION_EVIDENCED_BY_SKILL — provisional KEEP; NOT formal approval.**

Topology output expressly includes IA-location references, view-to-location mapping, conceptual findability/navigation dispositions and cross-links. IA owns stable conceptual location IDs and grouping. Interaction Design's outputs do not promise to publish this IA location inventory. A taxonomy/location reorganization with unchanged interactions can still force Topology review.

Hence a graph path through Interaction Design (present in v0) does **not** prove mediation or redundancy of Topology's direct IA edge. This is a negative control for naive transitive reduction.

### REF-CDR-03 — INTERFACE-TOPOLOGY -> INTERACTION-DESIGN

**Disposition: DIRECT_CONSUMPTION_EVIDENCED_BY_SKILL — provisional KEEP.**

Topology explicitly enumerates interaction contexts, associates task views with context refs, and proves every context has a view disposition. Interaction Design owns interaction contexts, user actions, observable states and recovery; IA does not. A change to required interaction context with unchanged IA taxonomy materially changes the target's view inventory and coverage. Direct consumption is strongly indicated in the SKILL contract.

### REF-CDR-04 — INTERACTION-DESIGN -> CONCEPTUAL-INTERFACE-MODEL

**Disposition: DIRECT_CONSUMPTION_EVIDENCED_BY_SKILL — provisional KEEP.**

Interaction Design's output includes task/**concept** references and possible user-visible interaction roles, modes and state distinctions. The Conceptual Interface Model owns concept identities/meanings and shared user-visible mode/state vocabulary; IA organizes locations but does not own those meanings. Changing a concept's user-visible roles or mode distinctions may require interaction state/transition changes while IA grouping remains identical. Thus the alternative path through IA cannot be presumed a sufficient semantic substitute.

### REF-CDR-05 — SCREEN-VIEW-DESIGN -> INTERACTION-DESIGN

**Disposition: DIRECT_CONSUMPTION_EVIDENCED_BY_SKILL — provisional KEEP.**

Screen/View SKILL requires direct bindings to accepted actions, operation outcomes and state variants; its procedure (observable realization) derives screen-level assertions directly from upstream interaction obligations. Topology maps contexts to views, while Presentation System supplies shared representations; neither necessarily publishes all independently losable user-observable interaction actions/states. A new interaction denial/recovery state with unchanged navigation topology and presentation patterns can change screen composition and assertions. The direct edge has a concrete output reason despite alternate paths.

### REF-CDR-06 — PRODUCT-INTENT -> PROBLEM-EVIDENCE

**Disposition: CONDITIONAL_PATH_DOES_NOT_REPLACE_DIRECT_EDGE — provisional KEEP.**

The source graph has a second route through USER-NEEDS, but USER-NEEDS is conditional on material user-needs evidence. Product intent is always required by the Reference Model's generic target and must remain defensible when the user-needs specialization is not applicable. Even before examining substantive semantics, this counterexample disproves using that possible path alone as proof of redundancy. Whether the direct source imposes a particular product output obligation still belongs to accepted Product Requirements review.

### REF-CDR-07 — DOMAIN-MODEL -> DOMAIN-STRATEGY

**Disposition: OPEN_MEDIATION_QUESTION — no proposed edit.**

Strategic Domain output owns subdomain/responsibility landscape and investment classification. Model Context Strategy owns model-language applicability and translations; Tactical Domain Model owns concepts, invariants, and domain responsibility *within an accepted context*. For some subject scopes, Model Context may fully convey all necessary strategic boundaries, in which case a direct tactical-to-strategy edge may be unnecessary. But this is conditional: strategic classes might constrain independently required tactical scope in ways not exposed by the accepted context contract.

Review two concrete subject scenarios: (a) domain classification changes but accepted context public contract stays fixed; does any intrinsic domain model invariant change? (b) context translation/boundary changes with stable strategy; do tactical concepts change? Without accepted model-context content and owner adjudication, neither directness nor redundancy is proven.

### REF-CDR-08 — IMPLEMENTATION-PLAN -> PRODUCT-INTENT

**Disposition: TARGET_OUTPUT_UNDERSPECIFIED — no proposed edit.**

Reference template declares `engineering.delivery.release` as its sole explicit primary output claim, but the Implementation Design SKILL owns implementation slices, semantic-to-physical mapping, integration/quality gates, and more. A single broad label does not independently identify which accepted outputs require direct access to original product scope versus narrower accepted component/architecture/verification provider interfaces.

Before judging this and the many other IMPLEMENTATION-PLAN edges, first establish target-owned obligation IDs for implementation slices, exclusions, gates, etc. Do not delete these links merely because another path exists; do not retain them merely because the generic implementation SKILL lists upstream subject areas.

### REF-CDR-09 — COMPLETION-CRITERIA -> REALIZATION-VERIFICATION-PLAN

**Disposition: TARGET_OUTPUT_UNDERSPECIFIED — provisional direct-consumption rationale, no decision.**

The Implementation Design SKILL explicitly says completion criteria prove realization of accepted design and selected test contracts must have executable conformance. The Verification Strategy SKILL owns evidence objectives and traceability; the implementation plan may not fully represent those acceptance gates. That argues for possible direct verification input even when the verification plan is also reachable through Implementation Plan.

However, the Reference `COMPLETION-CRITERIA` template has neither `primary_claims` nor `claim_surface`. Consequently this experiment cannot claim independently defined *target* output obligations, and cannot authorize KEEP/REMOVE.

## Provisional tally

- 1 high-priority possible unnecessary direct edge (REF-CDR-01).
- 4 links with concrete direct-consumption explanations and counterfactuals (REF-CDR-02 to 05).
- 1 conditional-path negative control that rejects reachability-only deletion (REF-CDR-06); the substantive target obligation remains unaccepted.
- 3 unresolved cases pending project-owned output obligations / mediation evidence (REF-CDR-07 to 09).
- **0 Authority-approved changes, 0 reference graph edits, 0 independently certified CDR verdicts.**

## Falsification / next evidence

1. Run the manually dispatched `harness core` workflow on the experimental branch; the Draft-suppressed automatic full gate is **not equivalent** to execution.
2. Run an isolated provider-backed Phase A evaluation on the *blinded* artifact `cdr-reference-phase-a-blind`, with zero repository access and no graph/oracle data. This document and Phase B output must not be provided to that evaluator.
3. Independently define accepted target output contracts and provide immutable project/Authority acceptance revisions. Reconcile its predictions with all 94 declared links, including **missing** edge candidates.
4. For REF-CDR-01, ask the owner to find an interaction obligation consuming an IA-location rule not already deferred to Topology. If none and the owner explicitly accepts an updated contract, propose a new Reference Model snapshot with a revised edge; preserve frozen v0 for calibration.
5. For REF-CDR-02/03/04/05, challenge alleged mediation with a concrete source-change / intermediate-stable case before any KEEP certification.
6. Only after independent acceptance may a project Authority propose a changed accepted Engineering Graph. Never auto-write `requires` and never promote the research Reference Model on an operator hypothesis.

The canonical Harness Core, PREP, original Reference Model and `main` remain unchanged.
