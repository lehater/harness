# CDR CREATE integration — noncanonical end-to-end experimental route

Status: **EXPERIMENTAL READ-ONLY** in Draft PR #220. This is an integration increment, not permission to create or remove accepted Engineering Graph `requires`. It neither retrofits existing accepted project capabilities nor changes PREP or Harness main.

## Where this fits the native process

The native Decision Pipeline already evaluates `CREATE`, `REVISION`, `REDO`, its canonical read set, Decision Governance and Semantic Admission. Its admission logic assumes the target production and its `requires` already exist. It does not independently admit mutations to the *Engineering Graph topology*.

Therefore CDR **must precede any newly proposed topology change**, and its result may only block a `CREATE` that would otherwise run without independently settled dependencies. It cannot override Semantic Admission or invent an Authority acceptance event.

`evals/cdr_create_workflow.py` composes the existing generic `cdr_operational` source-only discovery, external evaluator request and response binding, cycle-aware reconciliation, and the existing `cdr_governance_packet`. This reduces the previous stand-alone tests to one concrete creation handoff. The provider catalog comes from the current project Engineering Graph producer IDs, Core artifacts, individually revised semantic-baseline entries and source files; it is **automatically enumerated**, not an operator-supplied shortlist.

The catalog enumerates **eligible public document sources**; it does not claim complete semantic exports, entailment, independent Authority adjudication or direct consumption. The target output obligations still come from a scoped operator draft, not an independently accepted target output contract. Existing `requires` are omitted from Phase A model-visible context. The original accepted graph is read in Phase B only for comparison/cycles.

## Process

1. **Prepare:** validate exact, clean pinned project commit; load draft target obligations, source-only provider catalog and build source-bound tool-disabled evaluator request. Output `handoff` with deterministic SHA256. No target graph edges or post-model answers are sent to the model.
2. **External evaluate:** the evaluator returns an exact request-bound `harness-dependency-resolution-evaluator-response`; no graph write, no repo tools exposed during blind phase.
3. **Reconcile:** regenerate Phase A from the pinned inputs; reject changed handoff, forged request/case IDs, malformed target coverage or cited source indexes. Existing direct dependencies are compared with proposals but never deleted on absence of support. A new provider whose existing dependency path reaches the target (including not-yet-declared target) is **BLOCKED_BY_CYCLE**.
4. **Governance dossier:** independently materialize specific target output and directness review questions using the existing experimental Governance packet mechanism. The result is `BLOCKED_PENDING_INDEPENDENT_AUTHORITY_DECISIONS` or `BLOCKED_INVALID_PROPOSED_TOPOLOGY`, never automatic adoption.
5. **Check:** regenerate everything from source and frozen model response before checking the operator's review draft. A consistent draft remains `DRAFT_VALIDATED_PENDING_TRUSTED_AUTHORITY`. No reviewer role/name/hash may grant acceptance.
6. **Native CREATE opt-in:** an operator supplies the generated `harness-cdr-create-readiness-v1` gate to `derive_decision_roadmap(cdr_create_gate=...)` or `python -m harness.application.decision_pipeline ... --cdr-create-gate <gate.json>`. When this specific Capability is otherwise `CREATE`, it is moved from `READY` into `BLOCKED: CDR_CREATE_AUTHORITY_REVIEW_PENDING`. Other production/revision paths remain unchanged. Unknown, forged `RESOLVED`, and fake accepted gates fail closed.

This is **opt-in**. Automatically enforcing across every already accepted graph would retroactively block legacy Capability creation without independently reviewed contracts and is **not authorized by this experiment**.

## Operator commands

Starting from a clean pinned project and a draft scoped input contract:

```sh
make cdr-create-prepare \
  PROJECT_ROOT=/path/to/project PROJECT_COMMIT=<sha> \
  CDR_INTAKE=/path/to/intake.yaml CDR_OUTPUT=/tmp/handoff.json

# Feed the handoff's "request" object to an external tool-disabled evaluator.
# Preserve its original JSON response independently of Phase B.

make cdr-create-reconcile \
  PROJECT_ROOT=/path/to/project PROJECT_COMMIT=<sha> \
  CDR_INTAKE=/path/to/intake.yaml CDR_HANDOFF=/tmp/handoff.json \
  CDR_RESPONSE=/tmp/evaluator-response.json CDR_OUTPUT=/tmp/review.json

# A review draft is prepared separately against /tmp/review.json's dossier;
# the user/agent cannot claim Authority approval via draft metadata.
make cdr-create-check \
  PROJECT_ROOT=/path/to/project PROJECT_COMMIT=<sha> \
  CDR_INTAKE=/path/to/intake.yaml CDR_HANDOFF=/tmp/handoff.json \
  CDR_RESPONSE=/tmp/evaluator-response.json \
  CDR_REVIEW=/tmp/review.json CDR_DRAFT=/tmp/operator-draft.json \
  CDR_OUTPUT=/tmp/checked.json
```

The `review.json` contains a `gate` object. Pass only that object as `--cdr-create-gate`; it can **block** native execution, never authorize one. Consumer frontiers derive this blocked status through the usual Decision Pipeline → Project Frontier flow; no new Core or semantic admission mechanism is introduced.

## Verified and blocked remainder

- Synthetic create flow covers automatic discovery, exact source immutability, request-bound evaluator evidence, target output coverage, cycle closure through an undeclared target, source revision integrity, generation/consistency of Governance draft and explicit Make entrypoints.
- A separate native Decision Pipeline test covers blocking exactly one otherwise READY `CREATE`, leaving other selections alone, rejecting false positive `RESOLVED` gates.
- Full `make harness-check`, Greenfield graph regression and all focused policy checks are required on an exact PR HEAD before considering this integration checkpoint complete.

**Required before rollout:** a trusted project-authorized Authority decision event bound to exact output obligation and exported claim revisions, independently verified material directness, accepted provider coverage, and a separately designed graph changeset admission transaction. No authenticated reviewer/approval or canonical graph-write capability is available in this experiment. This is a governance blocker, not a reason to fabricate permission or silently adopt model suggestions.

There is no auto-merge, PREP update, main update or canonical acceptance in this experiment.
