# Bootstrap external Harness operating model

Status: active planning

## Goal

Create a reusable Harness repository that can operate on multiple engineering repositories while every target project remains the durable owner of its own truth, execution state and authorization.

## Boundary

### Move to external Harness

1. **Core operating model**
   - task-first routing and explicit task precedence;
   - progressive disclosure and conditional active-state loading;
   - context loading/rollover and recoverability;
   - decision/no-invention protocol;
   - branch/checkpoint/PR/CI working discipline;
   - generic active-plan/state contract.

2. **Software-product methodology profile**
   - problem/evidence -> requirements -> domain -> architecture -> implementation-readiness lifecycle;
   - gate/reopen/dirty propagation semantics;
   - implementation-authorization contract.

3. **DDD methodology profile**
   - domain change routing;
   - strategic DDD convergence;
   - tactical DDD methodology.

4. **Reusable Skills**
   - core: `execute-work-package`, `resolve-decision`, `agent-harness-design`, `skill-design`;
   - software-product: `implement-slice`, `architecture-review`, stakeholder/user-journey workflows where they remain project-independent;
   - DDD: `domain-model-change`.

5. **Contracts and schemas**
   - target-project manifest (`.harness/project.yaml` or equivalent);
   - Harness revision pin;
   - enabled methodology profiles;
   - project state pointer;
   - project-local Skill/AGENTS extension points;
   - project validation/CI discovery metadata.

6. **Validation and eval framework**
   - Harness structure validation;
   - project-contract validation;
   - Skill routing corpus validation;
   - observed model-routing result scoring;
   - context-overhead metrics;
   - lifecycle-transition corpus machinery.

7. **Bootstrap/templates**
   - minimal root `AGENTS.md` bridge;
   - project manifest example;
   - active-state skeleton;
   - CI integration examples.

8. **Runtime, only as needed**
   - resolve/open a target project;
   - resolve the pinned Harness revision;
   - assemble effective generic + project-local guidance;
   - switch target projects by discarding conversational context and recovering from repository state.

### Keep in each target project

- product/domain/requirements/architecture truth;
- project ADRs and implementation contracts;
- active plan/capsule, blockers, gates and authorization state;
- context problem registers and project roadmaps;
- project-specific scoped `AGENTS.md`;
- project-specific Skills;
- source/build/test/deployment commands and CI workflows;
- validators/eval cases that encode project-specific invariants.

## Lessons adopted from NAPMS Harness simplification

NAPMS PR #127 established several rules that should become generic Harness design constraints rather than remain NAPMS-local:

- the explicit task is primary; an existing active plan must not capture unrelated work;
- target-project active state is loaded only when current execution, lifecycle/gate state or authorization matters;
- lifecycle/process protocols are loaded on demand, not as a mandatory startup stack;
- `execute-work-package` is orchestration only and delegates lifecycle/lease semantics to canonical protocol owners;
- one policy has one owner; validators should check structure/references/invariants instead of forcing repeated policy phrases into root maps, Skills and protocols;
- static routing-corpus validation proves corpus structure only, not actual model routing;
- actual model-routing evaluation should record behavior and cost signals such as files read, Skills loaded, tool calls before first useful action and premature stops;
- mechanically checkable rules belong in deterministic checks where practical rather than bloating agent instructions.

These constraints apply to the extracted Harness unless a later measured experiment demonstrates a better alternative.

## Target shape

```text
harness/
  AGENTS.md
  docs/
    methodology/
      core/
      software-product/
      ddd/
    architecture/
    plans/active/
  skills/
    core/
    software-product/
    ddd/
  contracts/
  validators/
  evals/
  templates/
  runtime/
```

Target projects remain thin:

```text
project/
  AGENTS.md
  .harness/project.yaml
  .agents/skills/        # project-only extensions
  docs/...               # project truth + project state
  .github/workflows/...  # project execution surface
```

## Implementation sequence

### WP1 — Contract and loading architecture

Decide and document how a project pins and loads Harness. Compare at minimum:
- external/sibling checkout resolved by a Harness launcher;
- git submodule or equivalent pinned materialization;
- remote repository reference with a local bridge for capable agents.

Acceptance:
- one canonical project manifest schema;
- deterministic Harness revision pin;
- clear behavior when Harness is unavailable or the pin is invalid;
- target active-state location is discoverable but not automatically loaded for unrelated tasks;
- no requirement to preserve conversation history.

### WP2 — Extract core methodology

Rewrite NAPMS reusable process material into repository-independent core/software-product/DDD profiles. Do not copy NAPMS paths or product assumptions.

Acceptance:
- explicit user task selects task/scope/output; methodology constrains execution but does not silently redirect unrelated work;
- each protocol has one owner;
- active state and lifecycle protocols are loaded only when the current task depends on them;
- optional profiles are explicit rather than globally forced;
- project state is referenced through the project contract, not hard-coded paths except contract defaults;
- lifecycle/authorization state machines are not duplicated into routing maps or unrelated Skills.

### WP3 — Extract reusable Skills

Move only Skills whose trigger/responsibility is project-independent. Generalize descriptions and replace NAPMS-specific paths with contract lookups.

Acceptance:
- concise trigger descriptions;
- `execute-work-package` remains orchestration only: recover current state, identify owner/gate, route to the smallest Skill/protocol, persist material execution-state changes;
- isolated audit/review/research/implementation tasks do not load current-plan orchestration unless they depend on it;
- neighboring Skills are not preloaded speculatively;
- no product truth in Skill bodies;
- project-local extension/override boundary documented;
- routing eval cases cover confusable neighboring Skills.

### WP4 — Validation/evaluation framework

Generalize NAPMS Harness validators into reusable Harness and project-contract validators.

Acceptance:
- deterministic checks validate ownership/schema/reference invariants rather than duplicated policy prose;
- static routing-corpus validation explicitly states that no model was executed;
- observed model-routing evaluation is a separate surface;
- observed evaluations can compare at least `files_read`, `skills_loaded`, `tool_calls_before_first_action` and `stopped_early` against a baseline;
- lifecycle/eval machinery supports enabled profiles only.

### WP5 — NAPMS dual-run migration

Bind NAPMS to a pinned Harness revision while retaining its current local Harness temporarily. Compare effective guidance and gates before deleting duplicates.

Acceptance:
- existing NAPMS hosted gates stay green;
- current NAPMS project state remains repository-local;
- representative tasks preserve correct routing while not increasing unnecessary files/Skills/tool calls or premature stops;
- no generic methodology exists in two authoritative locations after cutover.

### WP6 — Nutrition Management bootstrap

Connect the minimal Nutrition Management repository directly to external Harness rather than copying NAPMS Harness into it.

Acceptance:
- new project can establish requirements/domain/architecture/execution state using the shared methodology;
- switching NAPMS -> Nutrition Management -> NAPMS recovers each project only from its repository plus pinned Harness revision.

## Non-goals for the first version

- no central database of project state;
- no multi-agent scheduler;
- no universal workflow/BPMN engine;
- no automatic cross-project prioritization;
- no removal of NAPMS local Harness before dual-run parity is demonstrated;
- no weakening or fast-path bypass of implementation authorization until measurements show that authorization itself, rather than context/routing duplication, is the remaining material overhead.

## Exit criteria

The external Harness is proven when both NAPMS and Nutrition Management can use the same pinned methodology/runtime, preserve all durable state locally, recover correctly after project switching without relying on prior conversation context, and retain task-routing quality without reintroducing unnecessary context fan-out.

## Next

Execute WP1 first. Do not bulk-copy NAPMS process/Skills before the project binding and loading model is decided.
