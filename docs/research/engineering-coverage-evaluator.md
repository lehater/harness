# Research Engineering Coverage evaluator

Status: research.

`engineering_coverage.py` is the single public research entrypoint for completeness evaluation.

## Inputs

Required:
- Engineering Graph;
- Core realization;
- selected Consumer;
- named scope.

Optional project-owned adapters during research:
- capability scope roots;
- Authority role aliases for non-standard Authority IDs;
- explicit activation/applicability facts;
- semantic-claim bindings until claims move into production contracts.

Reusable policy remains Harness-owned:
- Concern Catalog;
- Concern Activation Policy;
- Concern Semantic Proof Contract;
- Authority Role Contract;
- standard Authority-role bindings.

## Output

The evaluator returns one derived object:

```text
harness-engineering-coverage-evaluation
  project
  consumer
  scope
  scope_roots
  activated_count
  completion_ready
  summary
  rows
  remaining_work
```

Callers should not persist intermediate activation or planner projections as project truth.

## Evaluation boundary

The evaluator validates the Engineering Graph and Core realization first, then derives:

```text
validated graph + realization
        ↓
effective Authority roles
        ↓
Consumer/scope closure
        ↓
concern activation
        ↓
semantic proof instances
        ↓
routed remaining work
        ↓
completion_ready
```

The lower-level research scripts remain testable implementation modules for now; they are not the intended project integration API.

## Completion

`completion_ready=true` iff there is no remaining activated concern instance outside:
- COVERED;
- accepted NOT_APPLICABLE;
- accepted DEFERRED.

The evaluator does not treat the human-readable Coverage Map as an input.
