"""Legacy Consumer API v0 compatibility facade."""
from harness.integration.adapters.canonical_graph import *
from harness.integration.adapters.canonical_graph import __all__
from harness.integration.adapters.canonical_graph import main
if __name__ == "__main__":
    raise SystemExit(main())
