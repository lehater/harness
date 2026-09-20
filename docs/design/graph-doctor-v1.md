# Harness Graph Doctor v1

Status: canonical v1.

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

Acceptance is executed by `validators/validate_graph_doctor.py` through `make harness-check`.

## NAPMS pilot

Validation pilot: NAPMS.

Current NAPMS main model diagnosed:

```
ERROR 0
WARN  0
INFO  0
```

The unified NAPMS graph/projection therefore passes the new aggregate diagnostic layer without project-specific suppressions.

## Nutrition pilot

Validation pilot: Nutrition Management.

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

Pilot repair then:
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

The pilot proved diagnose → review → repair → revalidate behavior; project repair remains separate from this Harness contract.

## Conclusion

Graph Doctor is justified as a generic Harness capability.

It should remain a non-semantic diagnostic layer over existing canonical validators rather than duplicate their truth or mutate project semantics.

Canonical v1 policy:
- ERROR findings make the command exit non-zero.
- WARN findings are reported but do not fail by default.
- INFO findings are informational and do not indicate graph defects.
- Semantic auto-fix is forbidden.
- The canonical CLI is the standalone `graph_doctor.py`; a future umbrella CLI may delegate to it without changing this contract.

No Core entity change is required.
