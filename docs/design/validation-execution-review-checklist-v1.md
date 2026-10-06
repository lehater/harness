# Validation Execution Review Checklist v1

Status: canonical guidance.

## Purpose

Provide an applicability-driven review method for CI and other validation execution without creating a new Authority, Capability family, knowledge kind, dependency graph, check registry or execution optimizer.

The checklist helps an agent review whether accepted verification evidence is executed at the right decision boundary and whether the current execution topology is unnecessarily costly or complex.

It does not own verification truth. Verification/Test Design defines what must be proven; Repository Realization / Implementation Design owns the selected execution and gate realization.

## When to apply

Apply when merge/release validation is materially non-trivial, for example when there are:

- multiple suites, jobs or trigger surfaces;
- conditional or affected execution;
- scheduled, external/provider-backed or nondeterministic checks;
- meaningful setup/runtime cost;
- multiple merge/release decision boundaries;
- uncertainty about whether required evidence actually reaches the authoritative gate.

A project with no applicable gate, or one obvious cheap deterministic gate, does not need an elaborate execution analysis. Repository Realization completeness still applies.

## Inputs

Use the project-native sources that already own the relevant truth:

- accepted Verification/Test Design obligations and evidence contracts;
- executable checks/tests/build validators and their canonical commands;
- Repository Realization and current CI/workflow configuration;
- repository/package/build topology and any existing authoritative dependency graph;
- merge/release policy and decision boundaries;
- observed runtime, failure and setup-cost evidence when available.

Do not invent a second dependency model solely for CI selection.

## Review planes

For each applicable plane, record only findings supported by project evidence.

| Plane | Questions to check |
| --- | --- |
| Evidence coverage | What evidence is required for this decision boundary? Which executable checks produce it? Can required evidence be omitted while the gate still reports success? |
| Authoritative boundary | Which local/PR/integration/release execution is authoritative? Are convenience checks accidentally acting as a second source of truth? |
| Candidate and input binding | Does the evidence correspond to the revision/integration candidate actually being accepted? If results are reused, is effective-input equivalence trusted and explicit? |
| Trigger topology | When does each check run? Is the same evidence executed multiple times for the same effective inputs and decision context without a reason? |
| Impact/selectivity | What allows a check to be skipped? Is the selector based on authoritative information? Does unknown impact conservatively broaden rather than silently reduce required evidence? |
| Dependency source | Which graph or relation supports affected execution? Is an existing build/package/capability graph reused where it models the needed relation, rather than duplicated in workflow rules? |
| Ordering and parallelism | Which jobs have real prerequisites? Which ordering is only an optimization? Would parallelism reduce decision latency or merely consume extra work before an early failure? |
| Cost and critical path | Where is time actually spent: setup, dependency resolution, build, tests, external calls or orchestration? Is an optimization justified by measured cost rather than test labels? |
| Reuse and caching | Can setup, dependencies, build outputs or test results be reused safely from declared/equivalent inputs? Does reuse preserve verification semantics rather than bypass them? |
| Determinism and externality | Which checks are deterministic, flaky, environment-sensitive or provider-backed? What role should each play at merge/release boundaries according to project policy? |
| Evolution and self-change | What happens when CI configuration, selectors, dependency metadata or validation tooling itself changes? Is broader/self-validation available, and when should the topology be re-measured? |

## Decision classification

Classify any recommended change using the existing Repository Realization decision classes rather than inventing a CI-specific taxonomy:

- `universal-invariant`;
- `conditional-invariant`;
- `project-decision`;
- `concrete-tool-choice`;
- `generated-projection`;
- `implementation-freedom`.

If a recommendation would change Verification, Quality, Security, Product or Architecture semantics, route it to the owning Authority instead of accepting it as Implementation Design.

## Basis status

Every material finding or recommendation has one basis status:

- `SUPPORTED` — repository facts or accepted engineering knowledge are sufficient for the conclusion;
- `MEASURE` — runtime/economic evidence is insufficient; collect it before optimizing;
- `QUESTION` — an owning semantic/policy decision is missing or unresolved.

`MEASURE` and `QUESTION` are not permission to guess.

## Output

The review itself is analysis, not a new canonical artifact requirement. A useful result is a small set of records such as:

```text
plane
observation
risk
evidence
decision_class
basis: SUPPORTED | MEASURE | QUESTION
recommended_action
owner
```

Only accepted decisions that change project realization are written back to Repository Realization / Implementation Design and then projected into platform-specific CI configuration.

## Non-rules

This checklist does not imply that:

- E2E tests are automatically expensive or unit tests automatically cheap;
- affected/selective execution is always preferable to running all required checks;
- every project needs an exhaustive final gate;
- cheapest checks must always run before expensive checks;
- parallel execution is always faster or cheaper overall;
- external/provider-backed checks must always be manual or non-blocking;
- a previous green result is reusable without trusted effective-input equivalence;
- CI should maintain its own dependency graph when an authoritative graph already models the required relation;
- a simple cheap pipeline should be optimized without measured benefit;
- GitHub Actions, GitLab CI or any other platform construct is a Harness semantic primitive.

## Sanity probes

### Small frontend

If all required deterministic checks are cheap relative to orchestration overhead and already cover the merge decision, the checklist should permit an always-on PR gate and return `MEASURE` rather than invent affected selection.

### Monorepo with expensive integration suites

If an authoritative package/build graph exists and checks are materially expensive, the checklist may support dependency-aware selection as a project decision. Unknown or unmapped impact must not silently remove required evidence. The workflow should reuse the authoritative graph rather than encode a second hand-maintained dependency graph.

### Prep regression

Prep's current design is compatible with the checklist without becoming a universal template: cheap frontend/repository validation remains always-on, an explicitly isolated knowledge experiment uses conditional execution, broader integrated validation runs at different boundaries, and the choices are justified by project measurements and ownership. The transferable result is the review method, not Prep's concrete topology.
