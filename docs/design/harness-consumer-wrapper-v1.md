# Harness target-repository wrapper v1

Status: canonical bootstrap transport.

`distribution/harnessw.py` is intentionally standard-library-only so a clean
target checkout can materialize the pinned Harness Consumer Pack before Harness
runtime code is available locally.

A target keeps:

- `.harness/harnessw.py`;
- `.harness/harness-binding.json` using `consumer_api: v1`.

The wrapper validates the binding, resolves an immutable 40-hex revision,
bootstraps PyYAML when required, materializes the Pack through
`python -m harness.application.consumer_pack`, validates it and prints the
local Pack path.

Cache identity is:

```text
<cache>/v1/<revision>/
```

`--dev-source` is an explicit local-development override; it changes only the
effective source used to materialize the Pack and does not create a legacy API
surface.

Bindings using retired Consumer API identities fail closed.
