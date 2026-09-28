# Semantic Question Loop experiment v0

## Hypothesis

A machine-addressable semantic completeness gap should not be silently filled by
a downstream agent. A rejected semantic admission should expose a deterministic
Core `Question` proposal addressed to the Authority that owns the incomplete
capability. Persisting that Question blocks the capability until the owning
canonical artifact is changed and the Question is resolved.

## Scope

This experiment does not change Harness Core and does not introduce a universal
semantic DSL.

It adds only an above-Core projection:

```text
knowledge-kind obligation
  -> semantic admission finding
  -> Question proposal
  -> Core block
  -> owning Authority changes canonical artifact
  -> semantic admission
  -> resolve Question
```

Knowledge-kind contracts remain responsible for declaring only
machine-addressable obligations that have demonstrated value.

## Acceptance case

`validators/validate_semantic_question_loop.py` proves:

1. a `task-model` candidate can provide the capability structurally while
   missing a required semantic obligation;
2. semantic admission rejects the candidate;
3. the rejection yields a deterministic Question addressed to
   `APPLICATION-DESIGN`;
4. the Question blocks the capability;
5. supplying the missing semantic assertion makes admission pass;
6. the Question resolves only against the owning canonical artifact.

The target-repository experiment is intentionally separate so a real repository
can test whether these generated questions reveal useful missing knowledge rather
than merely satisfying a synthetic schema.
