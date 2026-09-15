# Target project binding contract

A target repository binds to Harness through `.harness/project.yaml`.

## Required fields

```yaml
version: 1
harness:
  repository: https://github.com/lehater/harness
  revision: <full git commit SHA>
  profiles:
    - core
project:
  active_state: docs/plans/active/README.md
```

`harness.revision` is immutable and must be a full commit SHA. Do not use a branch, tag, `main`, or `latest` as the durable project pin.

Optional profiles currently defined by Harness are `software-product` and `ddd`.

Optional project-local extension points may be declared when they exist:

```yaml
project:
  local_agents: AGENTS.md
  local_skills: .agents/skills
  validation_commands:
    - make test
```

## Loading rule

1. Read the target repository's root `AGENTS.md` and `.harness/project.yaml`.
2. Resolve exactly `harness.repository@harness.revision`.
3. Load Harness `AGENTS.md` and only the enabled methodology/Skill material required by the explicit task.
4. Load `project.active_state` only when current execution, lifecycle/gate state or authorization matters.
5. Load project-local Skills only when present and applicable.

Project-local truth wins for product/domain/architecture facts. Harness owns reusable methodology only.

## Failure behavior

If the pinned Harness repository/revision cannot be resolved, do not silently fall back to another revision or to copied local methodology. Report the binding as unavailable and stop only work that depends on Harness guidance.

Conversation history is never a recovery dependency.
