# Research — Root-cause analysis of semantic audit findings

Status: research only. Not canonical. No main changes.

Related audit:
- docs/research/full-semantic-audit-napms-nutrition.md

## Purpose

Explain why the semantic defects entered accepted canonical knowledge, why existing
Harness mechanisms did not stop them, which failures are project-local versus
systemic, and what can/cannot be checked deterministically.

---

# Executive conclusion

The defects are not one class of error.

They came from four independent failure modes:

1. **incomplete semantic invalidation after upstream replacement**;
2. **structural dependency validation without producer/consumer semantic compatibility**;
3. **ownership/provenance leakage across engineering Authorities**;
4. **capability existence treated as equivalent to subject-level semantic completeness**.

The common root is:

> Harness currently validates that the knowledge graph is structurally closed and
> that declared capabilities exist, but not that a realized artifact is a
> semantically valid realization of every obligation implied by those capabilities.

This is why the existing system could correctly answer "all required providers
exist" while the full semantic audit answered "some providers do not actually
provide the meaning their consumers require."

---

# 1. NAPMS: how the stale Resource UI arose

## Timeline

### 2026-09-19 — Resource-history UI is canonicalized

Commit:

- a79b2dc0 — "Finalize Harness pilot and engineering knowledge vertical (#146)"

The commit explicitly added:

- Resource history visibility gap;
- Resource-detail history query contract;
- Resource current/historical detail;
- Resource Detail UI contract;
- Resource history navigation;
- downstream verification/implementation routing.

At that point the Resource-history frontend work was derived from the then-active
Resource Catalogue semantics.

### 2026-09-20 — blind backend redesign replaces canonical backend/domain truth

Commit:

- a92b5d75 — "Promote repaired blind backend design to canonical main"

The commit explicitly:

- replaced strategic models;
- replaced tactical domain models;
- replaced system rules;
- replaced module contracts;
- replaced HTTP requirements;
- replaced OpenAPI;
- reconciled Resource Catalogue canonical layer;
- made the implementation Consumer backend-scoped.

The repaired Resource model established the current semantics:

- one immutable Resource AuthorityScopeRef;
- explicit ResourceEndpoint identities;
- Site history;
- OWNER/ADMINISTRATOR responsibility history.

The old UI semantic model was not rebuilt as part of that backend-scoped
replacement.

### 2026-09-21 — Engineering Coverage/frontend design is canonicalized

Commit:

- 63cc4001 — "Canonicalize NAPMS Engineering Coverage results"

The commit:

- bound semantic claims to canonical capabilities;
- completed backend concern decisions;
- added/canonicalized first-MVP frontend design;
- expected the frontend Harness target to be complete.

The Resource UI artifact inherited from the earlier vertical was reused as an
accepted provider.

No mechanism compared its meaning with the newly repaired Resource domain model
and newly replaced OpenAPI.

## Root cause

This is a **semantic invalidation failure**.

The canonical Resource model changed materially, but downstream invalidation was
effectively bounded by selected dependency/consumer scope rather than by changed
semantic assertions.

The graph knew that artifacts were connected, but it had no statement such as:

```text
RESOURCE-DETAIL-UI obligation:
  every displayed Resource fact must correspond to a currently accepted
  RC-DOMAIN public semantic assertion
```

and no assertion-level dependency such as:

```text
UI.Resource.scope-affiliation
  <- RC.Resource.AuthorityScopeRef semantics
```

Therefore no deterministic contradiction was visible to the graph.

## Why ordinary dependency closure did not save us

A file-level dependency edge says:

> this artifact used that artifact.

It does not say:

> this particular material assertion is supported by that particular upstream
> assertion and remains valid if the upstream assertion changes.

The replacement preserved enough artifact IDs/capabilities that the graph remained
structurally satisfiable.

The semantic identity underneath those capabilities changed.

---

# 2. NAPMS: why OpenAPI could be accepted while Resource behavior was incomplete

## Observation

Current accepted Resource Catalogue curation requires:

- register Resource;
- add Endpoint;
- set/replace/clear Endpoint address;
- maintain Site;
- maintain OWNER/ADMINISTRATOR responsibility;
- inspect current/history truth.

Current internal Module Contracts expose the corresponding application operations.

But current canonical HTTP/OpenAPI exposes only part of that behavior.

## Root cause

This is a **capability granularity failure**.

The graph had a capability equivalent to:

```text
engineering.interface.http-contract
```

and later semantic claims such as:

```text
engineering.interface.machine.contract
engineering.interface.machine.errors
engineering.interface.machine.compatibility
```

Those are broad capability/claim labels.

They do not encode subject-level obligations such as:

```text
for every externally required Resource Catalogue command:
    exactly one accepted external operation or explicit non-exposure decision exists

for every required Resource read model:
    the contract carries all required semantics
```

The presence of one valid OpenAPI artifact therefore satisfied the provider
boundary even if its operation set was incomplete.

## Why the existing completeness model did not catch it

Earlier completeness work was primarily **knowledge-family completeness**:

- tactical model exists;
- interface contract exists;
- verification exists;
- required capability provider exists.

It was not **semantic set closure inside the artifact**:

```text
expected operations - materialized operations = missing operations
```

The new semantic-acceptance research identifies precisely this missing level.

---

# 3. NAPMS: why the Resource Detail data contract drifted from OpenAPI

## Observation

Resource Detail declares a presentation data source and shape that canonical
OpenAPI does not provide.

## Root cause

This is a **cross-Authority contract compatibility failure**.

Interface Design was allowed to produce a human-interface contract while Machine
Interface Design independently provided OpenAPI.

The graph expressed that both existed and later frontend architecture consumed
both.

It did not validate the relation:

```text
human-interface required read model
  must be realizable from
machine-interface accepted operations/representations
```

There was no explicit compatibility obligation between the two outputs.

## Deeper design issue

"Both artifacts are inputs to Frontend Architecture" is too late.

Compatibility must be proved at the point where a consumer requires them jointly.

The consumer needs not only:

- capability A exists;
- capability B exists;

but also:

- A and B are mutually satisfiable for each required subject.

This requires **join obligations** or consumer-side acceptance constraints.

---

# 4. NAPMS 413 omission: why a simple mismatch survived

## Observation

HTTP requirements define payload-too-large = 413; OpenAPI omits it.

## Root cause

This is the simplest form of **materialization completeness failure**.

The HTTP-requirements artifact and OpenAPI are linked, but no deterministic
obligation currently asserts:

```text
every normative transport decision in HTTP-REQUIREMENTS
must have one matching OpenAPI realization or explicit N/A disposition
```

This particular defect is almost fully machine-checkable and should not require an
LLM once the obligation model exists.

It is evidence that even low-complexity semantic completeness is currently not
systematically checked.

---

# 5. Nutrition: why Data Design copied Implementation Stack decisions

## Timeline

### 2026-09-15 — implementation stack selected

Commit:

- b09ce292 — "Authorize first implementation slice (#6)"

Concrete S4 choices included Python, SQLite, SQLAlchemy, PySCIPOpt and associated
database mechanics.

### 2026-09-20 — implementation-readiness artifacts are materialized

Commit:

- f3e223f0 — "Complete MVP implementation-readiness design"

The same commit introduced/registered:

- APPLICATION-DESIGN;
- DATA-DESIGN;
- CLI-CONTRACT;
- IMPLEMENTATION-STACK;
- implementation plan/completion artifacts.

The graph declared:

```text
DATA-DESIGN
  depends_on:
    TARGET-ARCHITECTURE
    APPLICATION-DESIGN
```

while Data Design text itself embedded:

- SQLite;
- WAL;
- synchronous=FULL;
- read_uncommitted settings.

Those details were already owned by IMPLEMENTATION-STACK.

## Root cause

This is an **Authority ownership/provenance failure**.

The authoring process used known project context beyond the artifact's declared
upstream semantic inputs.

The structural ownership checks prevented obvious path/write violations, but did
not detect copied semantic decisions in prose.

## Why the graph remained valid

There is no literal path reference to IMPLEMENTATION-STACK required for the
semantic leak to exist.

The invalid dependency is semantic:

```text
Data Design statement "SQLite + WAL + synchronous=FULL"
is derived from Implementation Design truth
```

but the graph only knows file/artifact dependencies.

This confirms that provenance must eventually exist at material assertion level,
at least for assertions that establish capabilities.

---

# 6. Nutrition: why Add Member has no complete application contract

## Timeline

Commit:

- 454307e1 — "Design user-facing frontend with Harness (#34)"

One change canonicalized the complete frontend vertical:

- frontend requirements;
- journeys;
- application contracts;
- human-interface design;
- security;
- architecture;
- component design;
- verification;
- test design;
- implementation design.

The requirement/journey introduced "add a household member".

The Application Contract introduced `SaveMemberProfile(household_id, profile)`
and described it as creating or replacing a profile "for that member".

No separate identity/lifecycle rule for creation of a new Household Member was
defined.

## Root cause

This is a **subject-instance completeness failure hidden by a plausible aggregate
operation name**.

The artifact had a command that looked close enough to satisfy the journey.

But the required semantic obligations are distinct:

1. create/establish member identity;
2. attach/replace current Nutrition Profile for that member.

The current contract fully describes only the second semantic concept.

## Why downstream verification did not catch it

Verification and Test Design inherited the same abstraction.

They test:

- valid profile save;
- invalid profile rejection;

but not:

- first creation of a previously nonexistent member identity;
- identity generation/ownership;
- duplicate identity/conflict semantics.

This demonstrates an important rule:

> A downstream test design cannot repair an omission that was already normalized
> away by an incomplete application contract.

Requirement selection must compare required behaviors against semantic operations,
not merely against nearby contract names.

---

# 7. Nutrition ADR-017 status drift: why lifecycle metadata became contradictory

## Timeline

The ADR was created during the Harness pilot and explicitly marked:

```text
accepted for the Harness pilot branch
```

Later Harness integration registered it as a current canonical provider in main.

The content status was not rewritten.

## Root cause

This is a **canonicalization transition failure**.

Promotion to canonical truth changed repository/graph status but did not validate
artifact-internal lifecycle declarations.

## Why this matters

Canonical registration and artifact self-declaration are two independent
representations of acceptance state.

Without an invariant linking them, they can diverge.

This class is deterministic:

```text
canonical provider in main
AND self-status says branch/pilot-only
=> contradiction
```

It should not need semantic review once lifecycle/status vocabulary is constrained.

---

# Cross-cutting systemic causes

## A. Artifact existence is stronger in the current model than artifact acceptance

The current path is effectively:

```text
artifact exists
+ graph registration
+ provider capability
+ no structural blocker
=> capability usable
```

What is missing is:

```text
artifact exists
+ structural validity
+ semantic acceptance for its production contract
=> capability usable
```

This is the principal architectural gap.

## B. Revalidation follows artifact/capability edges, not changed semantic assertions

When a large canonical replacement keeps the same artifact IDs or capability
names, the graph may see no reason to invalidate downstream meaning.

Needed future mechanism:

```text
changed accepted semantic assertion
-> affected assertion provenance edges
-> affected artifact obligations
-> downstream acceptance invalidation
```

A coarse first implementation can invalidate all direct/downstream consumers of a
changed provider capability; a later implementation can narrow this by assertion
provenance.

## C. Capabilities are too coarse to prove completeness by themselves

A capability such as "HTTP contract" or "application contracts" identifies a kind
of accepted knowledge.

It does not prove:

- every required operation exists;
- every required entity/subject is covered;
- every required error is represented;
- every upstream invariant is preserved.

Therefore capabilities must remain routing units, not semantic-completeness units.

## D. Authority write isolation is not semantic provenance isolation

An Authority can obey all path/write rules while copying or inventing a decision
owned elsewhere.

Semantic acceptance therefore needs a non-invention/provenance check in addition
to write-set enforcement.

## E. Coverage currently trusts production claims too early

Coverage semantic claims represent intended meaning of a provider.

Without semantic acceptance evidence, the evaluator cannot distinguish:

```text
provider intends to cover concern X
```

from:

```text
provider has correctly and completely materialized concern X
```

This caused the false-confidence path exposed by NAPMS.

---

# What Harness should change

These are research conclusions, not yet canonical changes.

## P0 mechanism 1 — semantic acceptance must gate capability realization

A capability realization is usable only when:

```text
artifact registered
AND structural validation passes
AND required semantic obligations are complete
AND deterministic semantic checks pass
AND no unresolved contradiction/provenance defect exists
AND required semantic review is accepted
```

Only then may its semantic claims be consumed by Engineering Coverage.

## P0 mechanism 2 — artifact-kind production contracts need semantic obligations

Examples:

### HTTP contract

- all required externally exposed operations represented;
- input/output semantics represented;
- accepted error semantics represented;
- authorization/idempotency/concurrency semantics represented where applicable;
- compatibility contract represented.

### Application contract

- every selected user/application behavior has a material operation;
- required subject identity/lifecycle semantics are explicit;
- domain versus technical outcomes are explicit.

### Human-interface contract

- every displayed/edited domain fact maps to current provider semantics;
- every required interaction maps to an accepted application/machine operation;
- presentation must not invent domain entities.

### Data Design

- every persistent semantic fact traces to an accepted owner;
- implementation-vendor details require an allowed owner/input;
- no downstream implementation choice is copied into upstream design.

## P0 mechanism 3 — subject-level completeness

Obligations must quantify over required subjects:

```text
for every required Resource curation command ...
for every frontend journey action ...
for every normative HTTP error ...
for every persisted aggregate ...
for every selected requirement ...
```

Without this, "some operation exists" can masquerade as complete capability.

## P1 mechanism 4 — transition/canonicalization checks

Promotion or replacement should validate:

- self-declared status;
- graph registration status;
- branch/pilot wording;
- supersession markers;
- downstream affected closure.

## P1 mechanism 5 — consumer join constraints

When a consumer requires two capabilities jointly, Harness needs to permit an
acceptance obligation over the pair.

Example:

```text
Frontend Architecture requires:
  Human Interface
  HTTP Contract

join obligation:
  every required Human Interface server interaction is realizable by HTTP Contract
```

This cannot be represented by independent provider existence checks alone.

---

# Limits: what can be guaranteed and what cannot

There are real limits. The goal should not be to pretend arbitrary engineering
semantics can be formally proven.

## Deterministically checkable

With structured obligations, Harness can reliably check:

- missing required subjects/operations;
- cardinality;
- declared error/status coverage;
- identifier/reference consistency;
- lifecycle/status contradictions;
- dependency/provenance declaration;
- ownership violations where assertions are structured;
- forbidden dependencies;
- selected requirement-to-test traceability;
- exact enum/state coverage;
- canonical API/UI operation mapping where contracts are structured;
- contradiction against machine-readable invariants.

These should eventually be hard gates.

## Semantically reviewable but not generally formally provable

Natural-language artifacts can require interpretation for:

- whether a paraphrase preserves upstream meaning;
- whether two differently worded rules contradict;
- whether a proposed abstraction subtly broadens/narrows scope;
- whether an engineering decision is justified by inputs;
- whether an omission is material rather than intentional.

LLM/agent review is suitable here, but its output is evidence, not mathematical
proof.

Reliability improves when the review is constrained by:

- explicit expected obligations;
- bounded upstream context;
- Authority ownership;
- assertion provenance;
- deterministic checks first;
- adversarial contradiction pass;
- independent second review where material.

## Outside the internal semantic audit unless explicitly sourced

Harness cannot independently guarantee:

- scientific correctness of nutrition standards;
- correctness of an external legal/industry standard;
- truth of stakeholder statements;
- correctness of external source data;
- real runtime behavior before executable evidence exists.

It can guarantee that accepted project artifacts preserve the accepted sources and
do not silently invent or contradict them.

## Scope limitation of the completed audit

The completed audit covered registered canonical artifacts.

It did not treat:

- legacy docs;
- generated projections;
- implementation code;
- unregistered files

as independent canonical truth.

Implementation code may reveal a design gap, but it cannot resolve which design
meaning is canonical.

## Historical-cause limitation

Commit history provides strong evidence for when a semantic state entered or was
replaced.

It cannot always prove the human/agent mental reason for a choice.

The root causes in this document are therefore mechanism-level causal explanations
supported by repository transitions, not claims about private intent.

---

# Are there fundamental blockers?

No fundamental blocker prevents Harness from catching the concrete defects found
in this audit.

All seven direct findings can be prevented with a combination of:

- artifact-kind semantic obligations;
- subject-level completeness;
- cross-provider join checks;
- canonicalization status checks;
- semantic provenance;
- downstream invalidation.

The hard limit starts only at unrestricted natural-language entailment and
external truth.

Therefore the right target is not "formal proof of all engineering correctness".

The practical target is:

> Make every material engineering claim either deterministically provable from
> accepted structured knowledge, or explicitly subject to bounded semantic review
> with provenance and a visible uncertainty boundary.

That is sufficient to prevent the failure modes observed here without turning
Harness Core into a universal ontology or theorem prover.

# Recommended next experiment

Before fixing project defects, encode these seven real findings as regression
fixtures for the research semantic-acceptance evaluator.

Success criterion:

1. every existing real defect is detected;
2. the corresponding repaired artifact passes;
3. downstream capabilities become unusable while upstream semantic acceptance is
   invalid;
4. Engineering Coverage cannot report the affected concern COVERED;
5. no project-specific filename heuristic is required.

If that succeeds, the research has enough empirical evidence to propose
canonicalization of the semantic-acceptance layer.
