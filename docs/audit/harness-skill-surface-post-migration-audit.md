# Harness Skill/Distribution Post-Migration Audit

Date: 2026-10-01  
Run: AUD-007  
Status: verified on audit branch; not integrated to main.

## Scope

Re-audit the skill system from the accepted target architecture rather than from
the pre-migration filesystem:

- Maintainer vs Consumer physical/discovery separation;
- operation/method/artifact-production routing semantics;
- clean-context repository entry;
- inactive procedure quarantine;
- Consumer Pack distribution and clean-target bootstrap;
- root instruction ownership.

## Current inventory

Executable `SKILL.md`: **53**.

| Surface / route | Count | State |
|---|---:|---|
| Consumer operations | 6 | 5 public + 1 internal, all registry-owned |
| Consumer methods | 10 | routed by canonical Concern ids / explicit method id |
| Consumer artifact producers | 35 source files | 34 routed by `knowledge_kind`; 1 explicit unrouted research producer |
| Maintainer operations | 2 | separately registered; source-repository only |
| Archived pre-Core procedures | 5 | non-executable docs under `docs/legacy/skills/**` |

## Verification

### HARN-017 — operation routing ambiguity

Not reproduced.

- Consumer Operation Registry owns active Consumer operations.
- `project-bootstrap-reconcile` is the public startup entry.
- `bootstrap-existing-project` is internal-only.
- typed `skill_router.py` rejects the internal helper as a public route.
- fresh-context fixtures exercise the boundary.

Result: **VERIFIED**.

### HARN-018 — inactive skill discovery

Not reproduced.

- legacy procedures are no longer named `SKILL.md`;
- archived lifecycle entries point to `docs/legacy/skills/**`;
- agent-layer validation rejects archived entries that remain on executable
  `SKILL.md` surfaces;
- Consumer Pack excludes legacy paths.

Result: **VERIFIED**.

### HARN-019 — non-capability method routing

Not reproduced.

- 10 non-owning methods have explicit Consumer Method Registry routes;
- canonical Concern ids provide deterministic method selection;
- direct method id remains an explicit route;
- the conditional transition producer is no longer conflated with methods and is
  excluded from Consumer distribution while unrouted.

Result: **VERIFIED**.

### HARN-020 — skill role inferred from directory

Not reproduced.

- role is declared by `skills/skill-surface-registry-v0.yaml`;
- validators use `surface + route_class + lifecycle + route_status`;
- the physical `skills/artifacts/**` directory no longer determines whether a
  procedure is a method or artifact producer.

Result: **VERIFIED**.

## Physical consumer bootstrap

A clean target layout needs only:

```text
AGENTS.md
.harness/harnessw.py
.harness/harness-binding.json
```

The wrapper test:

1. reads the immutable binding with Python stdlib only;
2. fetches the exact Harness commit;
3. invokes that revision's Consumer Pack materializer;
4. validates the pack;
5. proves no Harness skill tree was copied into the target repository;
6. executes `skill_router.py` from the materialized pack;
7. reuses the immutable cache on the second sync;
8. verifies explicit local development override;
9. rejects a moving `main` revision.

Full PR workflow run **962** passed this path.

## Instruction ownership

Root `AGENTS.md` now owns:

- repository identity/purpose;
- always-on Core invariants;
- Maintainer-surface bootstrap;
- pointers to typed routing/canonical policies;
- repository workflow invariants.

Task procedures live in registered skills. Conditional provider-backed LLM
policy lives in `spec/assurance/llm-execution-policy-v1.yaml`.

`validate_instruction_ownership.py` ratchets this boundary.

## Optional abstraction pilot

`product-requirements`, `domain-model` and `verification-strategy` were compared
for EVO-024.

They share headings and lifecycle shape, but their semantic read boundaries,
stop conditions, acceptance rules, registration semantics and decision behavior
are materially different. Common semantic admission is already centralized in
canonical workbench/admission contracts.

No shared base procedure is introduced. EVO-024 is PARKED until measured
behavioral/context evidence demonstrates a concrete duplication failure.

## Remaining non-blocking research

- real-agent behavioral execution evals for important skills;
- natural-language intent classification quality;
- conditional CHANGE-TRANSITION-DESIGN producer promotion;
- future packaging/release transport beyond the wrapper/cache v0 mechanism.

These do not recreate HARN-017..020.
