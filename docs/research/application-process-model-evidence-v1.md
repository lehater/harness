# Application Process Model research evidence

Status: research evidence for `docs/design/application-process-model-v1.md`.

## Research result

The process model was tested against standards/research and contrasting process
shapes before promotion to v1.

The resulting boundary is intentionally smaller than BPMN or a universal
workflow metamodel:

```text
Application Process owns
  boundary
  + composition constraints
  + continuation
  + completion

Participating work/events/decisions/actors/data/state remain referenced truth.
```

## Reference-model findings

The following findings materially shaped v1:

- ISO 18629/PSL distinguishes an activity definition from its occurrences and
  models constraints over occurrences.
- Workflow Patterns provides notation-independent coverage for ordering,
  choice, synchronization, repetition, multiple instances and cancellation.
- BPMN supplies a rich notation/execution metamodel but notation constructs
  need not become canonical Harness concepts.
- UML keeps Activity and State Machine semantics separate.
- DMN separates decision logic from process coordination.
- CMMN demonstrates that case-like, situation-driven work should not be forced
  into one universal Process abstraction.
- declarative process approaches demonstrate that process semantics need not be
  represented as one imperative control-flow graph.

## Contrasting-model checks

The v1 boundary was checked against:

- a synchronous ordered flow;
- approval with external wait and occurrence correlation;
- saga-like recovery/compensation;
- a long-running process with multiple continuations.

All fit the same ownership boundary. The only material optional semantics needed
beyond boundary/composition/completion are continuation/correlation,
recovery/compensation and independently meaningful semantic progress.

## Repository evidence

NAPMS supplied real-project semantic examples, but its pinned Harness revision
is older than current Harness and therefore is not treated as current-runtime
proof.

Initial current-Harness validation demonstrated that an independently
addressable process Capability fits inside APPLICATION-DESIGN without a new
Authority or Core concept. Integration work then established a dedicated
`application-process-design` knowledge kind because Process v1 has a distinct
production/decision/semantic-acceptance contract. The split is routing and
acceptance specialization, not a new decision owner.

A source-bounded BPMN experiment demonstrated that the process contract can
drive a disposable projection while refusing to infer richer BPMN runtime
semantics.

These experiments are evidence for the boundary, not part of the canonical
contract.


## Harness integration decision

Process v1 is integrated through the existing Harness discovery and production
pipeline:

- Engineering Coverage exposes `application.process` with proof claim
  `engineering.application.process`;
- the application Authority role can produce that claim;
- Design Profile forms a separate Process Capability when the contract has an
  independent consumer/acceptance/revalidation boundary;
- `application-process-design` routes the Capability to the Process producer;
- semantic admission enforces mandatory boundary, referenced-work, composition
  and completion assertions plus process-specific review checks;
- Decision Governance explores occurrence boundary, composition,
  continuation/correlation and completion/recovery;
- Reference Engineering Model contains an optional `APPLICATION-PROCESS`
  proposal keyed by explicit `application_process_material` project evidence.

No Process Authority, Core Process entity or universal process DSL is introduced.
