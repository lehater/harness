# Harness consumer bootstrap fragment

This repository uses the Harness Consumer Surface.

Before Harness-controlled engineering work:

1. Run `python .harness/harnessw.py sync`.
2. Treat the printed directory as the active pinned Harness Consumer Pack.
3. Use that pack's `skill_router.py` as the Harness procedure entrypoint.
4. Do not discover Harness procedures from remote GitHub links or from a
   different local Harness checkout.
5. A local Harness checkout may be used only through the explicit wrapper
   `--dev-source` override for development/dogfooding.

The project binding is `.harness/harness-binding.json`. It is tooling metadata,
not project semantic truth.
