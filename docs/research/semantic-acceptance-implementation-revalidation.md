# Research — Semantic acceptance implementation and revalidation results

Status: research only. Not canonical. No main changes.

## Scope

This record closes the implementation/revalidation loop started by:

- `artifact-semantic-completeness-correctness.md`;
- `artifact-semantic-acceptance-experiment-results.md`;
- `artifact-semantic-acceptance-real-project-pilots.md`;
- `full-semantic-audit-napms-nutrition.md`;
- `semantic-audit-root-cause-analysis.md`;
- `prevention-vs-posthoc-semantic-audit.md`.

## Harness implementation

Research branch:

`research/artifact-semantic-completeness-correctness`

Implemented:

- `semantic_acceptance.py` as an above-Core semantic acceptance layer;
- subject-aware obligations and required-value coverage;
- provenance, ownership, source-fidelity, internal/cross-artifact contradiction checks;
- consumer compatibility obligations;
- optional bounded semantic review evidence;
- generated `harness-artifact-semantic-evaluation` evidence;
- capability realization gating on explicit semantic rejection;
- prerequisite-based semantic invalidation closure;
- Coverage action `REVALIDATE_SEMANTICS`;
- semantic-claim gating so ACCEPTED capability evidence exposes only explicitly accepted claims;
- backward-compatible migration mode for capabilities without semantic evaluation evidence;
- formal research contract `spec/semantic-acceptance/artifact-semantic-acceptance-v1.yaml`;
- strengthened Application Design, Data Design, Human Interface Design and Interface Contract artifact-skill acceptance rules;
- mandatory semantic acceptance regressions in `make harness-check`.

Regression suite covers all seven original direct audit findings plus:

- rejected upstream capability invalidates downstream capability;
- accepted revalidation restores the closure;
- accepted capability cannot expose undeclared/unaccepted Coverage claims.

Final Harness CI:

```text
harness core: success
head: 48536dc9ff00f402ac1cbde051b9b38a3f20ca68
```

## NAPMS repair

Branch:

`fix/semantic-audit-findings`

Draft PR: #166.

Canonical repairs:

1. System Architecture now exposes `ReadResourceDetail` with current/history semantics.
2. HTTP requirements now explicitly require:
   - clear Endpoint address;
   - replace/clear Site;
   - replace/clear OWNER/ADMINISTRATOR responsibility;
   - Resource detail current/history representation.
3. OpenAPI now materializes:
   - `DELETE /v1/resources/{resourceRef}/endpoints/{endpointRef}/address`;
   - `PUT /v1/resources/{resourceRef}/site`;
   - `PUT /v1/resources/{resourceRef}/responsibilities/{role}`;
   - Resource current/history view;
   - 413 Payload Too Large for request-body operations.
4. Resource UI now treats:
   - `AuthorityScopeRef` as immutable Resource identity context;
   - Endpoint address, Site and OWNER/ADMINISTRATOR responsibility as temporal current/history facts;
   - canonical data source as `GET /v1/resources/{resourceRef}`.
5. Frontend verification/test/implementation contracts were revalidated and updated to the corrected Resource semantics.
6. `check_openapi_contract.py` now enforces Resource operation completeness, ResourceView shape, 413 realization and UI/OpenAPI semantic compatibility.

Final NAPMS CI:

```text
design: success
architecture: success
Engineering Coverage: success
head: f09290f1a85b3c94c3a8f3beaeea6b18837b6360
```

## Nutrition repair

Branch:

`fix/semantic-audit-findings`

Draft PR: #42.

Canonical repairs:

1. Data Design no longer owns/copies SQLite, WAL, synchronous, SQLAlchemy or Alembic decisions.
   It now owns vendor-neutral relational representation/consistency semantics and leaves concrete realization to Implementation Design.
2. Frontend Application Contracts now define explicit:
   - `CreateMember(household_id, profile)`;
   - provider-owned opaque member identity generation;
   - atomic initial profile creation;
   - rejection/technical-failure behavior;
   - `SaveMemberProfile(household_id, member_id, profile)` only for existing identities.
3. User Journey, Human Interface, Verification, Test Design and Implementation Design now preserve the explicit create-vs-update lifecycle.
4. ADR-017 lifecycle wording was canonicalized.
5. During revalidation an additional missed defect was found: ADR-016 had the same pilot-branch lifecycle wording. It was also canonicalized.
6. A project regression test now:
   - scans all registered canonical artifact paths for pilot-branch acceptance wording;
   - prevents concrete Implementation Stack ownership from leaking back into Data Design;
   - requires explicit member creation semantics and corresponding test design.

Final Nutrition CI:

```text
CI: success
head: f246c783fbcdd339201d4a097f9f156b1a39d21a
```

## Revalidation result

All 77 registered canonical paths were rescanned for the failure classes that can be checked deterministically after the repair.

NAPMS canonical artifacts:

- no `PILOT_CURRENT` status remains;
- no accepted-artifact `Harness pilot branch` lifecycle wording remains;
- no canonical Resource UI artifact contains the superseded Responsibility Scope affiliation semantic;
- no canonical Resource UI artifact retains `GET /api/resources/{resourceId}`.

Nutrition canonical artifacts:

- no accepted-artifact `Harness pilot branch` lifecycle wording remains;
- Data Design contains no concrete SQLite/SQLAlchemy/Alembic/`synchronous=FULL` implementation-stack decisions;
- member creation is represented explicitly by the Application Design owner.

Affected semantic closure was re-reviewed after each repair.

Result:

```text
original material findings: closed
new deterministic lifecycle finding discovered during revalidation: ADR-016
ADR-016: closed
remaining material findings in repaired affected closure: 0
```

## Important research correction

The original "full" semantic audit missed ADR-016 even though it contained the same lifecycle defect as ADR-017.

That is evidence that manual/LLM whole-project audit alone is not sufficient.

The correction is architectural:

- deterministic finite scans must handle machine-addressable classes;
- semantic review handles residual meaning;
- full audit remains reconciliation/backstop.

This strengthens rather than weakens the hybrid strategy.

## Canonicalization readiness

Empirical evidence now includes:

- conceptual analysis;
- synthetic defect injection;
- real project pilots;
- full canonical-artifact audit;
- root-cause analysis;
- prevention-vs-audit cost analysis;
- working Harness implementation;
- real project defect repair;
- project CI revalidation;
- discovery of an audit omission caught by systematic deterministic scanning.

No Core expansion is required.

The semantic-acceptance mechanism is ready for a separate canonicalization change.
Research branch and project repair branches should not be merged automatically without an explicit canonicalization/merge decision.
