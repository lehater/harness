# Bootstrap external Harness operating model

Status: active implementation

## Goal

Create a reusable Harness repository that can be read independently and applied by an agent to any target project explicitly selected by the user. Target projects remain complete, independent owners of their own truth, instructions and durable execution state.

## Boundary

### External Harness owns
- task-first/progressive-disclosure working method;
- decision/no-invention and knowledge lifecycle protocols;
- software-product change lifecycle;
- Strategic/Tactical DDD methodology;
- generic Skills such as decision resolution, architecture review, domain-model change and knowledge capture;
- generic validation/evaluation mechanics when added.

### Target projects own
- product requirements/domain/architecture/ADRs;
- project-specific guardrails and scoped `AGENTS.md`;
- active plans, blockers, gates and authorization state;
- project-specific Skills when genuinely project-specific;
- code/build/test/deployment commands and CI;
- project-specific validators/eval cases.

## Usage model

There is no required manifest, pin, submodule, runtime bridge or hard repository binding.

A chat/session may be instructed to use Harness on a named target repository. The agent then reads only the relevant Harness method/Skill and only the relevant target-project material. Switching projects discards conversational assumptions and recovers the next project's durable state from that project repository.

## Implementation sequence

### WP1 — Extract reusable methodology
Move generic process from project repositories into `docs/methodology/`, removing product-specific paths and assumptions.

### WP2 — Extract reusable Skills
Move only project-independent Skills into `skills/` and generalize their triggers/bodies.

### WP3 — Clean Nutrition Management
Remove copied generic Harness material from the Nutrition Management bootstrap branch. Keep only product knowledge, project state, local instructions/guardrails and project-specific mechanics.

### WP4 — Validate separation
Check that no external methodology remains authoritative in Nutrition Management and that no Nutrition Management product truth/state leaked into Harness.

### WP5 — Later NAPMS migration
Apply the same separation to NAPMS after the external Harness surface is stable enough to compare behavior without reintroducing context bloat.

## Non-goals

- no project-to-Harness binding contract;
- no pinned Harness revision requirement;
- no central project-state database;
- no scheduler/multi-agent runtime;
- no universal workflow engine;
- no automatic cross-project prioritization.

## Exit criteria

Harness contains reusable methodology/Skills without target-project truth. Nutrition Management contains no duplicated external methodology. An agent can be told in chat to use Harness while working on Nutrition Management or another repository without any repository-level coupling.
