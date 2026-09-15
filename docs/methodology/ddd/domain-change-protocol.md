# Domain-change re-entry protocol

Use when new requirements, architecture/implementation findings or stakeholder clarification may change accepted target-project domain semantics.

## Classify the highest affected layer

```text
implementation detail only -> implementation/readiness
observable behavior or quality changes -> Requirements -> revalidate dependent Domain/Architecture/Implementation
tactical identity/lifecycle/invariant changes -> Tactical DDD -> revalidate dependent Architecture/Implementation
language/responsibility/authority/context relationship changes -> Strategic DDD -> revalidate affected Tactical DDD and downstream work
```

Do not let a lower layer solve an upstream semantic unknown.

Revisit Strategic DDD only when evidence materially changes a ubiquitous-language boundary, responsibility/decision ownership, independent lifecycle/invariants, authority boundary, or context relationship/public semantic contract.

A new class, table, endpoint, service or deployment unit is not by itself a Strategic DDD trigger.
