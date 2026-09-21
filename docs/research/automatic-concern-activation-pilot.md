# Research — Automatic Concern Activation pilot

Status: research only. No main/canonical changes.

## Question

Can Harness derive which Engineering Concerns must be considered for a selected project scope without maintaining a manual `required` checklist?

## Model

~~~text
Concern Catalog
   ↓
Activation Policy + project topology + explicit project facts
   ↓
Activated Concerns
   ↓
Coverage Proof + lifecycle/blockers
   ↓
Coverage State
   ↓
Authority-routed remaining work
   ↓
completion_ready
~~~

A catalog entry does not create work by itself.

## Activation sources

The experiment uses four classes:

1. Baseline — minimal implementation-readiness questions for ordinary software products.
2. Structural rules — machine signals such as human interface, persistence, security boundary, external dependency/source, observability or quality-design topology.
3. Project facts — facts not safely inferable from generic topology, such as privacy applicability or a specific performance concern.
4. Applicability decisions — accepted NOT_APPLICABLE/DEFERRED decisions with evidence.

No prose inspection is required by the activation engine.

## NAPMS

The automatic policy activates 60 concerns from the current first-MVP topology.

All 9 concerns that the previous research overlay manually marked as required are activated automatically:

- interface.human.journeys;
- verification.interface.human;
- data.lifecycle;
- data.classification;
- security.vulnerability-management;
- security.secure-development;
- reliability.recovery;
- operability.incident;
- quality.performance.resource-efficiency.

Therefore the NAPMS activation overlay can be empty except for explicit applicability decisions.

The broader 60-concern result is intentional: once persistence, a security boundary, quality design, observability and UI contracts exist, the completion mechanism should ask whether their related concern families have actually been decided rather than silently assuming that an existing document covers them.

## Nutrition

The policy plus four explicit project facts activates 68 concerns.

Against the old manually maintained `required` research list, 13 of 16 are derived automatically or from explicit project facts.

The three old entries not automatically activated are:

- operability.metrics;
- operability.tracing;
- operability.alerting.

This is currently considered a positive mismatch, not an activation defect.

Nutrition is a local single-user application. Generic runtime topology is sufficient to activate configuration/logging/health/recovery concerns, but it does not by itself justify making dedicated metrics, distributed tracing or alerting mandatory. Those should activate only when a project requirement, deployment topology, SLO/operability decision or explicit project fact makes them relevant.

## Explicit Nutrition project facts retained

The experiment retains only facts that generic topology cannot safely infer:

- governance.privacy — member/profile information makes privacy assessment relevant;
- governance.data — persisted domain/source/user data makes project data governance relevant;
- quality.performance.latency — interactive browser journeys make response time relevant even without a numeric target;
- quality.performance.resource-efficiency — local execution makes bounded resource use relevant.

These are activation facts, not coverage states.

## Important distinction

An activated concern may still resolve to COVERED, MISSING, BLOCKED, STALE, NOT_APPLICABLE, DEFERRED or UNASSESSED.

Activation means only: Harness must obtain an explicit engineering answer for this concern before declaring the selected scope complete.

## End-to-end control loop

~~~text
project topology
+ reusable activation policy
+ minimal activation overlay
        ↓
activated concerns
        ↓
semantic proof contract
+ realized canonical artifacts
+ Authority role competence
        ↓
derived work plan
        ↓
completion_ready
~~~

The planner no longer needs a manually authored `required` list in its primary path.

## Remaining design risks

### Over-activation

Rules must not infer concerns merely because an Authority exists if that Authority can be instantiated for a narrower reason.

Mitigation: use specific machine signals where available; treat broad Authority-role rules as review candidates; compare against materially different pilot projects.

### Under-activation

Some facts cannot be inferred from software topology: legal/regulatory scope, privacy/sensitivity, safety/harm, AI/ML autonomy, and explicit business SLOs. These require explicit project facts or upstream canonical requirements.

### Circularity

Activation must not be based on the existence of the artifact whose absence it is supposed to detect. For example, threat analysis cannot activate only because a Threat Model already exists; it should activate because a security/trust boundary exists.

## Current conclusion

A manually maintained complete `required concerns` list is not necessary.

The likely target architecture is:

~~~text
Reusable Concern Catalog
+ Reusable Activation Policy
+ Project topology / accepted facts
+ Small explicit applicability overlay
        ↓
Derived activated concern set
~~~

That set becomes the algorithmic plan boundary for Coverage and completion control.