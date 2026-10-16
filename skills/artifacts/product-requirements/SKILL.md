---
name: product-requirements
description: "Use for actionable CREATE work requiring accepted product intent, observable behavior or acceptance semantics. Derive requirements from accepted problem evidence and explicit product decisions without inventing domain ownership or technical realization."
---

# Product Requirements

## Trigger

Use when actionable grouped artifact work has `knowledge_kind:
product-requirements`, including product-intent and acceptance capabilities that
may be materialized by one coherent requirements artifact.

## Inputs

- actionable grouped artifact work and Product Requirements Authority;
- accepted Problem Evidence when required by the production contract;
- explicit user/stakeholder product decisions;
- accepted scope constraints and existing product policy relevant to the selected
  target.

## Read boundary

Read the smallest canonical sources needed to establish:

- product goal/intent;
- externally observable behavior;
- product-level constraints and scope boundaries;
- acceptance expectations/examples;
- explicit non-goals.

Domain models, architecture, interfaces, persistence and implementation are read
only when checking for conflicts. They do not become evidence that a product
decision was accepted merely because current code behaves that way.

## Procedure

1. Confirm all grouped capabilities are actionable CREATE under one Product
   Requirements Authority and subject.
2. Enumerate the relevant source/evidence statements before drafting requirements.
3. Classify **each decision/source statement before assigning a REQ id** as PRODUCT_REQUIREMENT, PRODUCT_CONSTRAINT, ACCEPTANCE_CRITERION, VERIFICATION_OBLIGATION, NON_GOAL, CONTEXT, DOWNSTREAM_DECISION, QUESTION or DUPLICATE. Classify by *semantic owner*, not speaker: stakeholder confirmation of a test procedure, oracle, Domain/Architecture/Interface decision does not turn it into a Product Requirement.
4. Normalize requirement-bearing statements into independently changeable **product obligations**, not independently testable fields or cases:
   - preserve observable scope, temporal, cardinality, negative and NOT_REQUIRED constraints, including in acceptance criteria/non-goals;
   - one cohesive input/output contract may contain multiple independently testable fields (IPv4, TCP/UDP, both ports), states (known/unknown metadata), or scenarios without requiring a REQ for each;
   - split only when obligations could meaningfully be accepted, changed, removed or assigned a distinct product priority independently. Document the independence rationale; share one group identity for facets of the same obligation and merge them before admission;
   - different examples/test vectors verify one obligation; they do not become product requirements by being separately testable;
   - retain genuine independent negative behavior constraints, but record mere absence of a mandatory feature under non_goals rather than manufacturing a positive capability;
   - do not discard an observable constraint just because a sentence contains design vocabulary.
5. Reconcile conflicts. If two accepted sources imply incompatible product behavior, create a Product Requirements Question and stop the affected capability.
6. Normalize the accepted result into product-level observable requirements without importing Domain/Architecture/API/Data choices. When a mixed statement contains both observable intent and a downstream realization choice, preserve the observable constraint and route the realization choice to its owning downstream Authority. If nothing observable remains after removing the realization choice, do not manufacture a Product Requirement from it.
7. Define acceptance semantics/examples sufficient for downstream design to know what success means. Acceptance criteria describe observable pass conditions; a requirement to *author independently labeled test cases, execute tests or maintain an oracle* belongs to Verification Design, even when explicitly requested by the product owner. Never elevate such a procedure to a Product REQ.
8. Preserve scope boundaries and non-goals.
9. Keep source/evidence semantics distinct from accepted product decisions.
10. Do not select Domain entities/aggregates, architecture, API shape, persistence, package layout or implementation strategy.
11. If a needed product choice is not determined by accepted input, create a Core Question to Product Requirements and stop the affected capability rather than inventing behavior.
12. Do not invent numeric quality targets; preserve explicit NOT_REQUIRED decisions when they exist.
13. Produce one canonical managed `product-requirements/v1` artifact.
14. Give every atomic normative requirement a stable unique `REQ-*` identifier.
15. Record non-empty `source_refs` for every requirement; preserve rationale when it materially explains derivation or intent.
16. Publish **only currently accepted** requirements (`status: ACCEPTED`). Delete invalid, superseded, merged or withdrawn requirements from canonical active content; **no `RETIRED` entries or historical ID inventories**. Git preserves previous versions. Do not silently reuse an old ID for a different obligation. Respect the global current-state-only rule in `docs/design/process-simplicity-and-efficiency-v0.md`. If accepted downstream references exist, reconcile them before removing their required semantics.
17. Produce an explicit, machine-addressable semantic review *before* admission:
   - `source_dispositions`: each relevant source statement (one stable source identifier) assigned one of the classifications in step 3, with a rationale and the product REQ ids it supports; Verification/Non-goal/other non-product sources have no REQ ids. Verification obligations must be handed off with provenance, not silently dropped;
   - `requirement_classifications`: every product assertion id, role PRODUCT_BEHAVIOR or PRODUCT_CONSTRAINT, one stable *normative obligation* group, and a rationale explaining why this is a distinct product obligation. The same obligation group must not appear on two REQs; consolidate first;
   - compare expected source coverage, field/state facets, scope/non-goals and acceptance criteria independently. A claim that a requirement is "independently testable" alone is insufficient.
   These rows belong in candidate `semantic_review` and are checked by `product-requirement-boundary-review` during admission. The checker validates review completeness and consistency, **not** whether the reviewer's semantic judgment is true. A separate substantive reviewer should examine all decisions before merging.
18. Run `python -m harness.workspace.workspace validate-artifact` on the candidate.
19. When machine-addressable semantic acceptance is used, require explicit Authority ownership for candidate/source assertions and constrain admitted source Authorities to the accepted upstream production contract plus Product Requirements itself. Do not admit Domain, Architecture, Interface, Data or Implementation decisions as requirement evidence merely because they are available or stakeholder-confirmed.
20. Apply common semantic acceptance, register all capabilities actually satisfied by the artifact, then re-evaluate the target Consumer.

## Stop conditions

Create or preserve a Product Requirements Question when:

- two accepted stakeholder/product sources conflict;
- an observable behavior choice materially changes product meaning and has not
  been decided;
- a numeric/quality constraint is required but unknown;
- acceptance cannot be stated without deciding an upstream product fact;
- the proposed requirement can only be justified by an already-derived downstream design decision rather than an independent observable product need/choice.

Route downstream instead of deciding here when the unresolved issue is semantic
domain ownership, architecture, interface representation, persistence or
implementation detail.

## Output schema

`product-requirements/v1`.

The canonical artifact contains:

- `purpose`;
- non-empty `requirements`;
- for each requirement:
  - stable unique `id` beginning with `REQ-`;
  - one atomic normative `statement`;
  - `status: ACCEPTED` (no historical/retired entries);
  - non-empty `source_refs`;
  - optional `rationale`;
- optional `non_goals`.

Requirement IDs identify the accepted requirement, not its document position or technical implementation. Reasonable wording refinement does not require a new ID when the same normative requirement remains intact; materially different semantics must not silently reuse an old ID. Git history is the only routine historical record. Do not materialize an inactive requirements graveyard.

## Acceptance checks

- every relevant source/evidence statement has an explicit disposition during requirements production;
- every requirement-bearing source statement maps to one or more accepted requirements or to a blocking Question;
- no observable scope/time/cardinality/negative/NOT_REQUIRED constraint is silently dropped;
- true independent product obligations remain independently addressable; multiple fields/states/test examples of one contract do not force separate REQs;
- every accepted requirement is supported by evidence or explicit product decision;
- every normative requirement represents a changeable product obligation, with reviewed independence rationale rather than per-field/per-test atomization;
- every requirement has one stable unique `REQ-*` ID and non-empty source provenance;
- IDs are not reused for materially different requirement meaning;
- statements describe what the product must achieve, not how it is implemented;
- acceptance semantics are concrete enough for downstream design/verification and do not create product REQs for oracle construction or execution of tests;
- the mandatory classification review has one entry per candidate requirement and an explicit disposition for each relevant source statement, including test obligations and non-goals;
- non-goals prevent accidental scope expansion;
- Domain/Architecture/Interface decisions remain downstream and are not promoted upstream through wording, provenance shortcuts or stakeholder reconfirmation;
- unknown quality targets are not fabricated;
- the artifact genuinely provides every grouped CapabilityId being registered.

## Registration

Register the accepted project-native requirements artifact as one Core
`CanonicalArtifact` owned by Product Requirements.

Its `provides` may contain several capabilities from the grouped artifact work
when one accepted requirements artifact genuinely materializes them together.

Its dependencies identify the accepted Problem Evidence / product-policy
artifacts actually used.

## Human projection

Render the managed canonical artifact into a disposable human-readable Requirements document. The projection is for review; `.harness/knowledge/**` remains the source of truth.

## Established practice anchors

Use IREB CPRE (elicitation, documentation, validation), INCOSE *Guide to Writing Requirements* (necessary, singular, verifiable *obligations*), and GitHub Spec Kit's requirements-quality checklist distinction between *quality of requirements* and *testing implementation* as methodology, not as executable validators. See:
- https://cpre.ireb.org/en/concept/foundationlevel
- https://www.incose.org/group/requirements-working-group/
- https://github.com/github/spec-kit/blob/main/templates/commands/checklist.md

This skill does not require a particular PRD template, normative wording pattern or universal requirement count. Never import Spec Kit's assumed defaults when Harness needs a product owner decision.
