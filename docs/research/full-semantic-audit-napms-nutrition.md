# Research — Full semantic audit of NAPMS and Nutrition canonical artifacts

Status: research only. Not canonical. No main changes.

Audit baseline:

- Nutrition Management main: `ac8f30131baf5659eeacfeddf4d927f7451dc16b`
- NAPMS main: `503d2bb597c869c40ad43ae40cc9e294f12a1262`
- Harness research branch: `research/artifact-semantic-completeness-correctness`

## Scope

This audit covers every artifact registered as current canonical project knowledge in:

- Nutrition Management `.harness/graph.yaml`: 39 artifacts;
- NAPMS `docs/canonical-graph.yaml`: 38 nodes.

Total audited canonical artifacts: **77**.

The audit evaluates semantic consistency against accepted project truth and
declared producer/consumer dependencies. It does not use implementation code as
design authority and does not attempt to independently re-prove external
scientific or standards facts beyond their accepted canonical source evidence.

Checks applied:

1. capability fit;
2. completeness for downstream consumer obligations;
3. fidelity to upstream accepted semantics;
4. ownership/Authority boundaries;
5. dependency/provenance closure;
6. internal contradiction;
7. cross-artifact contradiction;
8. subject coverage where the consumer expects a set of subjects;
9. semantic-claim safety for Engineering Coverage.

Statuses:

- `PASS`: no material semantic defect found in the audited acceptance boundary;
- `FINDING`: direct semantic defect found in this artifact;
- `IMPACTED`: no independent defect required to explain the problem, but the
  artifact cannot be considered fully accepted while an upstream finding remains.

## Executive result

The existing canonical knowledge is **not semantically clean**.

Direct findings:

- NAPMS: 4 material findings, including P0 defects;
- Nutrition: 3 material findings, all P1 in the audited baseline.

The strongest failures are cross-artifact failures rather than document-local
errors. Structural graph completeness currently allows downstream canonical
artifacts and Coverage claims to remain green even where their semantic inputs
cannot actually support them.

---

# NAPMS

## P0 — NAPMS-SEM-001 — canonical Resource UI uses superseded Resource semantics

Affected artifact:

- `RESOURCE-DETAIL-UI` — `docs/contracts/ui/resource-detail.yaml`.

Current canonical Resource Catalogue semantics say:

- every Resource has one required immutable `AuthorityScopeRef`;
- Site is a separate historical Resource fact;
- Resource Responsibility is a separate OWNER/ADMINISTRATOR historical fact;
- `AuthorityScopeRef` is not a temporal Responsibility Scope affiliation.

Those rules are established by the current canonical chain:

- `RC-CURATION`;
- `RC-LANGUAGE`;
- `RC-DECISIONS`;
- `RC-PROCESS`;
- `RC-DOMAIN`.

But `RESOURCE-DETAIL-UI` requires:

- current "Responsibility Scope affiliations";
- historical "scope affiliations";
- ended/replaced scope-affiliation history.

That semantic object does not exist in the current canonical Resource model.

### Consequence

The Interface Design artifact is deciding against its canonical domain provider.
A frontend implementation must choose between two incompatible meanings.

### Required disposition

`RESOURCE-DETAIL-UI` must be rejected as currently semantically accepted.

Repair should re-derive current/history presentation from:

- immutable `AuthorityScopeRef`;
- Site history;
- OWNER/ADMINISTRATOR responsibility history;
- Endpoint/address history.

No implementation should preserve the obsolete affiliation model merely because
legacy code currently has such concepts.

## P0 — NAPMS-SEM-002 — canonical HTTP contract cannot realize accepted Resource curation

Affected artifacts:

- `HTTP-REQUIREMENTS` — `docs/contracts/http/napms-api-requirements.yaml`;
- `OPENAPI` — `docs/contracts/http/napms.openapi.yaml`.

Accepted Resource curation semantics require supported behavior for:

- register Resource with immutable `AuthorityScopeRef`;
- add Endpoint;
- set/replace Endpoint HOST/PREFIX realization;
- clear current Endpoint realization;
- maintain Site with history;
- maintain OWNER/ADMINISTRATOR responsibility with history;
- inspect current Resource truth/history.

The in-process `MODULE-CONTRACTS` explicitly include:

- `SetSite`;
- `SetResponsibility`;
- `ClearEndpointAddress`;
- current Resource queries.

The canonical HTTP contract exposes only a subset:

- create/get Resource;
- add Endpoint;
- set Endpoint Address;
- other non-Resource first-MVP operations.

It provides no public operation for:

- clearing Endpoint address;
- changing/clearing Site;
- changing/clearing OWNER/ADMINISTRATOR responsibility;
- inspecting the required history.

### Consequence

The first-MVP external application API is semantically incomplete relative to
accepted Product/Domain/Application requirements.

This is particularly severe because NAPMS currently binds
`engineering.interface.http-contract` to:

- `engineering.interface.machine.contract`;
- `engineering.interface.machine.errors`;
- `engineering.interface.machine.compatibility`.

Engineering Coverage can therefore derive a false `COVERED` state from a
canonical artifact that does not materialize the complete required interface
semantics.

### Required disposition

`HTTP-REQUIREMENTS` and `OPENAPI` must not provide usable generic interface
Coverage proof until the missing Resource curation surface is either:

1. added to the canonical application API; or
2. explicitly removed/deferred by an upstream accepted product/interface decision.

## P0 — NAPMS-SEM-003 — Resource Detail declares a data contract absent from canonical OpenAPI

Affected artifacts:

- `RESOURCE-DETAIL-UI`;
- transitively the frontend canonical chain.

`RESOURCE-DETAIL-UI` declares:

```text
GET /api/resources/{resourceId}
ResourceDetail.resourceId
ResourceDetail.current
ResourceDetail.history
```

The canonical OpenAPI instead declares:

```text
GET /v1/resources/{resourceRef}
-> ResourceView
```

and `ResourceView` contains only the current summary fields required by that
schema; it does not contain the UI-declared `current/history` shape.

The frontend architecture explicitly states that frontend integration uses the
canonical OpenAPI API only.

### Consequence

The UI contract has no accepted upstream machine contract capable of supplying
its declared data.

This is not a route spelling issue. The required representation semantics are
also absent.

### Required disposition

Reconcile Interface Design and HTTP contract before accepting downstream frontend
architecture/implementation readiness.

## P1 — NAPMS-SEM-004 — HTTP requirements require 413 but OpenAPI omits it

`HTTP-REQUIREMENTS` defines:

```text
payload_too_large: 413
```

The canonical OpenAPI contains no 413 response contract.

### Consequence

The intended HTTP error semantic is not fully realized by the artifact currently
claiming `engineering.interface.machine.errors`.

### Required disposition

Either materialize 413 where applicable in OpenAPI or remove/change the
requirement through Interface Design.

## NAPMS downstream impact

The following artifacts inherit P0 semantic uncertainty from the broken
UI/OpenAPI frontier:

- `MVP-UI-NAVIGATION`;
- `FRONTEND-HUMAN-INTERFACE`;
- `FRONTEND-ARCHITECTURE`;
- `FRONTEND-COMPONENT-DESIGN`;
- `FRONTEND-VERIFICATION`;
- `FRONTEND-TEST-DESIGN`;
- `FRONTEND-IMPLEMENTATION-DESIGN`.

Their local responsibilities are generally coherent, but they cannot collectively
prove frontend readiness while their required UI/API semantics are inconsistent.

## NAPMS artifacts with no additional material finding

The audit found no separate material semantic defect in:

- FIRST-MVP-REQUIREMENTS;
- RC-DISCOVERY;
- STRATEGIC-CAPABILITIES;
- STRATEGIC-CONTEXTS;
- STRATEGIC-RELATIONSHIPS;
- RC-CURATION;
- RC-LANGUAGE;
- RC-DECISIONS;
- RC-PROCESS;
- RC-DOMAIN;
- AM-LANGUAGE;
- ACC-DOMAIN;
- AD-DOMAIN;
- BC-DOMAIN;
- AP-DOMAIN;
- FIRST-MVP-JOURNEY;
- C4-STRUCTURE;
- SYSTEM-RULES;
- SECURITY-ARCHITECTURE;
- MODULE-CONTRACTS;
- TECH-REPRESENTATION;
- PERSISTENCE;
- QUALITY-REQUIREMENTS;
- MVP-QUALITY-TARGETS;
- THREAT-MODEL;
- OBSERVABILITY;
- MVP-IMPLEMENTATION-READINESS;
- MVP-TEST-INTENT.

This means no defect was demonstrated by this audit. It is not a claim of
mathematical truth for unrestricted prose.

---

# Nutrition Management

## P1 — NUTRITION-SEM-001 — Data Design steals/duplicates concrete Implementation Stack decisions

Affected artifact:

- `DATA-DESIGN` — `docs/data/data-design.md`.

The canonical responsibility split says:

- S3 / Data Design owns persistence representation and semantic persistence
  contracts;
- Implementation Design / `IMPLEMENTATION-STACK` owns concrete stack choices.

`ADR-010` explicitly owns the first-slice choice of:

- SQLite;
- WAL;
- `synchronous=FULL`;
- SQLAlchemy Core;
- Alembic;
- exact first-slice database mechanics.

But `DATA-DESIGN` itself states the concrete first-slice SQLite/WAL settings.

At the same time its Core dependencies are only:

- TARGET-ARCHITECTURE;
- APPLICATION-DESIGN.

It does not depend on `IMPLEMENTATION-STACK`.

### Consequence

Two problems occur:

1. concrete implementation truth is duplicated across semantic owners;
2. Data Design uses a concrete choice without declared provenance/dependency.

A later stack replacement can leave accepted Data Design silently stale.

### Required disposition

Keep Data Design vendor/mechanism-neutral where possible and move the concrete
SQLite/WAL mechanics to Implementation Design/Stack, or formally redesign the
ownership/dependency direction without introducing a lifecycle cycle.

The first option is preferred because it preserves the existing Authority
responsibilities.

## P1 — NUTRITION-SEM-002 — frontend supports “add member” but no accepted member-identity creation contract exists

Affected artifacts:

- `FRONTEND-USER-JOURNEYS`;
- `FRONTEND-APPLICATION-CONTRACTS`;
- downstream frontend design.

Accepted frontend requirements require creating/updating the current Nutrition
Profile per member.

The accepted journey explicitly says:

```text
add a household member or open an existing member
```

The Application Contract exposes:

- `ListMemberProfiles(household_id)`;
- `GetMemberProfile(household_id, member_id)`;
- `SaveMemberProfile(household_id, profile)`.

It says `SaveMemberProfile` creates/replaces a profile "for that member", but
does not decide:

- how a new Household Member identity is created;
- who chooses/generates `member_id`;
- whether creating the first profile implicitly creates Member identity;
- what duplicate/conflict semantics apply;
- whether member lifecycle is a distinct application command.

### Consequence

The presentation/implementation layer must invent a material Nutrition Targeting
application semantic to implement the accepted Add Member journey.

That violates the rule that frontend adapters do not create domain/application
truth.

### Required disposition

APPLICATION-DESIGN / Nutrition Targeting must define the minimal accepted member
creation/identity contract before the Add Member frontend slice is considered
implementation-ready.

## P1 — NUTRITION-SEM-003 — canonical provider still describes its acceptance as pilot-branch scoped

Affected artifact:

- `GAP-SUGGESTION-RANKING-DECISION` —
  `docs/decisions/ADR-017-gap-suggestion-energy-density-fallback.md`.

The artifact is registered in the current main canonical graph and resolves a
Core Question, but its status text says:

```text
accepted for the Harness pilot branch
```

### Consequence

The same artifact is simultaneously represented as:

- current canonical accepted project truth by Core registration; and
- branch-scoped experimental acceptance by its own semantic content.

That makes acceptance provenance ambiguous.

### Required disposition

Either canonicalize its lifecycle/status wording for current main truth or stop
registering it as an accepted current provider.

## Nutrition downstream impact

`NUTRITION-SEM-002` affects the frontend chain that consumes the incomplete
application contract, particularly:

- FRONTEND-HUMAN-INTERFACE;
- FRONTEND-ARCHITECTURE;
- FRONTEND-COMPONENT-DESIGN;
- FRONTEND-VERIFICATION-DESIGN;
- FRONTEND-TEST-DESIGN;
- FRONTEND-IMPLEMENTATION-DESIGN.

The existing frontend Test Design tests profile success/rejection, but does not
close the missing new-member identity contract.

## Nutrition artifacts with no additional material finding

No separate material semantic defect was demonstrated in:

- PROBLEM;
- PRODUCT-REQUIREMENTS;
- STRATEGIC-DOMAIN;
- CONTEXT-MAP;
- NUTRITION-TARGETING-DOMAIN;
- FOOD-KNOWLEDGE-DOMAIN;
- MARKET-CATALOG-DOMAIN;
- PURCHASE-PLANNING-DOMAIN;
- NUTRIENT-EVIDENCE-SEMANTICS;
- FOOD-CATEGORY-TAXONOMY;
- BLS-V4-SOURCE-BASELINE;
- BLS-V4-EVIDENCE-SEMANTICS;
- BLS-V4-ERRATA-POLICY;
- BLS-V4-CATEGORY-ASSIGNMENT-DECISION;
- TARGET-ARCHITECTURE;
- VERIFICATION-STRATEGY;
- APPLICATION-DESIGN;
- CLI-CONTRACT;
- COMPONENT-DESIGN;
- IMPLEMENTATION-STACK;
- FRONTEND-REQUIREMENTS;
- FRONTEND-DELIVERY-DECISION;
- FRONTEND-SECURITY;
- FRONTEND-OPERABILITY-DESIGN;
- FRONTEND-SECURITY-ANALYSIS;
- REDESIGN-VERIFICATION-DESIGN;
- REDESIGN-TEST-DESIGN;
- REDESIGN-IMPLEMENTATION-DESIGN;
- ENGINEERING-DESIGN-POLICY.

Again, this is the result of the current bounded semantic audit, not an assertion
that arbitrary natural-language or external scientific truth has been formally
proved.

---

# Full artifact disposition register

## NAPMS

| Artifact | Audit status | Reason |
|---|---|---|
| FIRST-MVP-REQUIREMENTS | PASS | No material inconsistency found |
| RC-DISCOVERY | PASS | Aligned with current Resource curation semantics |
| STRATEGIC-CAPABILITIES | PASS | Ownership model coherent |
| STRATEGIC-CONTEXTS | PASS | Ownership model coherent |
| STRATEGIC-RELATIONSHIPS | PASS | Provider/consumer semantics coherent |
| RC-CURATION | PASS | Aligned with Product/Resource model |
| RC-LANGUAGE | PASS | Current vocabulary coherent |
| RC-DECISIONS | PASS | Current Resource decisions coherent |
| RC-PROCESS | PASS | Process matches current Resource semantics |
| RC-DOMAIN | PASS | Tactical model coherent |
| AM-LANGUAGE | PASS | Authority semantics separated from Resource metadata |
| ACC-DOMAIN | PASS | No material finding |
| AD-DOMAIN | PASS | No material finding |
| BC-DOMAIN | PASS | No material finding |
| AP-DOMAIN | PASS | No material finding |
| FIRST-MVP-JOURNEY | PASS | Cross-context composition coherent |
| C4-STRUCTURE | PASS | Structure matches backend/frontend/dependency model |
| SYSTEM-RULES | PASS | Reliability/consistency semantics explicit |
| SECURITY-ARCHITECTURE | PASS | Security semantics explicit |
| MODULE-CONTRACTS | PASS | Internal contracts cover current Resource operations |
| TECH-REPRESENTATION | PASS | Representation ownership coherent |
| HTTP-REQUIREMENTS | FINDING P0 | Incomplete Resource curation interface |
| OPENAPI | FINDING P0/P1 | Missing required operations/history and 413 realization |
| MVP-UI-NAVIGATION | IMPACTED | Depends on unresolved Resource UI/API frontier |
| RESOURCE-DETAIL-UI | FINDING P0 | Stale domain semantics and nonexistent data contract |
| PERSISTENCE | PASS | No material finding |
| QUALITY-REQUIREMENTS | PASS | Explicit qualitative targets/constraints |
| MVP-QUALITY-TARGETS | PASS | Product provenance preserved |
| THREAT-MODEL | PASS | Threat/security obligations explicit |
| OBSERVABILITY | PASS | Logging/config/health/incident boundaries explicit |
| MVP-IMPLEMENTATION-READINESS | PASS | Backend readiness locally coherent |
| MVP-TEST-INTENT | PASS | Requirement/evidence coverage locally coherent |
| FRONTEND-HUMAN-INTERFACE | IMPACTED | Consumes inconsistent UI/API baseline |
| FRONTEND-ARCHITECTURE | IMPACTED | Canonical API cannot satisfy selected UI contract |
| FRONTEND-COMPONENT-DESIGN | IMPACTED | Same upstream defect |
| FRONTEND-VERIFICATION | IMPACTED | Cannot prove impossible/inconsistent upstream contract |
| FRONTEND-TEST-DESIGN | IMPACTED | Same upstream defect |
| FRONTEND-IMPLEMENTATION-DESIGN | IMPACTED | Frontend readiness not semantically closed |

## Nutrition Management

| Artifact | Audit status | Reason |
|---|---|---|
| REDESIGN-VERIFICATION-DESIGN | PASS | No material finding |
| REDESIGN-TEST-DESIGN | PASS | No material finding |
| REDESIGN-IMPLEMENTATION-DESIGN | PASS | No material finding |
| ENGINEERING-DESIGN-POLICY | PASS | No material finding |
| PROBLEM | PASS | No material finding |
| PRODUCT-REQUIREMENTS | PASS | Consistent with problem/scope |
| STRATEGIC-DOMAIN | PASS | Context ownership coherent |
| CONTEXT-MAP | PASS | Provider/consumer semantics coherent |
| NUTRITION-TARGETING-DOMAIN | PASS | No material finding |
| FOOD-KNOWLEDGE-DOMAIN | PASS | No material finding |
| MARKET-CATALOG-DOMAIN | PASS | No material finding |
| PURCHASE-PLANNING-DOMAIN | PASS | No material finding |
| NUTRIENT-EVIDENCE-SEMANTICS | PASS | Evidence/mapping distinctions coherent |
| FOOD-CATEGORY-TAXONOMY | PASS | No material finding |
| BLS-V4-SOURCE-BASELINE | PASS | Canonical source identity internally coherent |
| BLS-V4-EVIDENCE-SEMANTICS | PASS | No material finding |
| BLS-V4-ERRATA-POLICY | PASS | No material finding |
| BLS-V4-CATEGORY-ASSIGNMENT-DECISION | PASS | No material finding |
| GAP-SUGGESTION-RANKING-DECISION | FINDING P1 | Branch-scoped acceptance text in main canonical provider |
| TARGET-ARCHITECTURE | PASS | No material finding |
| VERIFICATION-STRATEGY | PASS | No material finding |
| APPLICATION-DESIGN | PASS | No material finding |
| DATA-DESIGN | FINDING P1 | Concrete S4 stack decisions duplicated without dependency |
| CLI-CONTRACT | PASS | No material finding |
| COMPONENT-DESIGN | PASS | No material finding |
| IMPLEMENTATION-STACK | PASS | Correct owner of concrete stack |
| FRONTEND-REQUIREMENTS | PASS | User outcomes explicit |
| FRONTEND-USER-JOURNEYS | PASS | Journey intent valid; exposes downstream contract gap |
| FRONTEND-APPLICATION-CONTRACTS | FINDING P1 | Missing Add Member identity/application semantic |
| FRONTEND-HUMAN-INTERFACE | IMPACTED | Add Member action lacks complete application contract |
| FRONTEND-DELIVERY-DECISION | PASS | No material finding |
| FRONTEND-SECURITY | PASS | No material finding |
| FRONTEND-ARCHITECTURE | IMPACTED | Selected frontend includes unresolved member-creation slice |
| FRONTEND-COMPONENT-DESIGN | IMPACTED | Same upstream semantic gap |
| FRONTEND-OPERABILITY-DESIGN | PASS | No material finding |
| FRONTEND-SECURITY-ANALYSIS | PASS | No material finding |
| FRONTEND-VERIFICATION-DESIGN | IMPACTED | Add Member obligation cannot be completely traced |
| FRONTEND-TEST-DESIGN | IMPACTED | No contract closing member-identity creation behavior |
| FRONTEND-IMPLEMENTATION-DESIGN | IMPACTED | Full frontend target is not semantically implementation-ready |

---

# Harness implications confirmed by the audit

The audit validates the original semantic-acceptance research with real defects.

## 1. Structural COMPLETE is insufficient

Both projects can have structurally registered providers while semantic producer /
consumer contracts disagree.

## 2. Coverage can false-positive without semantic acceptance

NAPMS is the concrete counterexample:

```text
OPENAPI exists
+ capability provides engineering.interface.http-contract
+ semantic claim binding exists
=> current Coverage may accept interface.machine.contract

but

accepted Resource behavior
- missing public interface semantics
!= semantically complete interface contract
```

## 3. Artifact dependency lists are insufficient for provenance correctness

Nutrition Data Design demonstrates that an artifact can contain downstream
implementation decisions without declaring the semantic owner it copied them
from.

## 4. Downstream closure must invalidate transitively

When an upstream semantic provider is rejected, downstream artifacts that require
that meaning must become unusable until revalidated. They should not all be
rewritten automatically; they should be marked affected and reevaluated after the
owner repairs canonical truth.

## 5. Semantic audit should create Questions for unresolved choices

For the findings above, automatic “repair” by the auditor would be incorrect
where more than one valid upstream decision exists.

The appropriate operational model remains:

```text
semantic finding
-> owning Authority
-> Question if a decision is required
-> canonical repair
-> semantic revalidation
-> downstream revalidation
-> Coverage recomputation
```

# Audit conclusion

The answer to the practical question is:

> No, the existing artifacts are not all semantically correct and complete.

The audit found real defects that existing structural validation and Engineering
Coverage did not prevent.

Most importantly, the NAPMS interface/frontend frontier demonstrates an actual
false-confidence path that the proposed semantic acceptance layer is intended to
close.

No changes should be merged to `main` from this research branch automatically.
The next step is to repair the project-owned canonical defects in their own
branches, then rerun this audit and use the results as acceptance evidence for
canonicalizing the Harness semantic-acceptance mechanism.
