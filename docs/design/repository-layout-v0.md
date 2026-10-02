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

Before the package migration, Harness kept runtime modules directly in the repository root.
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
dotted Python module identity to its canonical `target` and explicit `mode`, separately from package
bridges. The shared closed grammar supports `import-only` (canonical symbols and
`__all__` re-exports) and `import-and-cli` (the same exports plus canonical `main`
and execution under the `__main__` guard). Unknown modes, extra fields and any
implementation are rejected. Every dotted component must be a Python identifier;
the physical file is mechanically derived by replacing dots with slashes and
appending `.py` (for example, `foo.bar.baz` maps to `foo/bar/baz.py`).
Nested facades are excluded from runtime semantic ownership; the root migration
ratchet considers only root files. Exact dotted aliases normalize to their
canonical targets, and owned runtime imports may not use them, including
`from foo import bar` when `foo.bar` is an alias. These files are tracked separately from the
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

## Decision package migration decision

Architecture decision record: ADR-DECISION-PACKAGE-V0 (accepted).

The root implementation namespace obscured the already enforced Decision
ownership boundary. Following the existing Project Model, Reference Model and
Evidence mechanism, the complete `decision` context moves in one coherent slice
into `src/harness/decision/`. Its four canonical modules are:

- `harness.decision.decision_execution_assurance`;
- `harness.decision.decision_exploration`;
- `harness.decision.decision_explorer_contract`;
- `harness.decision.decision_governance`.

All four root files remain temporary `import-only` facades under the existing
closed grammar; none gains a CLI. Explicit canonical `__all__` lists preserve
the observed legacy public surface, including imported names. Function/class
bodies remain unchanged, and every exported legacy object and `__all__` shares
canonical identity. Exploration imports the Explorer contract directly inside
the canonical package. Application and Scenario Suite consumers retain their
legacy imports, normalized by the existing compatibility registry.

Decision retains `may_depend_on: []`. `CoreError` imports use canonical
`harness.project_model.core` under the existing shared-kernel permission; no
published boundary, new bridge or installed-package execution is introduced.
The temporary source-tree bridge and `tool.uv.package = false` remain unchanged.

Consumer Pack `consumer_api: v0` retains the four root facades and adds exactly
the four canonical modules plus `src/harness/decision/__init__.py` through
`exact_files`, without expanding prefixes. Existing TD-DIST-001/002 evidence
extends isolated-pack checks with the frozen pre-move public surfaces, all
exported-object and `__all__` identities, canonical file locations, shared-kernel
identity, absence of CLI entrypoints and existing Decision scenarios through
distributed Application consumers. The subprocess removes checkout `PYTHONPATH`
and requires no installed Harness package. TL0/TL1 facade grammar/normalization
checks and existing Decision admission/governance/scenario evidence protect the
physical migration; no duplicate semantic tests or provider judgement are needed.

All seven provider-run records under `spec/assurance/evidence/**` were checked
against the four moved files and the complete changed-file set. No changed file
belongs to an execution binding. Under AR-M11, no additional evidence becomes
stale; historical hashes, outcomes and existing stale classifications remain
unchanged. No provider run is performed.

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

## Coverage package migration decision

The complete `coverage` context migrates in one coherent slice to
`src/harness/coverage/`: `architecture_driver_closure.py`,
`concern_activation.py`, `coverage_obligations.py`, `coverage_planner.py` and
`engineering_coverage.py`. Only their `harness.coverage.*` identities own
semantics. Root Architecture Driver Closure and Coverage Obligations use
`import-only`; Concern Activation, Coverage Planner and Engineering Coverage
use `import-and-cli`. These reuse the existing closed facade grammar and
source-tree bridge; no new packaging or execution mechanism is introduced.

Explicit `__all__` freezes each pre-move public surface, including imported
names. Production function/class ASTs are independently equivalent to the
reviewed baseline. Engineering Coverage's module-level `ROOT` is adjusted to
preserve repository-relative policy lookup after relocation. Internal Coverage
imports are relative; Project Model imports use canonical Core and Engineering
Graph identities. Coverage retains only the `project-model` and `assurance`
dependency directions.

The existing Coverage -> Assurance published boundary remains exactly
`harness.assurance.semantic_acceptance.coverage_assurance_view` and
`harness.assurance.semantic_acceptance.coverage_invalidation_closure`. Canonical
Coverage imports the migrated Assurance implementation with exactly those
published symbols. No Assurance implementation is copied and no new DTO/API is
introduced.

Consumer Pack v0 retains all five root facades and adds exactly the Coverage
initializer plus the five implementation files through `exact_files`.
TD-DIST-001/002 isolated-pack evidence checks frozen exports, object identity,
canonical locations, CLI presence/absence, canonical Project Model identity,
relative internal imports and policy lookup without checkout `PYTHONPATH` or an
installed Harness package. Fresh CLI processes exercise all three existing CLIs
with distributed research fixtures. Published-boundary mutation checks reject
broad Assurance access and non-published symbols from canonical Coverage;
existing facade grammar mutations and alias normalization remain enforced.
Existing HA-A06 validators and Scenario Suite cases retain legacy imports and
protect the same semantic behavior.

Repository-wide consumer discovery classified internal Coverage imports,
Application (`coverage_application`, `project_frontier`), Scenario Suite
(`scenario_drivers`), validators/tests, experiments/research, docs/spec and
Consumer Pack declarations. Only internal dependencies and ownership/distribution
contracts change; neighboring consumers retain compatibility imports. Two validators that directly
exercise private helpers import those helpers from canonical Coverage while
public semantic checks retain the compatibility surface. Historical
audit/research prose is preserved. Assurance execution bindings contain no
Coverage consumer match and no changed-file intersection.

All seven provider evidence records and their 76 `execution_bindings.files`
entries were compared with the complete changed-file set, including validators,
contracts and documentation. There is no intersection: AR-M11 introduces no
additional staleness. Historical hashes, outcomes and currentness classifications
remain unchanged; no provider judgement run is performed. Deterministic migration
evidence does not substitute for provider judgement.

## Workspace package migration decision

Architecture decision record: ADR-WORKSPACE-PACKAGE-V0 (accepted).

The complete `workspace` context moves as one coherent slice into
`src/harness/workspace/`: `frontend_interface_knowledge.py`,
`frontend_screen_contracts.py`, `human_projection.py` and `workspace.py`.
Their four `harness.workspace.*` identities alone own implementation semantics.
The initializer is documentation-only. Root frontend modules use `import-only`;
Human Projection and Workspace use `import-and-cli`, preserving their existing
CLIs through the same closed facade grammar used by earlier migrations.
No new bridge or installed-package execution is introduced; the existing
source-tree bridge and `tool.uv.package = false` remain unchanged.

Explicit `__all__` preserves the observed pre-move public names, including
imported names. Legacy/canonical export objects and `__all__` share identity.
Consumer Pack validation freezes those surfaces and whole-module AST digests
from reviewed baseline `725f37754b1040c74ed48ead9758e4767ee31f50`.
Reversing only canonical Project Model import normalization and removing
`__all__` reproduces those digests, independently proving function/class and
module equivalence; no path adaptation or semantic redesign is needed.
Human Projection imports canonical Core and Engineering Graph; Workspace imports
canonical Core and Target State rather than their compatibility aliases.

Workspace retains exactly `may_depend_on: [project-model, integration]`.
Human Projection imports only `validate_project_alignment` from canonical
`harness.integration.integration_alignment`. This is the existing ordinary
Workspace -> Integration direction, with no new published boundary or copied
Integration semantics.
Ownership/alias assertions and forbidden Application/Coverage/Assurance import
mutations exercise the existing context validator; isolated-pack identity
checks bind alignment to the actual Integration implementation.

Consumer Pack retains `consumer_api: v0` and all four root facades. Only the
Workspace initializer and four canonical modules are added through `exact_files`;
`include_prefixes` is unchanged. Reused TD-DIST-001/002 evidence checks frozen
exports, canonical paths, CLI presence/absence, canonical Project Model identity,
import direction and full-module AST equivalence in a materialized pack without
checkout `PYTHONPATH` or an installed Harness package. Fresh processes run
Workspace validate/render against the managed fixture and Human Projection
compile against the existing unified-model/recipe fixtures. The distributed
managed-workspace scenario checks composition; frontend scenarios requiring
`examples/` run in the checkout without expanding the distribution.
Existing HA-A17 frontend/workspace/human-projection validators and Scenario Suite
continue to protect behavior; existing facade grammar mutations protect delegation.

Repository-wide search classified Workspace internal consumers (no internal
module imports), Application/Integration (no direct Workspace imports), Scenario
Suite (`scenario_drivers`), validators/tests, skills, docs/spec, Consumer Pack and
assurance bindings. Skills retain their managed-workspace/frontend/projection
procedures and legacy CLI entrypoints. Neighboring public consumers retain legacy
imports. Only the deep-dependency validator's private `_task_rows` import moves
to canonical Workspace, because private names are outside `import *` exports.
Historical audit/research documents remain unchanged.

All seven provider-run records under `spec/assurance/evidence/**` and every
`execution_bindings.files` list were compared with the complete PR changed-file
set. There are no intersections. Under AR-M11 this slice introduces no additional
staleness; historical hashes, outcomes and currentness classifications remain
unchanged. No provider judgement run is performed. There is no scope deviation.

## Runtime canonical-import normalization

Architecture decision (ADR): compatibility facades are no longer an internal
runtime dependency mechanism. Modules owned by `contexts.*.modules` in the
canonical context map must import migrated contexts through their canonical
identities. The architecture validator rejects exact compatibility aliases for
both `from ... import ...` and `import ...`, before the existing dependency and
published-symbol checks. Unmigrated root identities remain canonical; context
ownership, dependency directions and published boundaries are unchanged.

Internal migration compatibility and public Consumer API compatibility have
different lifetimes. `repository-layout-v0.yaml` owns the transitional alias
mapping under `compatibility`; `consumer-pack-v0.yaml` owns distribution and
public exposure through `root_files`, `exact_files` and `consumer_api: v0`.
No duplicate compatibility registry is introduced. Existing import/CLI facades
and the source-tree bridge remain unchanged because Consumer Pack v0 exposes
them. Facade removal is deferred to an explicit Consumer API compatibility
decision. Validators, tests, ignored research/scenario modules and external
consumers may continue exercising legacy surfaces.

Evidence uses TL0/TL1 exact-alias mutation/control checks and existing
TD-DIST-001/002 isolated Consumer Pack import, identity and CLI checks (HA-A18).
All 85 objects imported by the 40 normalized runtime imports were checked for
identity against their canonical re-exports. Production bodies, signatures and
CLI behavior are unchanged. The Workspace forbidden-dependency mutation uses
the canonical Coverage identity so it continues testing dependency direction
rather than being intercepted by the new alias guard.

All seven provider-run records under `spec/assurance/evidence/**` and every
`execution_bindings.files` list were compared with the complete changed-file
set. Four records intersect at `skill_router.py`: first-wave runs 36942421201
and 36947887869, TL4 existing-project run 36949909315, and TL5 known-project run
36952038645. All seven records were already stale on the base revision. Binding
intersection exists, but there is no new current -> stale transition. Historical
hashes, outcomes and currentness classifications remain unchanged. This
mechanical import normalization requires deterministic assurance only; no
provider judgement run or refreshed judgement claim is introduced.


## Integration and Assurance package migration decision

Architecture decision record: ADR-INTEGRATION-ASSURANCE-PACKAGE-V0.
Status: accepted.

Nested compatibility modules preserve import identity and module CLI identity,
not direct filesystem-script execution. `import adapters.foo` and
`python -m adapters.foo` remain compatibility surfaces. `python adapters/foo.py`
depends on filesystem layout and is intentionally unsupported after migration.
Facades retain the existing closed grammar without path bootstrapping.
Canonical nested CLIs use `python -m harness.integration.adapters.canonical_graph`
and `python -m harness.assurance.adapters.copilot_live_calibration_evaluator`.
Consumer v0 retains the corresponding legacy dotted module entrypoints.
The distribution manifest promises included files and import identities, not
direct nested file execution; no Consumer API bump is required.

The existing context map owns the Integration and Assurance boundaries, but
physical implementations still occupied root and adapter namespaces. One
coherent migration moves all three Integration and nine Assurance modules into
`src/harness/integration/` and `src/harness/assurance/`, including their respective
`adapters/` packages. Initializers contain documentation only. Context ownership
uses canonical identities exclusively, with unchanged dependency directions and
an empty known-violation ratchet.

The existing `compatibility.module_facades` mechanism generalizes to dotted
identities. Both legacy adapter paths are mechanically located and checked
against the same delegation grammar as root facades. There is no second facade
registry or filename-specific ownership rule. Nested aliases are excluded from
the semantic inventory; root implementation baseline entries are removed only
for the ten migrated root files.

All owned runtime consumers use canonical imports. Integration retains its
published Project Model symbol boundary. Coverage uses only the two existing
published Assurance symbols under their canonical module identity; neither
boundary widens. Assurance internally uses canonical identities, with no new
dependency. Application remained physically unchanged in that slice; its subsequent migration is recorded below.

Explicit `__all__` freezes the pre-move public surfaces from `d28f4cc`, including
imported public names and the private adapter helpers already imported by
acceptance validators. Every legacy export and export list shares canonical
object identity. Whole-module AST fingerprints reverse only approved imports
and remove the explicit export assignment, proving unchanged module logic,
function/class bodies and CLI guards. No repository-relative adaptation is
needed by these twelve implementations.

Consumer API remains v0. Root files and the `adapters/` include prefix stay in
the Pack; sixteen canonical files are added through `exact_files`. Reused
TD-DIST-001/002 evidence checks canonical locations, frozen surfaces, identity,
owned import discipline, published boundaries and nested facade mutations in
an isolated Pack without checkout `PYTHONPATH` or package installation.

Evidence scope: HA-A17 ownership/projection, HA-A18 distribution compatibility,
and unchanged HA-A12/A14/A20 deterministic semantic/currentness/calibration
behavior. Existing subsystem fixtures and the full Scenario Suite are reused;
new TL1 mutations target only facade metadata, closed grammar and import rules.
The entire changed-file set is compared with all provider execution bindings;
intersection is empty for all seven execution-bound provider records:
`first-wave-provider-run-36928079710`, `first-wave-provider-run-36942421201`,
`first-wave-provider-run-36947887869`, `tl4-existing-project-provider-run-36949909315`,
`tl5-known-project-provider-run-36952038645`,
`release-critical-formation-provider-run-36953091767`, and
`a04-r02-provider-run-36953433978`. This includes the changed
`.github/workflows/live-calibration-copilot.yml`, which none of those bindings
contains. All seven were already stale; there is no new currentness transition.
Historical results, hashes and existing stale states remain
unchanged. This physical migration makes no new provider-judgement claim and
requires no provider run.


## Application package migration decision

Architecture decision record: ADR-APPLICATION-PACKAGE-V0.
Status: accepted.

The fifteen ordinary Application runtime modules move together into
`src/harness/application/`: `agent_router`, `authority_context`, `consumer_pack`,
`coverage_application`, `decision_explorer_request`, `decision_pipeline`,
`graph_doctor`, `method_router`, `project_frontier`, `project_publication`,
`semantic_admission`, `semantic_closure`, `semantic_questions`,
`skill_invariant_policy` and `skill_router`. Their `harness.application.*`
identities own implementation; the initializer contains only a docstring.
Same-layer imports become relative. Existing cross-context dependencies and
published boundaries stay unchanged. The root migration baseline now contains
only ignored research, experiments, scenarios and evaluation infrastructure.

All fifteen root files remain Consumer API v0 facades under the existing closed
grammar. Publication, Questions and Skill Invariant Policy are import-only;
the other twelve preserve their existing CLIs. In particular `consumer_pack.py`
remains the wrapper's checkout and Pack entrypoint, and `skill_router.py` remains
the Pack CLI. There is no Consumer API bump, new bootstrap logic, include-prefix
expansion or installed-package requirement. Sixteen canonical Application files
are exported through `exact_files`.

`distribution.harnessw` deliberately remains the standalone stdlib-only bootstrap
transport, outside the materialized Pack. It imports no Harness implementation.
The preserved clean-target chain is standalone wrapper -> checkout root
`consumer_pack.py` facade -> canonical Consumer Pack implementation -> materialized
Pack -> root `skill_router.py` facade -> canonical Skill Router implementation.

Frozen public namespaces and whole-module AST hashes from
`1e67fdfadfde23148af72c73f2307ee7cbb7ab90` are checked in the isolated Pack.
Legacy and canonical `__all__` lists and every exported object share identity.
Reversing only relative Application imports, explicit exports and
`Path(__file__).resolve().parents[3]` root adaptations restores each baseline
AST. The five path-sensitive modules continue resolving repository/Pack-local
skills, registries, spec and docs; production bodies are otherwise unchanged.

Evidence reuses HA-A18 TD-DIST-001/002 (isolated Pack and clean-target wrapper),
HA-A16 routing validators, HA-A12/13 semantic admission/Questions/closure and
HA-A15 frontier/publication composition. Existing Scenario Suite evidence and
the full deterministic gate protect behavior. TL1 mutations from canonical
Application reject root `agent_router`, `skill_router` and `semantic_admission`
imports using the existing ownership ratchet; owned runtime alias imports are
zero. Validators/scenarios retain legacy imports as compatibility evidence.

The complete changed-file set is compared with every provider execution binding
under `spec/assurance/evidence/**`. Four records intersect at `skill_router.py`:
first-wave runs 36942421201 and 36947887869, TL4 existing-project run 36949909315
and TL5 known-project run 36952038645. All seven execution-bound records were
already stale on the base. Binding intersection: yes; new current -> stale
transition: no. Historical hashes, outcomes and currentness are preserved.
This mechanical migration requires deterministic evidence; no provider run or
new provider judgement claim is introduced.
