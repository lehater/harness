# Deep audit — INTERFACE-DESIGN

Verdict: SPLIT machine-interface ownership from human-interface/presentation ownership.

Repository evidence already models distinct knowledge kinds: interface-contract, human-interface-design, presentation-system-design and screen-view-design.

## MACHINE-INTERFACE candidate
Decision: supported external machine interaction/representation contract.
Accepted knowledge: protocol/API/message representation contract.
Consumers: external integrations, System/Component/Implementation/Verification and human UI only when it consumes that machine interface.

## HUMAN-INTERFACE candidate
Decision: human interaction semantics, information/navigation structure and presentation/view composition.
Accepted knowledge: human-interface, presentation-system and screen/view contracts.
Consumers: System/Component/Implementation/Test for user-facing realization.

Independent applicability is explicit: API/service with no human UI; local human application with no independently public machine contract. The example graph currently makes human-interface depend on machine-interface, but that is project-specific topology, not a universal boundary.

Final research decision: one INTERFACE-DESIGN applicability bit is unsafe. Split at least machine vs human interface. Presentation-system/screen-view remain capabilities under human interface until independent ownership is proven.
