# Harness runtime contract

Version 1 does not require a daemon, scheduler or central project-state database.

A Harness-aware runner needs only to:

1. open the selected target repository;
2. read `.harness/project.yaml`;
3. resolve the pinned external Harness commit;
4. assemble task-relevant generic Harness guidance plus target-project-local guidance;
5. execute against the target repository;
6. discard conversational context when switching projects and recover the next project from its repository plus its pinned Harness revision.

The target repository remains the durable owner of product truth, active execution state, blockers, gates and authorization.

Do not cache a different Harness revision as an implicit fallback. Operational caches may accelerate loading but must preserve the pinned revision identity.
