# Authority split migration plan v1

Status: research candidate. This is the final boundary-migration plan before canonicalization.

## 1. STRATEGIC-DOMAIN-DESIGN

Replace with:
- DOMAIN-STRATEGY — conditional; owns subdomain landscape, strategic classification, domain vision/investment constraints.
- MODEL-CONTEXT-STRATEGY — conditional; owns model/language applicability, context relationships and translation contracts.

Migration:
- split current strategic-domain skill into two skills/knowledge kinds;
- rebind capabilities by semantics, never by filename;
- existing project artifacts that mix both families require MANUAL-DECISION/reassessment, not automatic duplication;
- downstream requires edges are rebuilt from actual capability consumption.

## 2. SYSTEM-ARCHITECTURE

Keep SYSTEM-ARCHITECTURE but narrow it to system/runtime decomposition, runtime boundaries, dependency topology and technical interaction structure.

Add:
- CONCURRENCY-CONSISTENCY-DESIGN — conditional; owns ordering, isolation, atomicity, conflict, retry/idempotency and consistency semantics for interacting executions.

Migration:
- do not move generic architectural dependency rules;
- move only accepted knowledge whose correctness contract depends on concurrent interaction/order/isolation/atomicity;
- old System Architecture artifacts mixing topology and consistency require semantic reassessment;
- Data/Component/Verification/Implementation consume the new contract only when applicable.

## 3. INTERFACE-DESIGN

Replace with:
- MACHINE-INTERFACE-DESIGN — conditional; owns external machine interaction/representation contracts.
- HUMAN-INTERFACE-DESIGN — conditional; owns human interaction semantics, information/navigation structure, presentation-system and screen/view composition.

Migration:
- `interface-contract` routes to MACHINE-INTERFACE-DESIGN;
- `human-interface-design`, `presentation-system-design`, `screen-view-design` route to HUMAN-INTERFACE-DESIGN;
- a human interface may consume a machine interface in a project, but that edge is not universal;
- mixed legacy INTERFACE-DESIGN artifacts require semantic reassessment.

## Compatibility / bootstrap rule

Catalog Authority IDs are project-state identities. Removing/splitting IDs is therefore a migration event.

Bootstrap/reconcile must:
1. preserve unaffected Authority assessments;
2. never copy old applicability to every replacement Authority;
3. map an old assessment automatically only when existing accepted capability evidence proves exactly one replacement family;
4. otherwise create replacement Authorities as UNASSESSED and surface the old record as migration conflict/manual decision;
5. rebuild Project Engineering Status from the new catalog;
6. remain idempotent after migration.

## Canonicalization gate

Before merge:
- catalog contains atomic replacement Authorities;
- skills/knowledge-kind routing agrees with new ownership;
- semantic acceptance and role bindings use new IDs;
- examples/fixtures are migrated;
- bootstrap/reconcile has split-ID migration tests;
- all repository validators pass;
- no old Authority ID remains in canonical/runtime configuration except explicit migration compatibility fixtures/docs.


## Consistency review note

Post-migration semantic review found and corrected three drift classes before tests:
- catalog serialization accidentally contained literal escaped newlines around CONCURRENCY-CONSISTENCY-DESIGN;
- SYSTEM-ARCHITECTURE skill still claimed consistency/transaction ownership after the split;
- interface-contract and human-interface skills still used the former combined Interface Design ownership language.

These are migration defects, not new boundary decisions.
