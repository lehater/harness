# Decision Explorer Execution Assurance v0

Status: experimental.

## Problem

A candidate-free Explorer Request and request-bound exploration evidence prevent
post-hoc schema substitution, but they do not prove that the model/runtime
performing Decision Exploration was physically isolated from a previously chosen
candidate, conversation history or hidden memory.

A producer-controlled field such as `isolated: true` is not evidence. It has the
same trust problem as the earlier `NO_MATERIAL_DECISION` escape hatch: the
workload would be certifying the property that must constrain the workload.

## Assurance levels

### REQUEST_BOUND

Harness generates the Explorer Request from Engineering Graph/Core/lifecycle and
project policy. Exploration must bind to its deterministic request identity.

This proves:

- the authorized project input manifest;
- the decision axes, material dimensions and exploration policy;
- the accepted-prerequisite baseline;
- that the current candidate/write target is excluded from the declared request;
- that later policy/baseline changes invalidate the request.

It does **not** prove that the runtime actually withheld all other context.

### ATTESTED_ISOLATED

A stronger level requires an external trusted control plane that:

1. creates an independent execution context;
2. supplies only the Explorer Request and permitted materialized inputs;
3. executes the explorer;
4. binds the produced exploration output to the request;
5. emits authenticated execution provenance that the workload cannot forge.

Harness does not currently own such a runtime. Therefore this level is
intentionally fail-closed rather than represented by a self-attested receipt.

## Architectural analogy

The useful model is closer to a trusted build platform than to another semantic
artifact. The Explorer Request is analogous to externally supplied build
parameters/materials; exploration output is an artifact; the external executor
is the trusted control plane/builder that must faithfully record provenance.

The trust boundary belongs outside the workload being evaluated.

## Current integration

Project decision policy may declare:

```yaml
defaults:
  execution_assurance: REQUEST_BOUND
```

or request:

```yaml
defaults:
  execution_assurance: ATTESTED_ISOLATED
```

`REQUEST_BOUND` is currently machine-verifiable by Harness.

`ATTESTED_ISOLATED` is rejected with
`DECISION_TRUSTED_EXECUTION_VERIFIER_REQUIRED` until a trusted executor/verifier
adapter exists.

This avoids claiming isolation that the current repository-only Harness cannot
actually establish.

## Candidate executor options for the next experiment

1. **Fresh model session controlled by an orchestrator**
   - minimal practical boundary;
   - same model is acceptable;
   - orchestrator must create the session and restrict inputs;
   - provenance strength depends on trusting the orchestration service.

2. **Independent model/session**
   - adds viewpoint diversity as well as context isolation;
   - higher cost and may introduce capability differences;
   - best reserved for deeper exploration policies.

3. **Sandboxed/attested execution**
   - strongest runtime claim when backed by authenticated provenance;
   - significantly more infrastructure;
   - useful only when the project requires assurance against executor/workload
     tampering, not merely better reasoning discipline.

## Recommendation

Keep normal decision-governed work at `REQUEST_BOUND` until Harness is connected
to an orchestration runtime that can genuinely create fresh agent contexts.

When that runtime exists, add one narrow verifier adapter rather than accepting
generic execution metadata from the producer. The adapter should return only
verified request/output/executor/execution identities to semantic admission.

Do not add execution/session entities to Core.
