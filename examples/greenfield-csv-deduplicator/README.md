# Greenfield CSV Deduplicator pilot

Purpose: exercise Engineering Graph v0 as an agent-operated greenfield project
from an empty Core realization to an IMPLEMENTATION-complete target.

This project intentionally uses a smaller Authority set than NAPMS:

- DISCOVERY
- PRODUCT-REQUIREMENTS
- SYSTEM-ARCHITECTURE
- INTERFACE-DESIGN
- IMPLEMENTATION-DESIGN
- VERIFICATION-DESIGN

No DDD, persistence, security, quality or operability Authority is instantiated
because the selected product does not yet contain an independently owned decision
class requiring those boundaries.

The branch history is the experiment log. At each step the current target frontier
is evaluated first; the agent then creates only canonical knowledge permitted by
that frontier and registers the corresponding provider in `core-state.yaml`.
