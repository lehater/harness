# Harness Consumer API v1 bootstrap fragment

This repository uses the Harness Consumer Surface with `consumer_api: v1`.

Before Harness-controlled engineering work:

1. Run `python .harness/harnessw.py sync`.
2. Treat the printed directory as the active pinned Harness Consumer Pack.
3. From that directory invoke the typed procedure router through
   `python -m harness.application.skill_router ...`.
4. Load the returned `instruction_contracts` before consuming project/tool
   payloads, then read the returned `SKILL.md`.
5. Do not discover Harness procedures from remote GitHub links or a different
   local checkout. Development/dogfooding uses only explicit `--dev-source`.

The project binding is `.harness/harness-binding.json`: tooling metadata, not
project semantic truth. Stable public identities are operation ids, method ids,
knowledge kinds/skill ids and canonical `harness.*` runtime modules. Source paths
are not stable Consumer API identities. Programmatic Core access uses
`harness.project_model.core`; do not use `from harness import ...` as Core API.
