# Domain-change re-entry protocol

Use when new requirements, architecture/implementation findings or stakeholder clarification may change accepted domain semantics.

Classify the highest affected layer:

```text
implementation detail only -> S4 / code
observable behavior or quality expectation changes -> S1 Requirements
identity/lifecycle/invariant changes inside one accepted BC -> S2 Tactical DDD
language/responsibility/authority/context relationship changes -> S2 Strategic DDD
```

Revalidate only dependent downstream layers. Do not let a lower layer solve an upstream semantic unknown.

Revisit Strategic DDD only when evidence materially changes at least one of: ubiquitous-language boundary; responsibility or decision ownership; independent lifecycle/invariants; authority boundary; context relationship/public semantic contract.

A new class, table, endpoint, service or deployment unit is not by itself a Strategic DDD trigger.
