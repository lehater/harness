# Engineering Coverage Map prototype

Status: research only.

A project mapping references the reusable concern catalog and maps each concern to existing project truth.

Required leaf states:
- COVERED
- MISSING
- BLOCKED
- STALE
- NOT_APPLICABLE
- DEFERRED
- UNASSESSED

A mapping row may contain:
- concern
- state or derivation rule
- capabilities
- artifacts
- applicability evidence/rationale
- provenance / caused_by
- freshness

The prototype deliberately permits explicit project mapping because not every concern is inferable from capability names alone.
The evaluation target is to measure how much of each map can be derived automatically from existing Engineering Graph/Core data.
