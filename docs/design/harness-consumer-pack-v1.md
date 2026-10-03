# Harness Consumer Pack v1

Status: canonical distribution contract.

## Public identity

Consumer API v1 is the only supported Consumer Pack identity. Public runtime
entrypoints are canonical `harness.*` modules; source filenames are not a
parallel API.

Canonical binding:

```json
{
  "version": 1,
  "kind": "harness-consumer-binding",
  "consumer_api": "v1",
  "source": {
    "repository": "<repository>",
    "revision": "<40-hex immutable commit>"
  }
}
```

## Contents

The inventory is `spec/distribution/consumer-pack-v1.yaml`.

The Pack contains:

- canonical runtime modules under `src/harness/**`;
- the source-tree `harness/__init__.py` package bridge;
- consumer skills and routing registries;
- required catalogs, profiles, specs and design/research contracts;
- canonical Scenario Suite/Drivers under `harness.application`.

It excludes root Python facades, top-level `adapters/`, Maintainer skills,
audit/history material and test code.

## Commands

```sh
python -m harness.application.consumer_pack validate-definition --consumer-api v1
python -m harness.application.consumer_pack materialize SOURCE PACK --revision SHA --consumer-api v1
python -m harness.application.consumer_pack validate-pack PACK --consumer-api v1
python -m harness.application.skill_router operation --surface consumer --operation project-bootstrap-reconcile
python -m harness.application.scenario_suite SCENARIOS --catalog CATALOG
```

The CLI defaults to v1; retired API identities are rejected.

## Compatibility

Consumer API v1 published identities are append-only across Harness revisions.
The compatibility baseline is `spec/distribution/consumer-api-v1-baseline.yaml`.
Existing public runtime modules, public operations, methods, and artifact
knowledge-kind identities must remain available under v1. Additive identities
are compatible. A rename or removal is a breaking change and must be handled by
introducing a new `consumer_api` while preserving v1 for existing bindings.

The full gate compares the current Consumer surface with the frozen baseline so
an ordinary Harness upgrade cannot silently break a pinned Consumer contract.

## Integrity

Materialization records a manifest containing the immutable binding revision,
effective revision, selected files and SHA-256 hashes. Validation rejects missing,
modified or untracked files and forbidden prefixes.

## Bootstrap

`distribution/harnessw.py` is the standalone stdlib-only bootstrap transport.
It reads a v1 binding, fetches/materializes the pinned revision and validates the
resulting Pack without requiring a globally installed Harness package.

See `docs/design/harness-consumer-wrapper-v1.md`.
