# Repository Layout v0

Status: canonical migration target.

## Purpose

Define the physical repository structure that Harness converges toward after the
logical bounded-context boundaries have been established.

The repository already has a canonical semantic ownership map in
`spec/architecture/harness-context-map-v0.yaml`. This contract makes physical
Python packaging converge on that ownership instead of allowing the repository
root to remain the implementation namespace.

## Problem

Harness currently keeps most runtime modules directly in the repository root.
That makes the root simultaneously act as:

- the repository control surface;
- the Python import namespace;
- the application/orchestration layer;
- several bounded contexts;
- experiment/evaluation infrastructure.

Logical context ownership is already enforced, so the flat physical layout no
longer communicates the architecture that the dependency ratchet protects.

## Target runtime layout

The target runtime package is:

```text
src/harness/
  project_model/
  reference_model/
  coverage/
  assurance/
  decision/
  evidence/
  integration/
  workspace/
  application/
```

Package names are a physical projection of the existing bounded contexts. They
do not create new domain ownership and must not become a second context map.

The machine-readable mapping is
`spec/architecture/repository-layout-v0.yaml`.

## Repository surfaces

The intended top-level responsibilities are:

```text
src/harness/**     production/runtime Python
tests/**           behavior verification
checks/**          repository/architecture/CI policy checks
evals/**           provider/agent evaluation infrastructure
experiments/**     non-production research code
spec/**            machine-readable contracts and fixtures
skills/**          routed agent procedures and registries
docs/**            human-readable canonical/design/research material
examples/**        controlled example projects/fixtures
distribution/**    bootstrap/distribution transport
.github/**         repository automation
```

These are responsibility boundaries, not a requirement to create every
directory before it has content.

## Root Python migration ratchet

During migration the current root Python modules are an explicit finite
baseline. The architecture validator enforces:

1. a new root `*.py` module cannot appear outside the baseline or an explicit
   permanent bootstrap exception;
2. when a root module is moved or deleted, its baseline entry must be removed;
3. every baseline/exception module remains classified by the canonical context
   map or as research/test infrastructure;
4. the target package mapping covers every bounded context/application layer.

The baseline is migration state only. It is not permission to keep the flat
layout indefinitely.

A permanent root Python exception requires a concrete bootstrap/compatibility
reason. Convenience or import-shortening is not sufficient.

## Migration rules

Physical moves must preserve these invariants:

- no Harness domain semantics change merely because a module moves;
- the canonical context map remains the owner of semantic boundaries and
  dependency direction;
- each move uses the destination package assigned to that context;
- import-boundary validation remains green after every migration step;
- Consumer Pack/bootstrap compatibility is preserved explicitly rather than by
  keeping arbitrary implementation modules in the root;
- experiments/evaluations are separated from production runtime only after
  their actual consumer/runtime role is established.

Cross-context published contracts from EVO-011 remain an independent design
concern. A package move must not be used to hide unresolved representation
coupling.

## Migration order

Use dependency direction to minimize temporary compatibility surfaces:

1. package/project metadata and the root-module ratchet;
2. leaf contexts: Project Model, Evidence, Decision;
3. Reference Model, Assurance, Integration;
4. Coverage and Workspace;
5. Application Layer;
6. experiment/evaluation separation;
7. test/check physical classification;
8. Consumer Pack path-decoupling and compatibility cleanup.

Each implementation step is a separate branch/PR from the current integrated
`main`, with the full deterministic gate run before integration.

## Python project metadata

`pyproject.toml` is the repository-level dependency/tooling declaration.
During the foundation step Harness remains a non-packaged uv project
(`tool.uv.package = false`) because production modules have not moved under
`src/harness` yet.

PyYAML is pinned to the same 6.0.3 version already required by the clean-target
wrapper. CI execution remains unchanged in this step. Lockfile adoption and a
switch to frozen uv-based CI execution are a separate execution-policy change
and must be validated independently rather than bundled into the layout
foundation.

## Evidence

This migration target is enforced at TL0 by
`validators/validate_context_boundaries.py`, which now validates both the
semantic context map and the physical-layout migration ratchet.

Every coherent migration candidate must also pass the existing full
`make harness-check` gate before integration.

## Non-goals

This contract does not:

- introduce new Harness bounded contexts;
- change Core entities or engineering semantics;
- require a repository-wide module move in one PR;
- convert all validators to a new test framework;
- change Consumer Pack API/version semantics;
- define a published Python package/release version.
