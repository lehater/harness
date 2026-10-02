# Harness target-repository wrapper v0

Status: canonical bootstrap transport for Consumer APIs v0 and v1.

New integrations MUST use `consumer_api: v1` and
`spec/distribution/consumer-binding-example-v1.json`. V0 is deprecated but fully
functional; its wrapper branch remains required compatibility behavior.

## Problem

A pinned Consumer Pack cannot bootstrap itself in a clean target checkout:
`consumer_pack.py sync` is Harness code and therefore is not present before
Harness has been obtained.

The bootstrap mechanism must not solve this by copying Harness skills or by
making remote source-tree paths the target project's API.

## Decision

A target repository that wants clone-and-run Harness consumption commits two
small tooling files:

```text
.harness/
  harnessw.py
  harness-binding.json
```

This is analogous to a build-tool wrapper.

- `harnessw.py` is a transport/bootstrap loader, not a Skill.
- `harness-binding.json` pins the immutable Harness source revision and
  `consumer_api`.
- No Harness skill tree is copied into the target repository.
- The materialized Consumer Pack lives in a user/local cache, outside canonical
  project truth.
- Updating Harness normally changes only the pinned revision; wrapper changes
  are needed only when the bootstrap protocol itself changes.

## Clean-clone flow

```text
git clone target-project
        ↓
target AGENTS.md
        ↓
python .harness/harnessw.py sync
        ↓
read immutable binding JSON
        ↓
fetch exact Harness commit
        ↓
run that revision's Consumer Pack materializer
        ↓
validate pack hashes + API
        ↓
print local Consumer Pack path
        ↓
python -m harness.application.skill_router ... (from Pack directory)
```

The wrapper never follows a moving branch.

## Runtime prerequisites

The wrapper itself uses only the Python standard library plus the system
`git` executable.

Harness Consumer Pack tooling currently requires PyYAML. If the active Python
cannot import it, the wrapper creates a private cache-local bootstrap virtual
environment and installs exactly `PyYAML==6.0.3`. This environment is tooling
cache and is not committed to the target repository.

## Cache

Default cache:

- Windows: `%LOCALAPPDATA%/Harness/Cache` when available;
- other platforms: `~/.cache/harness`;
- `HARNESS_CACHE_DIR` overrides both.

A valid immutable pack at:

```text
<cache>/<consumer_api>/<revision>/
```

is reused after validation.

## Development override

```text
python .harness/harnessw.py sync --dev-source ../harness
```

uses the local Harness checkout only for the effective Consumer Pack while
preserving the project's pinned binding revision. It does not modify the
binding.

This is intended for Harness/consumer co-development and dogfooding.

## Ownership

The wrapper/binding are target-repository tooling integration, not:

- Core entities;
- project Authorities or Capabilities;
- canonical product/domain/architecture truth;
- Harness skills;
- a second routing system.

Once the Consumer Pack path is resolved, all Harness procedure discovery goes
through `python -m harness.application.skill_router ...` from the Pack directory.
V0 retains its root router compatibility path.
