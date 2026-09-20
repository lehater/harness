# Research — Graph Doctor v1

Status: research candidate.

## Goal

Provide one non-destructive diagnostic pass over Harness Engineering Graph, Core/project realization, canonical files and project graph alignment.

The tool is a doctor/linter, not an automatic semantic repair engine.

## Command

Examples:

```sh
python graph_doctor.py .harness/engineering-graph.yaml \
  --core-model .harness/graph.yaml \
  --target IMPLEMENTATION \
  --source-root .
```

For projects with an authoritative canonical graph:

```sh
python graph_doctor.py docs/harness-engineering-graph.yaml \
  --source-graph docs/canonical-graph.yaml \
  --projection docs/harness-projection.yaml \
  --target BACKEND-IMPLEMENTATION \
  --source-root .
```

Use `--json` for CI/agent consumption.

Exit code is non-zero when ERROR findings exist.

## Report contract

```yaml
version: 1
kind: harness-graph-doctor-report
target: IMPLEMENTATION
summary:
  ERROR: 0
  WARN: 0
  INFO: 0
findings:
  - code: ARTIFACT_FILE_MISSING
    severity: ERROR
    owner: COMPONENT-DESIGN
    message: ...
    evidence: ...
    suggestions: [...]
healthy: true
```

Stable diagnostic fields:
- code;
- severity;
- message;
- optional semantic owner;
- evidence;
- suggested human actions.

Suggestions are not automatic semantic edits.

## Implemented diagnostics

Engineering Graph:
- `AUTHORITY_NO_OUTPUTS`;
- `CAPABILITY_MULTIPLE_PRODUCERS`;
- `CAPABILITY_NO_PRODUCER`;
- `CAPABILITY_DEAD_PUBLIC`;
- `TERMINAL_NO_PRODUCER`;
- `TERMINAL_ALREADY_CONSUMED`;
- `TERMINAL_OWNER_MISMATCH`;
- canonical validator backstop for cycles, subject collisions, malformed graph/schema.

Core/project realization:
- `ARTIFACT_DUPLICATE_ID`;
- `ARTIFACT_DUPLICATE_PATH`;
- `ARTIFACT_DEPENDENCY_MISSING`;
- `ARTIFACT_FILE_MISSING`;
- `ARTIFACT_UNKNOWN_AUTHORITY`;
- `ARTIFACT_ORPHAN`;
- `CANONICAL_POINTS_TO_GENERATED`;
- `ARTIFACT_PROVIDES_UNKNOWN_CAPABILITY`;
- `PROVIDER_OWNER_MISMATCH`;
- `QUESTION_UNKNOWN_AUTHORITY`;
- `QUESTION_BLOCKS_UNKNOWN_ARTIFACT`;
- `QUESTION_BLOCKS_UNKNOWN_CAPABILITY`.

Project/capability alignment:
- `ALIGNMENT_HIDDEN_DEPENDENCY`;
- `ALIGNMENT_PHANTOM_DEPENDENCY`;
- `ALIGNMENT_UNBOUND_ARTIFACT`;
- `ALIGNMENT_OWNER_MISMATCH`.

Target evaluation:
- `TARGET_INCOMPLETE` as INFO rather than a graph defect.

The doctor suppresses cascading target-state failures after structural ERROR findings, so one root defect does not produce noisy duplicates.

## Why no semantic auto-fix

The doctor may know that a public capability is dead, but it cannot know whether the correct action is:
- remove it from public topology;
- add a missing consumer;
- declare it intentionally terminal.

Likewise a missing canonical path may mean:
- file moved;
- artifact became obsolete;
- file was accidentally deleted.

Therefore semantic repair remains an Authority-owned decision.

Safe mechanical auto-fixes may be added later only when the result is derivable without choosing engineering semantics.

## Harness regression evidence

A dedicated acceptance suite proves:
- healthy baseline;
- dead public capability;
- stale/missing file;
- duplicate canonical path;
- stale Question blockers;
- canonical registration of generated output;
- hidden project dependency;
- phantom capability prerequisite;
- provider ownership mismatch;
- missing artifact dependency;
- incomplete Consumer target reported as INFO.

Research workflow: green.

## NAPMS pilot

Branch: `research/graph-doctor-v1`.

Current NAPMS main model diagnosed:

```
ERROR 0
WARN  0
INFO  0
```

The unified NAPMS graph/projection therefore passes the new aggregate diagnostic layer without project-specific suppressions.

## Nutrition pilot

Branch: `research/graph-doctor-v1`.

Initial diagnosis against current main found exactly the defects independently discovered during Human Projection research:

1. `ARTIFACT_FILE_MISSING`
   - `COMPONENT-DESIGN`
   - stale path `docs/implementation/component-design.md`.

2. two `CAPABILITY_DEAD_PUBLIC`
   - `nutrition-management.food-knowledge.bls-v4.source-structure`;
   - `nutrition-management.food-knowledge.bls-v4.normalization-order`.

3. `ARTIFACT_ORPHAN`
   - `REDESIGN-REVALIDATION`
   - stale registration of `docs/redesign/component-design.md` under PRODUCT.

Research-only repair then:
- removed the two unjustified public CapabilityIds while leaving their source artifacts canonical;
- removed stale `REDESIGN-REVALIDATION`;
- pointed `COMPONENT-DESIGN` at the existing accepted `docs/redesign/component-design.md`.

Second doctor pass:

```
ERROR 0
WARN  0
INFO  0
```

This proves a complete diagnose -> review -> repair -> revalidate loop on a real project.

No Nutrition main change was made.

## Conclusion

Graph Doctor is justified as a generic Harness capability.

It should remain a non-semantic diagnostic layer over existing canonical validators rather than duplicate their truth or mutate project semantics.

Before canonicalization:
- review diagnostic code names/severity policy;
- decide whether warnings may optionally fail CI;
- test at least one larger corrupted NAPMS mutation set;
- define whether doctor belongs under one future `harness doctor` CLI or remains a standalone command.

No Core entity change is required.
