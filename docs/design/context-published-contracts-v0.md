# Published Context Contracts v0

Status: canonical.

## Purpose

Define the narrow runtime contracts used where one Harness bounded context must
consume another context's stable information.

The bounded-context map owns dependency direction. This contract owns the
published module/symbol boundary for dependencies where consuming an internal
representation would couple two contexts unnecessarily.

Machine-readable enforcement lives in
`spec/architecture/harness-context-map-v0.yaml` under
`published_boundaries`.

## Coverage -> Knowledge Assurance

Engineering Coverage needs three facts from Knowledge Assurance:

- whether a concrete provider is accepted, rejected, or has no semantic
  evaluation yet;
- which Capabilities have semantic evaluation evidence and which semantic claims
  are accepted for them;
- how an explicitly invalid Capability propagates through production
  prerequisites.

Coverage does not own or interpret raw
`harness-artifact-semantic-evaluation` records.

The published API is:

```text
semantic_acceptance.coverage_assurance_view
semantic_acceptance.coverage_invalidation_closure
```

`coverage_assurance_view(project_docs)` returns a read-only projection with:

- `provider_disposition(artifact, capability)` ->
  `ACCEPTED | REJECTED | UNEVALUATED`;
- `capability_evaluated(capability)`;
- `evaluated_capabilities()`;
- `accepted_claims(capability)`;
- `accepted_claims_by_capability()`.

Returned collections are copies. Coverage therefore cannot mutate Assurance
state through the view.

The projection preserves the existing migration rule: a provider with no
semantic evaluation remains `UNEVALUATED` rather than becoming rejected.

## Repository Integration -> Project Model

Repository Integration validates project-native routing against the accepted
Core/Engineering Graph models. Those model documents are already public
Project Model contracts, so introducing another DTO would duplicate truth.

Integration may therefore use only these published Project Model operations:

```text
harness.project_model.core.CoreError
harness.project_model.core.validate_model

harness.project_model.engineering_graph.validate_engineering_graph
harness.project_model.engineering_graph.derive_profile
harness.project_model.engineering_graph.producer_index
harness.project_model.engineering_graph.production_index
```

During migration, `from harness import CoreError, validate_model` remains
supported through the temporary `harness/__init__.py` import bridge. The
validator normalizes that exact alias to `harness.project_model.core` before
checking published symbols. Legacy `from engineering_graph import ...` is
supported only through the temporary root `engineering_graph.py` import/CLI
facade and normalizes to `harness.project_model.engineering_graph` under the
same published-symbol checks. `harness.py` is a CLI facade, not the import bridge.

Integration must not import other Project Model implementation symbols merely
because they are physically reachable.

## Previously resolved directions

The earlier DDD audit already removed:

- Coverage -> Application imports by moving repository/skill orchestration into
  `coverage_application.py`;
- Decision Governance -> Application imports by separating
  `harness.decision.decision_explorer_contract` from the application request
  builder.

Those directions remain protected by the ordinary context dependency map and do
not require an additional published-boundary rule.

## Enforcement

`validators/validate_context_boundaries.py` validates both levels:

1. the context dependency itself must be allowed by the bounded-context map;
2. when a `published_boundaries` rule exists, imports must use only the listed
   target modules and explicit symbols.

A broad `import module` is rejected for such a boundary because it bypasses the
symbol contract.

The existing `CoreError` shared-kernel exception remains temporary and is
governed separately by the context map.

## Consequence for physical packaging

With HARN-016 resolved, the root-module migration ratchet established, and these
published boundaries enforced, physical movement into
`src/harness/<context>/...` can proceed incrementally.

Package movement must preserve these contracts; it must not replace them with
new cross-context access to implementation internals.
