# Deep audit — IMPLEMENTATION-DESIGN

Verdict: KEEP after boundary correction.

Decision: translate accepted design into bounded implementation slices plus repository/toolchain/environment/gate realization and completion criteria.

Accepted knowledge: implementation plan and repository realization contract.

Consumers: implementation agents and deterministic delivery/verification machinery. Repository-realization research independently validates this contract across different project shapes.

Necessity: Component/System/Policy/Security/Quality/Verification knowledge does not determine physical repository mapping, selected concrete tools, reproducible environment, gate wiring or implementation sequencing.

Encapsulation: Implementation Design consumes accepted upstream contracts and must not reopen their semantics.

Boundary correction: remove ownership of “migration concerns”. CHANGE-TRANSITION-DESIGN owns material transition validity: coexistence, ordering, irreversible points, recovery and retirement. IMPLEMENTATION-DESIGN only realizes an accepted transition contract and may own migration scripts/tool placement/execution wiring as implementation mechanics.

Toolchain/gate wiring remains part of repository realization; current evidence does not show an independent Authority lifecycle/consumer.

Final research decision: confirmed baseline Authority after wording/skill correction. Remove from further boundary work.
