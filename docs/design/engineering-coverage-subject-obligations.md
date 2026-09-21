# Engineering Coverage Subject Obligations

Status: canonical design contract.

## Purpose

Engineering Coverage must prove both closure of known engineering concerns and completeness of the semantic subjects required by an accepted Consumer/Scope. A generated Coverage Map is a projection, never an authority.

The coverage identity is:

`Coverage(project, consumer, scope, concern, subject?)`.

## Four independent completeness layers

1. **Graph completeness** proves realization of Capabilities already declared in the selected Consumer closure.
2. **Concern completeness** proves activated engineering concerns through accepted semantic claims.
3. **Subject/scope completeness** proves that every accepted scope atom was classified into a required semantic subject or an explicit justified disposition, and that every required `(concern, subject)` has exact scoped proof.
4. **Artifact semantic correctness** proves that a provider artifact actually carries accepted semantics; artifact existence alone is insufficient.

No layer substitutes for another. In particular, a complete graph or a covered broad concern cannot prove subject/scope completeness.

## Canonical inputs and generated outputs

Accepted product/engineering requirements remain canonical semantic truth. A subject-obligation contract contains only stable requirement references, Consumer/Scope identity, subject classification and explicit applicability disposition. It must not copy requirement statements.

The obligation contract is canonical routing/classification knowledge because derivation from unconstrained prose is not algorithmically reliable. The Coverage evaluation and Coverage Map are generated projections.

Every accepted requirement identity in the selected scope source must occur in at least one subject or in an explicit exclusion. Adding an accepted requirement therefore invalidates completion until classification is updated.

This proof boundary is deliberate: Harness proves completeness over machine-addressable accepted scope atoms; it does not infer hidden subjects from free prose. Scope atoms should therefore be atomic with respect to independently decidable Consumer obligations. A broader umbrella requirement may reference several subjects, but classifying it into one subject is not evidence that its remaining semantics were considered. Where that distinction matters, Product/Use-Case design must expose stable atoms or an equivalent canonical decomposition before Coverage can prove subject completeness.

## Evaluation

For every REQUIRED subject and concern, proof must match both accepted semantic claim and exact subject. A subjectless broad Capability cannot close a subject-scoped obligation.

Allowed explicit dispositions are:

- `NOT_APPLICABLE`: terminal only with rationale;
- `DEFERRED`: terminal according to project completion policy and only with rationale;
- `QUESTION`: evaluates BLOCKED until resolved.

Consumer and Scope are exact keys of the obligation contract. Proof outside the selected Consumer capability closure cannot satisfy it.

## Source adapters

Scope-source format is an adapter concern. Structured `product-requirements/v1` and accepted Markdown with stable `[REQUIREMENT-ID]` atoms are supported. Projects must make accepted scope atoms machine-addressable; Harness must not infer atomic obligations from free prose.

## Lifecycle and staleness

Upstream accepted-scope growth creates an unclassified requirement and makes Coverage incomplete. Changed subject classification changes the derived obligation set. Semantic rejection/invalidation of a provider still flows through the existing semantic acceptance mechanism. Generated projections can therefore be regenerated rather than edited.

## Activation self-suppression audit

Subject obligations remove one self-suppression class: a required subject can no longer disappear merely because no producer Capability was declared for it. Obligation gaps participate in the same control loop as concern gaps: semantic rejection, blocking Questions, missing prerequisites, ready Capability production, missing production contracts and unclassified accepted scope are all explicit remaining work.

Concern activation has a distinct residual risk when a rule is activated only by knowledge that the concern itself is expected to produce. Current high-risk rules are:

- `SECURITY-BOUNDARY`: depends on security-architecture role/knowledge;
- `OBSERVABILITY-DESIGN`: depends on an observability Capability;
- `QUALITY-DESIGN`: depends on quality-design knowledge/capability;
- `PERSISTENT-DATA`: depends on data role plus persistence Capability;
- `RELEASE-DELIVERY`: depends on implementation-design/delivery knowledge.

These rules are discovery/activation mechanisms, not proof that the concern universe is complete. Where accepted scope requires such a concern, it must be represented by an upstream canonical obligation/profile rather than inferred from the presence of its downstream design artifact. Future activation-policy changes should move those triggers to independent consumer/scope signals when universally valid.

## Invariant

`completion_ready == true` is forbidden when either:

- any activated concern is non-terminal; or
- any accepted scope atom is unclassified; or
- any required subject-scoped obligation is non-terminal.
