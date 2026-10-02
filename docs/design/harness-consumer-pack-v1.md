# Harness Consumer Pack v1

Status: canonical distribution contract.

## ADR-CONSUMER-API-V1 — retire facades at the distribution boundary

Status: accepted.

Consumer v0 distributes legacy module/file compatibility together with canonical
runtime implementations. Source facades must remain available while latest
Harness revisions can materialize v0. Removing them from source would break
that supported contract.

Consumer v1 instead distributes canonical module identities and minimal root
tooling. The explicit inventory is `spec/distribution/consumer-pack-v1.yaml`.
This is a versioned distribution decision, not a Core/domain or packaging-model
change. Source path is not a stable Consumer API identity.

Public v1 identities are:

- `consumer_api: v1`;
- operation ids, method ids, knowledge kinds and skill ids;
- canonical `harness.*` runtime module identities when programmatic access is
  required, including `harness.project_model.core` for Core.

Legacy names such as `engineering_graph`, `skill_router`, `semantic_acceptance`
and `adapters.canonical_graph` are not public v1 identities. Source filenames
still occur as physical artifact references returned by the typed router; they
are not a second API identity system. Consumer registries and skill identities
are unchanged.

## Inventory and import bridge

Only `scenario_drivers.py` and `scenario_suite.py` remain root Python files.
They are permanent Consumer test-orchestration tooling, not compatibility
facades, and their production dependencies use canonical runtime modules.

`harness/__init__.py` remains a technical non-installed import bridge. It allows
`python -m harness.application...` from a Pack root without installing Harness
or setting `PYTHONPATH=src`. Its existing Core re-exports remain intact for v0;
v1 procedures use `harness.project_model.core`, never `from harness import ...`
as public Core API. Retirement of the re-exports is a separate decision.

Canonical runtime files under `src/harness/**` are selected through explicit
`exact_files`, never a whole `src/` prefix. Catalogs, profiles, spec, design and
research contracts retain their required prefix selection. Only active routed
Consumer skills are distributed, with the filtered surface registry and existing
Consumer operation/method/artifact registries.

No `compatibility.module_facades` physical file or legacy `harness.py` CLI is
included. Top-level `adapters/` is excluded and forbidden, including the
provider/evaluation `copilot_behavioral_eval_agent.py`. Production nested
adapters remain canonical under Integration and Assurance packages.

## Binding, materialization and integrity

Binding schema stays version 1. JSON bootstrap binding uses
`kind: harness-consumer-binding`, `consumer_api: v1`, and `source` containing
`repository` and an immutable 40-hex `revision`.

`harness.application.consumer_pack` selects the definition from one API-to-path
mapping. Binding validation supports exactly v0 and v1; unsupported APIs fail
closed. `sync` gets the API from the binding, without fallback. Existing API and
CLI callers default to v0. Selection without a binding is explicit:

```bash
python -m harness.application.consumer_pack materialize SOURCE PACK --revision SHA --consumer-api v1
python -m harness.application.consumer_pack validate-definition --consumer-api v1
python -m harness.application.consumer_pack validate-pack PACK --consumer-api v1
```

The existing deterministic manifest, SHA-256, route/skill closure and forbidden
surface validation apply to both APIs. Tracked file tampering and arbitrary
untracked files fail. Only Python-generated `.pyc` within `__pycache__` is exempt
from the untracked-file check; manifested files always retain hash checks.
Cache identity remains `<cache>/<consumer_api>/<revision>`; dev-source retains
the binding revision separately from the effective revision.

## Wrapper protocol v1

`distribution/harnessw.py` supports both APIs and remains stdlib-only. Runtime
prerequisites and PyYAML bootstrap/cache behavior follow
`harness-consumer-wrapper-v0.md`.

For v0 it retains checkout/Pack `consumer_pack.py` invocation. For v1 every
source and existing-Pack execution uses
`python -m harness.application.consumer_pack` with the checkout/Pack root as
`cwd`. Materialization and Pack validation pass `--consumer-api v1`; dev-source
sync reads v1 from the binding. No root facade, Harness installation, environment
path bootstrap or shell invocation is needed.

Target agent instructions are `spec/distribution/target-agents-fragment-v1.md`:

1. Run `python .harness/harnessw.py sync`.
2. Use the printed pinned Consumer Pack directory.
3. From that directory invoke `python -m harness.application.skill_router ...`.
4. Load returned instruction contracts, then the selected skill.

This section is the versioned v1 extension of the existing wrapper contract;
it does not retrospectively change the v0 flow.

## Assurance and consequences

HA-A18 / TD-DIST-001 and TD-DIST-002 govern the affected failure modes. The
existing Pack validator preserves the v0 compatibility suite and adds an
isolated v1 canonical suite. It checks the complete physical facade set from
`repository-layout-v0.yaml`, canonical imports/CLIs, routing, Scenario Suite,
registry completeness, reproducibility and integrity mutations.

The wrapper validator exercises both clean-target matrices, exact pinned source
materialization, dev-source and cache reuse/rebuild. Its v1 source snapshot
removes root `consumer_pack.py` to falsify hidden facade dependence. Existing
Scenario Suite fixtures are executed through isolated v1 tooling to cover
cross-layer runtime closure; no new domain behavior or scenario DSL is added.

Both APIs remain supported by latest source. Source facades and the repository
compatibility registry remain unchanged. Future retirement of v0, source facades,
Core bridge re-exports or the non-installed packaging model requires a separate
compatibility decision.
