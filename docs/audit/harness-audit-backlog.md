# Harness Audit Backlog

Status: active audit ledger.

Purpose: keep one cumulative record of Harness defects and design gaps found across repeated audits. New audits must update an existing item when the same root cause is rediscovered instead of creating a duplicate.

## Statuses

- `OPEN` — reproduced or supported by code/spec evidence; not fixed.
- `IN_PROGRESS` — correction is being implemented.
- `FIXED` — correction merged into this audit branch and covered by regression evidence.
- `VERIFIED` — fixed behavior was re-audited from another perspective.
- `DEFERRED` — accepted issue intentionally postponed.
- `REJECTED` — investigation showed the original finding was not a defect.
- `NEEDS_DECISION` — behavior is internally consistent only after an explicit semantic/model choice.

## Severity

- `P0` — can produce a false COMPLETE/CURRENT result or a materially wrong next action.
- `P1` — important semantic inconsistency, missing state, or control-loop ambiguity.
- `P2` — maintainability/testability/integration weakness that can conceal later defects.
- `P3` — local ergonomics or presentation issue.

## Functional findings

| ID | Severity | Status | Perspective | Finding | Evidence / consequence |
|---|---|---|---|---|---|
| HARN-001 | P0 | OPEN | Completeness / applicability | Canonical Engineering Coverage policy declares `manual_activation_classes`, but `concern_activation.py` does not evaluate them. Silence can therefore omit privacy/safety/AI/regulated applicability from the coverage state and still allow `completion_ready=true`. | `spec/engineering-coverage/activation-policy-v1.yaml`, `concern_activation.py`, `engineering_coverage.py`. |
| HARN-002 | P0 | OPEN | Lifecycle / semantic change | An exhaustive prerequisite semantic baseline tracks only consumed atom fingerprints. Newly added atoms, and changed atoms previously dispositioned as irrelevant, can escape re-evaluation and leave downstream `CURRENT` even though the exhaustive decision surface changed. | `capability_lifecycle.py`, `semantic_derivation.py`; scenario `selective-lifecycle-revalidation` explicitly expects a new atom to leave downstream CURRENT. |
| HARN-003 | P1 | NEEDS_DECISION | Provider semantics | Core permits multiple providers for one Capability inside one Authority. Structural target evaluation blocks the Capability when any provider is blocked, while lifecycle/decision logic selects one provider. The same model can therefore be BLOCKED structurally and CURRENT in lifecycle. | `core-v0.md`, `target_state.py`, `capability_lifecycle.py`, `tests/test_lifecycle_experiment.py`. |
| HARN-004 | P0 | OPEN | Existing-project bootstrap | `decision_pipeline.py` treats a Core provider without a lifecycle assertion as if no provider existed and emits `CREATE_MISSING_PROVIDER`. Existing projects can be told to create duplicate canonical knowledge instead of admitting/baselining the existing provider. | `decision_pipeline.py::_selected_provider` and mode selection. |
| HARN-005 | P1 | NEEDS_DECISION | Granularity | Lifecycle/admission are Capability-granular, but an unresolved Question against an existing artifact blocks the whole artifact. If one artifact provides several capabilities, a gap in one can invalidate unrelated capabilities. | `Core Question.blocks`, multi-capability artifacts such as `PRODUCT-REQUIREMENTS`. |
| HARN-006 | P0 | OPEN | Question resolution | `resolve_question` only checks Authority ownership and sets `resolution=<artifact>`. It does not prove that canonical truth changed or that a new accepted semantic identity exists, so a Question can be structurally cleared against unchanged knowledge. | `harness.py::resolve_question`. |
| HARN-007 | P1 | OPEN | Orchestration / next-action | Harness exposes several partially overlapping frontiers: structural target/router, lifecycle decision roadmap, semantic closure, and Engineering Coverage work items. No single canonical next-action projection composes them, so an agent must know cross-layer precedence itself. The Decision Roadmap also reports only `READY` or `EMPTY`, so COMPLETE, BLOCKED, WAITING and metadata-incomplete terminal shapes share the same top-level `EMPTY` status. | `agent_router.py`, `decision_pipeline.py`, `semantic_closure.py`, `engineering_coverage.py`. |
| HARN-008 | P1 | OPEN | Model completeness | Engineering Graph validates only declared engineering knowledge. Engineering Coverage and the optional Reference Model attempt to detect omitted concerns, but the model currently has no canonical composition that guarantees the Engineering Graph itself is sufficiently complete for the selected project. | `engineering-graph-v0.md`, Engineering Coverage research/canonical policy, Reference Engineering Model research layer. |
| HARN-009 | P1 | OPEN | Replay / evidence currentness | A semantic evaluation set has no explicit current-record selection or uniqueness rule. `evaluation_index` silently overwrites duplicate `(artifact, capability)` entries by order, while `proposals_from_evaluation_set` aggregates Question proposals from all entries. A stale rejected evaluation can therefore reopen a resolved Question or block closure even when a newer accepted evaluation exists. | `semantic_acceptance.py::evaluation_index`, `semantic_questions.py::proposals_from_evaluation_set`, `append_question_proposals`. |
| HARN-010 | P1 | OPEN | Work grouping / admission | `agent_router.py` groups CREATE work by `(Authority, subject, knowledge_kind)` without requiring compatible prerequisite/read-boundary contracts. Strict semantic admission is capability-specific and derives allowed source Authorities from that capability's prerequisites. A grouped multi-capability artifact can therefore have no single coherent admission boundary when grouped capabilities require different inputs. | `agent_router.py::route_create_work`, `semantic_admission.py::admit_artifact`; current grouping regression covers only two root capabilities with identical empty prerequisites. |
| HARN-011 | P0 | OPEN | Contract evolution | Lifecycle currentness is bound to provider/prerequisite acceptance identities, but not to the semantic contract, decision contract, decision policy, overlay, or evaluator contract under which acceptance occurred. Updating Harness acceptance rules can leave an old evaluation/lifecycle assertion `CURRENT` and semantic closure `COMPLETE` without revalidation under the new rules. | Admission records only a generic contract label plus result fields; `capability_lifecycle.py` has no acceptance-policy fingerprint/baseline. |
| HARN-012 | P1 | NEEDS_DECISION | End-to-end state transition | A successful capability execution produces several coordinated facts (Core provider registration/update, semantic evaluation, lifecycle assertion, possible Question resolution), but Harness exposes no canonical apply/transition operation that updates them as one logical result. Partial persistence can cause the same work to reappear or leave contradictory projections. | `semantic_admission.py` returns evidence; Decision Pipeline skill instructs the agent to persist outcome and recompute, but no runtime transition composes those mutations. |
| HARN-013 | P0 | NEEDS_DECISION | Hidden dependency / currentness | Authority Context deliberately admits same-Authority supporting artifacts from Core `depends_on` even when their capabilities are absent from the selected production's Engineering Graph prerequisites. Strict admission permits same-Authority source assertions. A material semantic dependency can therefore bypass the production topology and lifecycle baseline, so changing that support may leave the dependent capability `CURRENT`. | `authority_context.py::_same_authority_closure`, `semantic_admission.py` allowed same-Authority sources, Integration Contract only rejects hidden cross-Authority dependencies. |

## Deferred hardening findings

These are real issues but are deliberately lower priority until the functional model is stable.

| ID | Severity | Status | Perspective | Finding |
|---|---|---|---|---|
| HARN-H01 | P1 | DEFERRED | Filesystem safety | Human projection output/source paths are not constrained strongly enough to the project root; destructive output handling can target an unintended directory. |
| HARN-H02 | P1 | DEFERRED | Delivery invariant | Repository rules do not technically enforce the PR + green-gate invariant described in `AGENTS.md`. |
| HARN-H03 | P1 | DEFERRED | CI coverage | Main PR workflow uses a manual path allowlist and currently omits multiple runtime Python modules. |
| HARN-H04 | P2 | DEFERRED | Test infrastructure | Validation is split across many bespoke scripts and not all repository validators/tests participate in the normal aggregate check. |

## Audit perspectives

Each substantial audit should explicitly cover one or more of these perspectives and append only new root causes:

1. **State-machine consistency** — every reachable state has one meaning and one deterministic next action.
2. **End-to-end agent loop** — bootstrap → frontier → produce → admit → persist → recompute → closure.
3. **Existing-project migration** — partial metadata, legacy providers, mixed canonical formats, gradual adoption.
4. **Idempotence and replay** — rerunning commands/evaluators with unchanged inputs must not invent new work or change truth.
5. **Change propagation** — upstream revision, split/merge, added/removed semantics, provider replacement, Question lifecycle.
6. **Failure semantics** — distinguish semantic uncertainty, invalid evidence, missing metadata, unsupported capability, and implementation lag.
7. **Granularity consistency** — project / Consumer / Authority / Artifact / Capability / subject / assertion must not be mixed accidentally.
8. **Completeness / omission resistance** — absent engineering territory must not silently look complete.
9. **Cross-layer consistency** — structural, semantic, lifecycle, coverage and decision layers must not contradict each other.
10. **Portability** — the same semantics must work for greenfield, mature legacy, multi-consumer and partially modeled repositories.
11. **Minimality / necessity** — derived layers must add information not already represented elsewhere and must not create parallel truth.
12. **Adversarial model cases** — multiple providers, multi-capability artifacts, stale evidence, partial projections, conflicting Questions, reordered operations.

## Audit runs

| Run | Date | Perspectives | Result |
|---|---|---|---|
| AUD-001 | 2026-10-01 | Functional state machine, completeness, lifecycle, provider semantics | Established HARN-001..008. |
| AUD-002 | 2026-10-01 | Replay/idempotence, grouped work, contract evolution, end-to-end persistence, hidden same-Authority dependencies | Added HARN-009..013 and additional evidence to HARN-002/HARN-007. |

## Audit protocol

For every new finding:

1. Search this ledger by root cause and affected invariant.
2. Reuse the existing ID if the root cause is already present.
3. Add new evidence to that item rather than duplicating it.
4. Before a fix, add a failing regression/acceptance scenario that expresses the intended invariant.
5. Mark `FIXED` only after implementation and regression evidence exist on this branch.
6. Mark `VERIFIED` only after a later independent audit perspective fails to reproduce the defect.
