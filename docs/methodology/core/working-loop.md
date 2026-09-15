# Working loop

## Persistence model

```text
conversation = disposable execution context
project canonical docs = durable accepted knowledge
project active state = compact resumable execution state
working branch = durable WIP/checkpoints
main = curated integrated history
```

Checkpoint when a coherent increment is complete, an owner/stage changes, the next task depends on the new state, or losing work would be costly.

Before discarding conversation context: promote accepted truth into project-local canonical owners; preserve consequential evidence separately from interpretation when needed; record material unresolved blockers/unknowns in the smallest project owner; update the configured active-state artifact when resumable state changed; remove duplicated/transient reasoning.

Fresh-session recovery is task-first: target root `AGENTS.md` -> target `.harness/project.yaml` -> pinned Harness guidance required by the task -> nearest target scoped `AGENTS.md` -> target active state only when current execution matters -> minimal canonical working set.

Do not reload historical baselines or all methodology by default.

Ordinary work happens on a branch and integrates through a coherent PR according to target-project rules. If implementation exposes an upstream semantic problem, stop the affected slice, preserve useful WIP, record the finding and return to the owning Requirements/Domain/Architecture layer before continuing.
