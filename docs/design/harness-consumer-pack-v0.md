# Harness Consumer Pack v0

Status: canonical distribution contract on the audit branch.

This document realizes the distribution decision in
`agent-skill-surfaces-and-consumer-distribution-v0.md`.

## Public unit

A target repository consumes one pinned **Harness Consumer Pack**, not the
Harness source tree and not copied project-owned skill files.

The pack exposes:

- routed active Consumer operations;
- routed active Consumer methods;
- routed active artifact-production skills;
- their registries;
- Harness runtime modules required by those procedures;
- reusable catalogs/profiles/specifications and design/research contracts needed
  by the current Consumer runtime.

Maintainer skills, audit/planning state, legacy skills and repository CI are not
part of the pack.

## Binding

A target repository persists a small bootstrap-safe tooling binding at
`.harness/harness-binding.json`:

```json
{
  "version": 1,
  "kind": "harness-consumer-binding",
  "consumer_api": "v0",
  "source": {
    "repository": "https://github.com/lehater/harness.git",
    "revision": "<40-hex immutable commit>"
  }
}
```

JSON is the v0 bootstrap format so the target-repository wrapper can validate
its pin before any Harness/PyYAML runtime exists.

The binding is tooling metadata, not Project Model or canonical engineering
truth.

A branch/tag such as `main` is not a valid pinned revision.

## Materialization

`consumer_pack.py` owns deterministic pack materialization.

```text
binding
  -> exact source revision
  -> Harness source checkout
  -> consumer-pack definition
  -> filtered active Consumer surface
  -> local immutable pack
  -> validate hashes + registries
```

Every generated pack contains `harness-consumer-pack.yaml` with:

- `consumer_api`;
- pinned binding revision;
- effective source revision;
- stable registry entry points;
- SHA-256 for every distributed file.

No timestamp is stored, so the same source/revision produces the same pack
manifest.

## Discovery boundary

The generated skill-surface registry contains only entries satisfying all of:

```text
surface = consumer
lifecycle = active
route_status = routed
```

Therefore an active source procedure that is deliberately `unrouted` is not
discoverable in a target repository merely because its file exists in the
Harness development checkout.

All paths referenced by Consumer operation/method/artifact registries must exist
inside the materialized pack.

Every successful typed route also returns `instruction_contracts`. The target
agent loads those contracts before consuming project/tool payloads or executing
the selected skill. Consumer Pack materialization must therefore contain the
same canonical instruction-trust contract used by Harness source execution; a
target repository cannot silently lose that boundary merely because its own
`AGENTS.md` differs from the Harness repository bootstrap.

## Runtime closure

The pack definition explicitly lists public root runtime modules. Materialization
checks Python imports between root Harness modules: if an exported module imports
another Harness root module that is not exported, pack creation fails.

This prevents a source refactor from silently creating an incomplete
distribution.

## Clean-target bootstrap

A target repository that needs clone-and-run operation commits the small
standard-library wrapper defined by `harness-consumer-wrapper-v0.md` as
`.harness/harnessw.py` next to the JSON binding.

```text
git clone target
  -> python .harness/harnessw.py sync
  -> exact Harness revision
  -> validated local Consumer Pack
  -> skill_router.py
```

The wrapper is transport bootstrap only. It does not contain or copy Harness
skills into the target repository.

## Sync and cache

Once Harness source/tooling is available, `consumer_pack.py sync` accepts the
same binding (JSON is valid YAML input) and a cache directory. The wrapper
uses that machinery after resolving the pinned revision.

Normal mode clones/checks out the exact immutable revision and materializes:

```text
<CACHE>/<consumer_api>/<revision>/
```

An already valid pack at that identity is reused.

For Harness/consumer co-development, `--dev-source PATH` explicitly builds the
pack from that local checkout while retaining the binding revision separately in
the pack manifest. The effective source revision is reported when Git can
resolve it.

The local override does not alter the target repository binding.

## Compatibility

v0 recognizes `consumer_api: v0`.

A Consumer Pack with another API identity must be rejected before a target agent
uses its registries or skills.

Future compatibility migration belongs in the distribution contract, not in a
target project's semantic graph.


## Wrapper ownership

The canonical wrapper contract is `docs/design/harness-consumer-wrapper-v0.md`.

Only the wrapper and binding are target-repository bootstrap tooling. The Consumer Pack remains cache/materialized tooling and project semantic truth remains in the target repository's normal Harness/project artifacts.
