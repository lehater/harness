---
name: recovery-continuity-analysis
description: "Use when loss, corruption, storage/runtime failure, backup, restore, failover, failback or state reconstruction can materially affect accepted product state or availability."
---

# Recovery Continuity Analysis

## Trigger

Use for deployment/state scope where authoritative data or service continuity may require recovery beyond ordinary operation failure handling.

## Inputs

Accepted Product/Domain/Application/Data/System/Quality/Security/Change Transition/Operability knowledge as applicable.

## Read boundary

Accepted design is authority. Existing backup jobs, replicas, snapshots, scripts, cloud defaults and runbooks do not prove recovery requirements or correctness.

## Procedure

1. Inventory authoritative, derived, reconstructible, ephemeral and security-critical state.
2. Enumerate material loss, corruption, storage, runtime and site failure scenarios.
3. Identify business consequence of loss/unavailability.
4. Resolve recovery objectives through Product/Quality when required.
5. Define valid recovery point and cross-state consistency.
6. Define restore versus recomputation semantics.
7. Route protection/replication/failover topology to Data/System.
8. Route material restore sequencing/intermediate states to Change Transition.
9. Route reconciliation to Domain/Application.
10. Include key/secret/credential recovery through Security.
11. Include backup retention/disposition through lifecycle/obligation owners.
12. Classify COVERED, NOT_APPLICABLE, DEFERRED_NONBLOCKING or QUESTION.
13. Derive Verification/Test restore drills and invariant oracles.
14. Derive Operability evidence for backup age, recovery progress/failure and post-restore health.
15. Leave scripts/tool commands to implementation/operations.

## Stop conditions

Create a blocking Question if implementation would otherwise decide material:
- tolerated committed-state loss;
- restoration time;
- authoritative vs reconstructible state;
- cross-store recovery consistency;
- partial-restore behavior;
- failover/failback authority;
- reconciliation;
- secret/key recovery;
- retention/disposition;
- trust/evidence gate before reopening service.

## Implementation freedoms

After closure: backup technology/format, compression, scheduler, storage layout, script decomposition, restore command syntax, replica technology within accepted constraints and drill automation mechanics.

## Output contract

Produce the smallest project-native coverage artifact/review with:
- scope/state class;
- failure/loss scenario;
- business consequence;
- recovery objective;
- authoritative/reconstructible semantics;
- recovery consistency point;
- protection/reconstruction owner;
- transition/reconciliation constraints;
- Security/retention constraints;
- state/reopening condition;
- Questions;
- Verification/Test obligations;
- Operability obligations;
- implementation freedoms.

The analysis artifact is not automatically a Capability.

## Registration

Current evidence rejects generic DISASTER-RECOVERY-DESIGN, BACKUP-DESIGN, RESTORE-DESIGN and BUSINESS-CONTINUITY-DESIGN Authorities.
