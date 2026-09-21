# Research — NAPMS autonomous Engineering Coverage pilot

Status: research only. No main/canonical Harness changes.

## Scope

Apply the unified Engineering Coverage evaluator to NAPMS using the native project integration shape:

canonical-design-graph + harness projection + engineering graph + selected Consumer -> derived Coverage.

Consumers tested: BACKEND-IMPLEMENTATION and FRONTEND-IMPLEMENTATION.

## Backend loop

Initial research Coverage: 57 activated, 50 remaining, completion_ready=false.

A conservative semantic-binding pass removed metadata-only gaps without treating artifact existence as proof.

Real missing decisions were then completed in current canonical owners: quality concern decisions; operability configuration/health/incident and explicit metrics/tracing/alerting applicability; security vulnerability-management and secure-development; reliability availability/durability/recovery; HTTP compatibility; data classification; backend release/rollback; verification architecture/human-interface/traceability/revalidation; implementation error handling; Resource-detail accessibility/responsiveness and explicit i18n non-applicability.

Final backend result: 57 activated, 0 remaining, completion_ready=true.

## Frontend discovery

The old Harness integration intentionally stopped at FRONTEND-IMPLEMENTATION READY -> engineering.frontend.human-interface.

Investigation found that current docs/ui files referenced by web/AGENTS.md do not exist; corresponding material exists only under docs-legacy/ui; docs-legacy is explicitly retired/frozen/non-canonical. Therefore legacy UI material cannot be used as current proof.

The current canonical frontend truth before this pilot consisted only of UI navigation, Resource-detail UI, and shared product/domain/HTTP/security/quality truth. The missing frontend design chain was therefore real rather than a projection-registration defect.

## Frontend design chain produced

The loop created current project-native artifacts for already-declared Engineering Graph capabilities:

1. engineering.frontend.human-interface
2. engineering.frontend.architecture
3. engineering.frontend.component-design
4. engineering.frontend.verification
5. engineering.frontend.test-design
6. engineering.frontend.implementation-design

They were registered in the canonical design graph, Harness projection and semantic claim bindings. No coverage-specific project capability family was introduced.

Shared Threat Model and Operability knowledge were added as explicit frontend-architecture prerequisites because activated frontend security/operability concerns otherwise had no proof inside the Consumer closure.

## Authority boundary finding

Initially SYSTEM-ARCHITECTURE owned both backend system architecture and the new frontend architecture.

The existing capability-scoped Authority-context validator rejected this because the frontend artifact introduced an independent prerequisite closure into execution context for engineering.architecture.rules.

The validator was not weakened. A dedicated FRONTEND-ARCHITECTURE-DESIGN Authority was introduced because frontend architecture is semantically coherent, changes independently behind shared contracts, and has a distinct public contract consumed by frontend component/verification design.

## Frontend result

After materializing the frontend chain and applying accepted operability N/A decisions: 60 activated, 0 remaining, completion_ready=true.

The increase from 57 to 60 activated concerns is expected: richer topology exposes additional relevant concerns rather than merely reducing a checklist.

## Integration result

At the completed frontend research head, Research Engineering Coverage, Unified Harness Integration and design validation all pass.

## Main findings

1. Coverage can discover an actually missing design layer rather than only missing metadata.
2. Frozen legacy documentation must not be used to manufacture current proof.
3. Completing one capability can legitimately activate additional concerns because selected topology becomes richer.
4. Capability-scoped Authority context is an effective test of whether an Authority boundary is too broad.
5. The correct repair for an over-broad Authority is boundary decomposition, not validator weakening.
6. Coverage remains a derived control loop over canonical engineering knowledge; it is not a second project ontology.