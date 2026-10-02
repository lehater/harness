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

1. a new root `*.py` module cannot appear outside the baseline, declared migration compatibility facades, or an explicit
   permanent bootstrap exception;
2. when a root implementation moves or is deleted, its baseline entry must be removed;
   a retained import/CLI facade is tracked separately by compatibility metadata;
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

Cross-context published contracts are canonicalized in
`docs/design/context-published-contracts-v0.md` and machine-enforced by the
bounded-context validator. Package moves must preserve those contracts rather
than reintroducing representation coupling through new import paths.

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
Harness remains a non-packaged uv project (`tool.uv.package = false`) during
the completed Project Model bootstrap. The explicit source-tree bridge supplies packaged
imports without installation. Installation and removal of the bridge require
a separate packaging/execution-policy change.

PyYAML is pinned to the same 6.0.3 version already required by the clean-target
wrapper. CI execution remains unchanged in this step. Lockfile adoption and a
switch to frozen uv-based CI execution are a separate execution-policy change
and must be validated independently rather than bundled into the layout
foundation.

## Project Model bootstrap migration decision

The first slice moves only Core into `src/harness/project_model/core.py`.
The second slice moves Target State into
`src/harness/project_model/target_state.py`, importing Core directly with `.core`;
root `target_state.py` delegates imports and CLI execution to that canonical owner.
The third slice moves Engineering Graph into
`src/harness/project_model/engineering_graph.py`, importing `.core` and `.target_state`
directly. Root `engineering_graph.py` uses the same module/CLI facade grammar.
The published Integration boundary names `harness.project_model.engineering_graph`;
legacy imports are normalized to that canonical identity before symbol checks.

The migration surfaces are distinct:

- `src/harness/project_model/core.py` is the only canonical Core implementation,
  owned as `harness.project_model.core` by Project Model;
- `harness/__init__.py` is a temporary source-tree import bridge: it sets only
  the package `__path__` to repository-relative `src/harness` and re-exports Core;
- `harness.py` is only the legacy CLI facade, delegating to canonical `main`.

Python resolves `import harness` to the adjacent package, not to the CLI file.
Both package initializers re-export the same canonical Core `__all__`; there
are no independent export lists or duplicate classes/functions. Canonical
`src/harness/__init__.py` has no required initialization that the bridge skips.
No global `sys.path`, `PYTHONPATH`, dynamic file loader or implementation copy
is involved.

Decision: retain this finite bridge while source-tree/Consumer Pack execution
has no Harness installation prerequisite. Installation alone cannot solve the
root `harness.py` name collision. A root implementation package would add a
second physical move. The explicit bridge preserves current execution with one
canonical implementation and can be removed when consumers and distribution
adopt installed-package execution.

`compatibility.import_aliases` maps each legacy import name to a canonical
`target` and its `bridge` path. `compatibility.cli_facades` maps each legacy root
CLI file to its canonical `target`. These are migration state, never context
owners or permanent bootstrap exceptions. The first supported import-bridge
shape is the root `harness` package. `compatibility.module_facades` maps a legacy
module name to its canonical `target` and explicit `mode`, separately from package
bridges. The shared closed grammar supports `import-only` (canonical symbols and
`__all__` re-exports) and `import-and-cli` (the same exports plus canonical `main`
and execution under the `__main__` guard). Unknown modes, extra fields and any
implementation are rejected. These files are tracked separately from the
implementation migration baseline.

The architecture validator discovers non-initializer modules under `src/harness`,
checks their context package, normalizes exact import aliases before dependency,
published-symbol and shared-kernel checks, and validates declared migration
files against a closed delegation grammar. Classes, production functions,
extra execution and path manipulation outside that grammar are rejected.
Packaged initializers carry only declared re-exports or documentation; they
are not independent semantic modules. Relative module imports are checked too.

Consumer Pack v0 explicitly includes the three canonical Project Model modules
(`core.py`, `target_state.py`, `engineering_graph.py`), their package initializers
and the temporary source-tree import bridge. The root `harness.py` CLI facade
and `target_state.py` / `engineering_graph.py` import/CLI facades remain in the
pack. Its acceptance validator runs canonical and legacy imports, identity checks
and CLI execution in a materialized pack without checkout `PYTHONPATH`; root
import-closure analysis alone does not prove packaged dependency closure.
Existing Core, Target State and Engineering Graph acceptance checks protect
HA-A01/HA-A03; isolated pack execution protects HA-A18 (TD-DIST-001/002).

Accepted provider-run bindings include the old Core document and, for several
runs, the root implementation. This move makes 12 previously active evidence
entries from five runs stale under the existing assurance contract. Their
original hashes/outcomes remain historical; deterministic migration checks do
not replace provider judgement evidence or establish a refreshed release claim.

## Reference Model package migration decision

The next coherent slice moves the complete `reference-model` context into
`src/harness/reference_model/`: `project_status.py`, `reference_materializer.py`
and `reference_model_evolution.py`. Only their `harness.reference_model.*`
identities own semantics in the context map. Production function bodies remain
unchanged; explicit `__all__` lists preserve the previous public import surface,
including previously re-exported imports, so legacy and canonical objects have
identical identity.

Root `project_status.py` and `reference_materializer.py` use `import-and-cli`;
root `reference_model_evolution.py` uses `import-only` and gains no CLI. Existing
Target State and Engineering Graph facades use `import-and-cli`. All five use
the same closed grammar, without filename-specific validation rules.

Reference Materializer imports `CoreError` and `validate_engineering_graph` from
canonical Project Model modules. The existing Reference Model -> Project Model
direction permits this dependency and has no separate published-symbol boundary;
no additional DTO or symbol contract is required. Reference Model remains a
supporting/research surface, with no new project-truth or completeness authority.

Consumer Pack v0 adds only the four exact Reference Model package files and keeps
all three root compatibility files. TD-DIST-001/002 evidence extends isolated
pack execution with both import surfaces, all exported-object identities,
Project Status bootstrap/status, Reference Materializer validate/materialize,
and the absence of an evolution CLI. Facade mutation checks reject implementation
and mismatched import-only/import-and-cli grammars at TL1. Existing Reference
Model validators continue to exercise semantics through legacy imports.

No changed file belongs to an existing provider-run execution binding. Under
AR-M11, this slice does not invalidate additional judgement evidence; historical
hashes and existing stale classifications remain unchanged. No provider run is
performed. Existing CI paths already include `src/harness/**`, and the full gate
has no path filter, so no execution-policy change is needed.

## Evidence package migration decision

The complete `evidence` context moves to `src/harness/evidence/`:
`source_boundary.py`, `source_coverage.py` and `source_set.py`. Only their
`harness.evidence.*` identities own semantics; all three root files become
`import-and-cli` facades under the existing closed grammar and leave the root
implementation baseline. No other context moves.

Production function bodies remain unchanged. Explicit `__all__` lists preserve
all previously available public names, including imported names; canonical and
legacy symbols have identical object identity. Each module imports `CoreError`
from `harness.project_model.core` using the existing shared-kernel permission.
Evidence keeps an empty `may_depend_on` list and gains no published boundary.

Consumer Pack v0 keeps the three root files and adds only the four exact Evidence
package files. Existing TD-DIST-001/002 isolated execution evidence covers all
three canonical/legacy imports, every exported-object identity and all three
legacy CLIs without checkout `PYTHONPATH`. Existing facade mutation checks
reject implementation. Source Coverage acceptance and Source Boundary/Source Set
Scenario Suite drivers continue to exercise legacy imports.

No changed file belongs to a provider-run execution binding. AR-M11 therefore
preserves existing evidence currentness; historical hashes and classifications
remain unchanged and no provider run is performed. Existing CI filters cover
`src/harness/**` and the final gate has no path filter; execution policy and check
inventory remain unchanged.

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
