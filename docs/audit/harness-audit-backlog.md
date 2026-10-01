# Harness Audit Backlog

Status: active audit ledger.

Purpose: keep one cumulative record of Harness defects and design gaps found across repeated audits. New audits must update an existing item when the same root cause is rediscovered instead of creating a duplicate.

Classification and routing rules are canonicalized in `docs/audit/README.md`.
Non-defect recommendations, research questions and optional future directions belong in the companion **Harness Evolution Radar**: `docs/audit/harness-evolution-radar.md`. A Radar item is not technical debt unless a separate `HARN-*` defect is demonstrated.

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
| HARN-007 | P1 | OPEN | Orchestration / next-action | Harness exposes several partially overlapping frontiers: structural target/router, lifecycle decision roadmap, semantic closure, and Engineering Coverage work items. No single canonical next-action projection composes them, so an agent must know cross-layer precedence itself. DDD review identifies this as an Application Layer responsibility that is currently distributed across peer modules. The Decision Roadmap also reports only `READY` or `EMPTY`, so COMPLETE, BLOCKED, WAITING and metadata-incomplete terminal shapes share the same top-level `EMPTY` status. | `agent_router.py`, `decision_pipeline.py`, `semantic_closure.py`, `engineering_coverage.py`; `docs/audit/harness-ddd-context-map.md`. |
| HARN-008 | P1 | NEEDS_DECISION | Model completeness | Engineering Graph validates only declared engineering knowledge. Engineering Coverage and the optional Reference Model attempt to detect omitted concerns, but their ownership relationship is not canonical. DDD target: Coverage owns completeness/applicability proof; Reference Model owns reusable concern/fact -> CapabilityTemplate materialization; Project Model owns the actual Engineering Graph. | `engineering-graph-v0.md`, Engineering Coverage policy, Reference Engineering Model research layer, `docs/audit/harness-ddd-context-map.md`. |
| HARN-009 | P1 | OPEN | Replay / evidence currentness | A semantic evaluation set has no explicit current-record selection or uniqueness rule. `evaluation_index` silently overwrites duplicate `(artifact, capability)` entries by order, while `proposals_from_evaluation_set` aggregates Question proposals from all entries. A stale rejected evaluation can therefore reopen a resolved Question or block closure even when a newer accepted evaluation exists. | `semantic_acceptance.py::evaluation_index`, `semantic_questions.py::proposals_from_evaluation_set`, `append_question_proposals`. |
| HARN-010 | P1 | OPEN | Work grouping / admission | `agent_router.py` groups CREATE work by `(Authority, subject, knowledge_kind)` without requiring compatible prerequisite/read-boundary contracts. Strict semantic admission is capability-specific and derives allowed source Authorities from that capability's prerequisites. A grouped multi-capability artifact can therefore have no single coherent admission boundary when grouped capabilities require different inputs. | `agent_router.py::route_create_work`, `semantic_admission.py::admit_artifact`; current grouping regression covers only two root capabilities with identical empty prerequisites. |
| HARN-011 | P0 | OPEN | Contract evolution | Lifecycle currentness is bound to provider/prerequisite acceptance identities, but not to the semantic contract, decision contract, decision policy, overlay, or evaluator contract under which acceptance occurred. Updating Harness acceptance rules can leave an old evaluation/lifecycle assertion `CURRENT` and semantic closure `COMPLETE` without revalidation under the new rules. | Admission records only a generic contract label plus result fields; `capability_lifecycle.py` has no acceptance-policy fingerprint/baseline. |
| HARN-012 | P1 | NEEDS_DECISION | End-to-end state transition | A successful capability execution produces several coordinated facts (Core provider registration/update, semantic evaluation, lifecycle assertion, possible Question resolution), but Harness exposes no canonical apply/transition operation that updates them as one logical result. Partial persistence can cause the same work to reappear or leave contradictory projections. | `semantic_admission.py` returns evidence; Decision Pipeline skill instructs the agent to persist outcome and recompute, but no runtime transition composes those mutations. |
| HARN-013 | P0 | NEEDS_DECISION | Hidden dependency / currentness | Authority Context deliberately admits same-Authority supporting artifacts from Core `depends_on` even when their capabilities are absent from the selected production's Engineering Graph prerequisites. Strict admission permits same-Authority source assertions. A material semantic dependency can therefore bypass the production topology and lifecycle baseline, so changing that support may leave the dependent capability `CURRENT`. | `authority_context.py::_same_authority_closure`, `semantic_admission.py` allowed same-Authority sources, Integration Contract only rejects hidden cross-Authority dependencies. |
| HARN-014 | P1 | OPEN | Graph evolution / migration | Capability Lifecycle fails hard when a previously tracked CapabilityId disappears from a revised Engineering Graph. Generic project graph rename/split/merge has no canonical migration/reconciliation path: an old lifecycle row becomes an exception instead of an explicit obsolete/migrate state, while the new Capability can independently appear as CREATE. | `capability_lifecycle.py::validate_projection`; rename/split/merge handling exists only in Reference Model evolution research, not the ordinary project Engineering Graph lifecycle. |
| HARN-015 | P0 | OPEN | Decision failure state | `FAILED_VALIDATION` is declared a terminal Decision Pipeline outcome but is not an input to the roadmap and has no persisted derived state. Recomputing after failure exposes the same missing/noncurrent capability as READY again. The documented instruction to explicitly redo is impossible for failed CREATE because `decision_pipeline.py` rejects `--redo` when no current provider exists. | `decision_pipeline.py` terminal outcomes, redo branch and `explicit redo requires current provider`; no scenario currently covers FAILED_VALIDATION replay. |
| HARN-016 | P1 | IN_PROGRESS | DDD bounded contexts | Harness runtime modules have no enforced bounded-context ownership, allowing domain contexts to depend on orchestration/integration internals. DDD audit found three concrete import inversions: Coverage -> Integration, Coverage -> Application, and Decision -> mixed application request builder. A machine-readable context map and ratchet validator now prevent additional violations while these three are removed. | `spec/architecture/harness-context-map-v0.yaml`, `validators/validate_context_boundaries.py`, `docs/audit/harness-ddd-context-map.md`. |
| HARN-017 | P1 | VERIFIED | Agent skill routing | Active `skills/agent/**` have no machine-readable routing/precedence contract. `AGENTS.md` manually selects some workflows, while `bootstrap-existing-project` and `project-bootstrap-reconcile` overlap for absent/unknown existing-project Harness state. `validate_agent_layer.py` validates shape only and cannot detect routing overlap. A new agent therefore has more than one plausible startup procedure and must synthesize precedence from prose. | `skills/consumer-operation-registry-v0.yaml`, `skills/agent/project-bootstrap-reconcile/SKILL.md`, `skills/agent/bootstrap-existing-project/SKILL.md`, `validators/validate_agent_layer.py`; full PR workflow runs 950-951 passed after the registry/type and bootstrap fixes. |
| HARN-018 | P1 | VERIFIED | Skill lifecycle / discovery | Five pre-Core procedures were retained as ordinary `SKILL.md` files even though they were declared inactive, so generic discovery could treat obsolete workflows as active. The fix moves their text to `docs/legacy/skills/**`, keeps archived lifecycle metadata in the surface registry, and makes validation reject any archived entry that remains on a `SKILL.md` discovery surface. | `docs/legacy/skills/**`, `skills/skill-surface-registry-v0.yaml`, `validators/validate_agent_layer.py`, `validators/validate_harness.py`; full PR workflow run 955 passed after quarantine. |
| HARN-019 | P1 | VERIFIED | Non-capability skill routing | Ten non-owning analysis procedures were grouped as `judgement_only` without executable routing and depended on manual discovery. They are now routed deterministically from canonical Engineering Concern IDs (or explicit method id) through the Consumer Method Registry. `change-transition-design` was separated from this defect: it is a conditional producer whose Reference Model contract remains research and is therefore tracked as an evolution/promotion question rather than forced into method routing. | `skills/consumer-method-registry-v0.yaml`, `method_router.py`, `validators/validate_method_router.py`; full PR workflow run 953 passed. Consumer Pack validation in run 957 also proves unrouted procedures are not exported to target repositories. |
| HARN-020 | P1 | VERIFIED | Skill role/type model | Skill role is inferred from directory rather than declared as an execution contract. `validate_agent_layer.py` treats every `skills/artifacts/**` file as an artifact-production skill and requires Registration/Human Projection/output/acceptance structure even for non-owning analyses that explicitly say they do not provide a Capability by default. This conflates procedure type with storage location and prevents validators/routers from enforcing the new Maintainer / Consumer + operation / method / artifact-production model. | `skills/skill-surface-registry-v0.yaml`, `validators/validate_agent_layer.py`; role validation now follows explicit registry metadata rather than directory names. Full PR workflow run 950 passed after the type-model change. |

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
13. **Instruction ownership / skill routing** — always-on rules, task procedures, canonical policies and inactive guidance must have one explicit owner and deterministic discovery/routing.

## Audit runs

| Run | Date | Perspectives | Result |
|---|---|---|---|
| AUD-001 | 2026-10-01 | Functional state machine, completeness, lifecycle, provider semantics | Established HARN-001..008. |
| AUD-002 | 2026-10-01 | Replay/idempotence, grouped work, contract evolution, end-to-end persistence, hidden same-Authority dependencies | Added HARN-009..013 and additional evidence to HARN-002/HARN-007. |
| AUD-003 | 2026-10-01 | Graph evolution and Decision Pipeline failure/retry semantics | Added HARN-014..015. |
| AUD-004 | 2026-10-01 | Strategic/tactical DDD decomposition of Harness itself, bounded contexts and dependency direction | Added HARN-016, refined HARN-007/HARN-008, and established a machine-enforced context-map ratchet. |
| AUD-005 | 2026-10-01 | Instruction ownership, skill routing, discovery lifecycle and procedural duplication | Added HARN-017..019; captured AGENTS/workbench/artifact-skill scaling work in EVO-021..027 and an active migration plan. |
| AUD-006 | 2026-10-01 | Accepted skill-surface architecture vs current repository realization | Completed full skill inventory, refined HARN-019, added HARN-020, and identified implementation gaps between the accepted Maintainer/Consumer distribution contract and current filesystem/validators. |
| AUD-007 | 2026-10-01 | Post-migration skill/distribution re-audit from clean source/consumer environments | HARN-017..020 no longer reproduced; verified typed surfaces, public/internal operation routing, concern-driven methods, legacy quarantine, clean-target wrapper bootstrap and Consumer Pack isolation. |

## Audit protocol

For every new finding:

1. Search this ledger by root cause and affected invariant.
2. Reuse the existing ID if the root cause is already present.
3. Add new evidence to that item rather than duplicating it.
4. Before a fix, add a failing regression/acceptance scenario that expresses the intended invariant.
5. Mark `FIXED` only after implementation and regression evidence exist on this branch.
6. Mark `VERIFIED` only after a later independent audit perspective fails to reproduce the defect.
