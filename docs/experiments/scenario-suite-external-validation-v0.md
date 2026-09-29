# Scenario Suite external validation v0

Status: experimental validation evidence.

## Harness self-validation

Harness branch `experiment/scenario-suite` validates the Scenario Suite as part
of `make harness-check`.

Checkpoint:

- Harness commit: `d606c703b97d868f5629d787997ceefd1b5d8cd9`;
- 36 passing scenarios;
- 40 required behavioral requirements;
- 0 planned coverage gaps.

The catalog treats known functional surface as required executable behavior, not
as an informal test backlog.

## Prep validation

Target branch: `lehater/prep:experiment/scenario-suite`.

Prep uses the generic Scenario Suite runner plus an explicitly loaded
project-owned driver module for native semantic projection.

Validated properties include:

- current structural Consumer closure;
- the real `PROVISIONAL-FOR-RESEARCH` Discovery gap becomes a routed semantic
  Question;
- the current 19-task Task Model passes reusable completeness obligations;
- removing recovery semantics from one real task is detected and routed to
  `APPLICATION-DESIGN`.

The ordinary Prep integration-health check independently accepts `BLOCKED`
only when the state is a clean routed semantic Question frontier and propagated
Engineering Coverage work is exclusively `REVALIDATE_SEMANTICS`.

Checkpoint:

- Prep commit: `9c3171a9ee0462550c2d323b56434d565990eafe`;
- Fast repository validation: PASS;
- Harness Scenario Suite: PASS.

## NAPMS validation

Target branch: `lehater/napms:experiment/harness-scenario-suite`.

NAPMS requires no project-specific Scenario Suite driver for the initial proof.
It uses only built-in Harness drivers against the real project-owned:

- `docs/canonical-graph.yaml`;
- `docs/harness-projection.yaml`;
- `docs/harness-engineering-graph.yaml`.

Validated properties include:

- canonical graph/projection alignment;
- `BACKEND-IMPLEMENTATION = COMPLETE`;
- `FRONTEND-IMPLEMENTATION = READY` with the existing two-capability HCD
  frontier;
- an injected hidden cross-Authority dependency is rejected;
- an injected provider Authority mismatch is diagnosed by Graph Doctor.

The NAPMS mainline immutable Harness pin remains unchanged; only the separate
experiment workflow checks out the Scenario Suite branch.

Checkpoint:

- NAPMS commit: `de866e6401bfecd73da1b66c9aa006f926b9ed83`;
- Harness Scenario Suite experiment: PASS.

## Conclusion

The same protocol now operates at three levels:

```text
Harness synthetic/acceptance fixtures
        ↓
Prep real project + project-native semantic driver
        ↓
NAPMS real project + built-in drivers only
```

This demonstrates that the Scenario Suite is not coupled to one project shape or
one Harness stage. Target repositories can own their scenarios and, only where
necessary, explicitly register project-specific adapters without changing the
generic runner.

This evidence does not prove exhaustive correctness. New Harness behavior must
still extend the coverage catalog and add executable scenarios before it can be
treated as covered.
