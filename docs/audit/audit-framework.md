# Harness Audit Framework

Status: canonical maintainer audit methodology.

## Purpose

Provide a reusable matrix of independent audit perspectives for Harness and a
record of which perspectives have actually been exercised.

This file owns **how Harness is audited**. Defect/evolution classification
remains owned by `docs/audit/README.md`.

## Audit flow

1. Select the smallest set of perspectives justified by the audit goal.
2. Define scope and evidence boundary.
3. Inspect canonical contracts, implementation and executable evidence.
4. Search existing HARN/EVO records by root cause.
5. Produce evidence-backed findings without allocating HARN/EVO identifiers.
6. Route findings through Maintainer `capture-harness-observation`.
7. Record the completed `AUD-*` run here with covered perspectives/result.
8. Re-audit a fix independently before calling a defect VERIFIED.

An audit may yield no new findings. That is still useful coverage evidence.

## Perspective matrix

Coverage states: **COVERED**, **PARTIAL**, **UNASSESSED**.

| ID | Perspective | Core question | Coverage | Latest evidence |
|---|---|---|---|---|
| AP-01 | State-machine consistency | Does every reachable state have one meaning and deterministic next action? | COVERED | AUD-003 |
| AP-02 | End-to-end agent loop | Does bootstrap -> frontier -> produce -> admit -> persist -> recompute -> closure work coherently? | COVERED | AUD-002 |
| AP-03 | Existing-project migration | Do partial metadata, legacy providers and gradual adoption remain safe? | COVERED | AUD-001 |
| AP-04 | Idempotence and replay | Can unchanged reruns invent work or change truth? | COVERED | AUD-002 |
| AP-05 | Change propagation | Do upstream revisions, split/merge and provider replacement invalidate required downstream evidence? | COVERED | AUD-003 |
| AP-06 | Failure semantics | Are uncertainty, invalid evidence, missing metadata and implementation lag distinguishable? | COVERED | AUD-003 |
| AP-07 | Granularity consistency | Are project/Authority/Artifact/Capability/subject/assertion levels kept distinct? | COVERED | AUD-002 |
| AP-08 | Completeness / omission resistance | Can absent engineering territory silently look complete? | COVERED | AUD-001 |
| AP-09 | Cross-layer consistency | Can structural, semantic, lifecycle, coverage or decision layers contradict each other? | COVERED | AUD-004 |
| AP-10 | Portability | Do semantics hold across greenfield, legacy, multi-consumer and partial models? | COVERED | AUD-007 |
| AP-11 | Minimality / necessity | Does every derived layer add information without creating parallel truth? | COVERED | AUD-006 |
| AP-12 | Adversarial model cases | Do multiple providers, stale evidence, conflicting Questions and reordered operations remain safe? | COVERED | AUD-003 |
| AP-13 | Instruction ownership / routing | Does every instruction/procedure have one owner and deterministic discovery? | COVERED | AUD-007 |
| AP-14 | Empirical agent behavior | Does a real agent select and execute the intended route/skill under representative tasks? | UNASSESSED | — |
| AP-15 | Observability / diagnosability | Can a maintainer explain why a route/state/action was produced from available evidence? | UNASSESSED | — |
| AP-16 | Evaluator quality / calibration | Are semantic evaluators reproducible and calibrated against trusted judgements? | PARTIAL | live-calibration contracts |
| AP-17 | Security / trust boundaries | Can repository content, tool output or prompt injection cross an authority/tool trust boundary? | UNASSESSED | — |
| AP-18 | Performance / cost / context efficiency | Does Harness avoid unnecessary context, validation, CI and evaluator work? | PARTIAL | AUD-008/AUD-009 (CI only) |
| AP-19 | Recovery / crash consistency | Can interrupted multi-step application work resume without contradictory published state? | PARTIAL | AUD-002 / HARN-012 |
| AP-20 | Versioning / compatibility | Can Harness/contracts/Consumer Pack evolve without silently invalidating projects? | PARTIAL | AUD-006/AUD-007 |
| AP-21 | Provenance / reproducibility | Can state be traced to the exact policy/evidence/version that produced it? | PARTIAL | AUD-002 |
| AP-22 | Scale / stress / pathological graphs | Does behavior remain correct at large graph/question/artifact counts and deep dependency chains? | UNASSESSED | — |
| AP-23 | Human control / explainability | Are human decision points, uncertainty and consequences explicit enough for safe intervention? | UNASSESSED | — |

## Re-audit triggers

Reconsider a perspective when its owning contract materially changes, a new HARN
exposes a blind spot, or a new execution environment/project shape invalidates
previous evidence.

Do not rerun every perspective after every change.

## Audit runs

| Run | Date | Perspectives | Result |
|---|---|---|---|
| AUD-001 | 2026-10-01 | Functional state machine, completeness, lifecycle, provider semantics | Established HARN-001..008. |
| AUD-002 | 2026-10-01 | Replay/idempotence, grouped work, contract evolution, end-to-end persistence, hidden same-Authority dependencies | Added HARN-009..013 and evidence to HARN-002/HARN-007. |
| AUD-003 | 2026-10-01 | Graph evolution and Decision Pipeline failure/retry semantics | Added HARN-014..015. |
| AUD-004 | 2026-10-01 | Strategic/tactical DDD decomposition, bounded contexts and dependency direction | Added HARN-016 and refined HARN-007/HARN-008. |
| AUD-005 | 2026-10-01 | Instruction ownership, skill routing, discovery lifecycle and procedural duplication | Added HARN-017..019 and EVO-021..027. |
| AUD-006 | 2026-10-01 | Accepted skill-surface architecture vs repository realization | Added HARN-020 and implementation-gap evidence. |
| AUD-007 | 2026-10-01 | Post-migration skill/distribution re-audit | Verified HARN-017..020 corrections. |
| AUD-008 | 2026-10-01 | CI cost, trigger selectivity, duplicate execution, validator coverage and lazy-gate ordering | Strengthened HARN-H03/H04 and added HARN-H05. |
| AUD-009 | 2026-10-01 | CI policy enforcement and post-correction verification | Verified HARN-H03/H04/H05 corrections. |

## Finding handoff contract

`audit-harness` emits audit-local findings containing:

- local reference;
- concise summary;
- affected invariant/surface;
- concrete evidence;
- consequence;
- uncertainty/limitations;
- suggested follow-up responsibility.

They are not HARN/EVO records. The coordinator routes them to
`capture-harness-observation`, which owns deduplication, classification and
persistence.

## Limits

Perspective coverage records past inspection; it does not prove that the
corresponding subsystem remains defect-free.
