# Research — Coverage Planner pilot results

Status: research only. No main/canonical changes.

## Purpose

Test whether activated Engineering Concerns can be turned into an algorithmic work plan:

```text
activated concern
  -> accepted semantic claim
  -> capable Authority role
  -> project Authority
  -> missing semantic production
  -> work item / completion blocker
```

The manually reviewed coverage maps are used only as research oracles. They are not planning inputs.

## NAPMS

Activated unresolved concerns in the current research overlay: 9.

| Concern | Derived planning result | Route |
|---|---|---|
| interface.human.journeys | MISSING | HUMAN-INTERFACE-DESIGN |
| verification.interface.human | MISSING | VERIFICATION-DESIGN |
| data.lifecycle | MISSING | DATA-DESIGN |
| data.classification | MISSING | DATA-DESIGN |
| security.vulnerability-management | MISSING | SECURITY-ANALYSIS |
| security.secure-development | MISSING | SECURITY-ANALYSIS |
| reliability.recovery | MISSING | SYSTEM-ARCHITECTURE through reliability role |
| operability.incident | MISSING | OPERABILITY-DESIGN |
| quality.performance.resource-efficiency | MISSING | QUALITY-DESIGN |

Result:
- routable missing work: 9;
- structurally unroutable: 0;
- completion gate: false.

Interpretation: NAPMS already has Authorities whose responsibility can own all currently activated gaps. The planner does not need new project Authorities for these nine concerns; it needs finer semantic outputs from existing Authorities.

## Nutrition

Activated unresolved concerns in the current research overlay: 16.

Routable to existing Authorities:

| Concern | Result | Route |
|---|---|---|
| data.classification | MISSING | DATA-DESIGN |
| data.lifecycle | MISSING | DATA-DESIGN |
| reliability.availability | MISSING | ARCHITECTURE through reliability role |
| reliability.recovery | MISSING | ARCHITECTURE through reliability role |

Structurally unroutable under the current role bindings:

| Concern group | Count | Missing responsibility role |
|---|---:|---|
| security threat/vulnerability/secure-development | 3 | security-analysis |
| operability logging/metrics/tracing/health/alerting | 5 | operability |
| governance privacy/data | 2 | governance |
| performance latency/resource-efficiency | 2 | quality |

Result:
- routable missing work: 4;
- blocked by missing project role assignment: 12;
- completion gate: false.

Important: `ASSIGN_AUTHORITY` does not automatically mean "create a new Authority". It means the project graph currently has no Authority explicitly bound to a reusable role competent to produce that semantic claim. Resolution may be:
1. bind an existing Authority if that responsibility is semantically coherent with its boundary;
2. split/create an Authority if responsibility would otherwise be mixed incorrectly;
3. decide that the concern is not applicable/deferred, with explicit evidence.

The planner must not choose among these automatically without the Authority-boundary rules.

## Main finding

Coverage can act as both plan and completion control without storing a manual plan.

The work plan is derived:

```text
Concern applicability
+ proof contract
+ Authority competence
+ project role bindings
+ realized canonical knowledge
+ blockers/freshness
        ↓
Derived Engineering Work Plan
        ↓
completion_ready
```

A project is complete for the selected scope only when every activated concern is one of:
- COVERED;
- NOT_APPLICABLE with accepted rationale/evidence;
- DEFERRED with accepted owner/reopen condition.

Any MISSING, BLOCKED, STALE, or attention-required UNASSESSED prevents completion.

## Design correction

Authority roles define **competence**, not mandatory outputs.

For example an OPERABILITY Authority may be able to produce logging, metrics, tracing, health and incident knowledge. It should produce only the subset activated for the project/scope.

This prevents the Concern Catalog from becoming a universal mandatory checklist while still making omissions algorithmically visible.

## Next research step

The remaining weakness is that project `semantic-claim-bindings` are still an external research adapter.

The target form is to move this semantic classification into the actual Engineering Graph production contract:

```yaml
produces:
  - capability: project-specific-capability
    knowledge_kind: data-design
    semantic_claims:
      - engineering.data.classification
```

Research migration check found an important ordering constraint: project graphs pinned to the current Harness reject the new field. Therefore the correct migration is Harness schema/runtime first, project adoption second. Until then pilot branches keep semantic claims in a research adapter.