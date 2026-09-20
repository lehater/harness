# Disaster recovery / backup / restore / continuity ownership research

Status: research conclusion.

## Research question

Does disaster recovery form an atomic engineering Authority, or is recovery knowledge already owned by Quality, Product/Domain, Data, System Architecture, Operability, Change Transition and Verification?

Separate:
- **recovery objective** — tolerated data loss and service restoration expectations;
- **recoverable state semantics** — which state must survive and what reconstructed state means;
- **protection mechanism** — backup, replica, snapshot, log shipping, export;
- **restore/reconstruction procedure** — how state/runtime is rebuilt;
- **continuity/failover** — how service continues or returns;
- **validation/evidence** — proof that recovery meets accepted objectives.

## Decision ownership map

| Decision | Owner |
| --- | --- |
| Business impact/tolerable loss of authoritative state | Product/Domain |
| RPO/RTO/availability/recovery target | Quality Design derived from product truth |
| Which state is authoritative vs reconstructible | Domain/Application/Data |
| Cross-store recovery consistency requirement | Domain/Application/System/Data |
| Backup/replication topology | System Architecture/Data Design |
| Failover topology | System Architecture |
| Restore ordering/dependency constraints | System + Change Transition when path states are material |
| Reconciliation after partial recovery | Domain/Application |
| Credential/key/secret recovery protection | Security Architecture |
| Backup retention/disposition | Product/Domain/Obligation Analysis/Data |
| Recovery diagnostics/progress evidence | Operability |
| Restore drill and invariant proof | Verification/Test |
| Exact commands/scripts/tooling | Implementation/operations after design closure |

## Key distinctions

### Backup is not recovery

A backup artifact is useful only if an accepted state can be restored from it within the required semantics/objectives. "Backup succeeded" does not prove restore correctness.

### Durability is not disaster recovery

A durable commit protects against some interruption modes. It does not establish recovery from loss/corruption of the storage/runtime/environment.

### RPO/RTO do not define state semantics

Numeric targets constrain architecture, but Domain/Application/Data must still define which state is authoritative, reconstructible or allowed to lag.

### Restore is a transition

When recovery passes through material intermediate states, ordering, irreversible points or coexistence constraints, CHANGE-TRANSITION-DESIGN owns transition validity. Recovery does not need to duplicate that boundary.

## Atomicity test — candidate RECOVERY-DESIGN

### Semantic cohesion — FAIL

The candidate combines product loss tolerance, quality targets, domain state semantics, data protection, runtime topology, security, transition sequencing and evidence. "Recovery" is the scenario joining them, not one kind of engineering decision.

### Independent change — FAIL

Backup mechanism may change behind stable RPO/RTO and state semantics. RPO can change without changing domain state. Restore procedure can change without changing backup representation. Failover topology can change independently of reconciliation policy.

### Public producer/consumer contract — FAIL as one owner

Consumers need specific capabilities from existing owners: recovery target, authoritative-state contract, protection topology, transition path, diagnostics and proof. A generic Recovery Design would aggregate them.

## Verdict

**Do not create DISASTER-RECOVERY-DESIGN, BACKUP-DESIGN, RESTORE-DESIGN or BUSINESS-CONTINUITY-DESIGN Authorities from current evidence.**

Recovery is a cross-Authority closure analysis.

## Pre-code blocking Questions

Route a Question when implementation/operations would otherwise decide:
- which committed state may be lost;
- acceptable data-loss window;
- acceptable restoration time;
- whether derived state is restored or recomputed;
- whether provenance/history must survive;
- consistency point across related stores;
- restore ordering;
- behavior while only part of state/runtime is restored;
- failover/failback authority;
- reconciliation after partial recovery;
- treatment of secrets/keys/credentials;
- backup retention/disposition;
- evidence required before restored service is trusted.

## Validation — Nutrition Management

Accepted Nutrition design uses one local file-backed SQLite database with WAL and synchronous FULL. This establishes durable-commit behavior for the implementation slice, but it does not establish backup/restore objectives.

The architecture also explicitly keeps Planning Input Snapshot and plan history ephemeral. Those are not authoritative state requiring backup.

Therefore a generic backup mechanism must not silently turn ephemeral planning artifacts into durable recovery state.

For the current local MVP, no accepted product/quality evidence establishes RPO/RTO or disaster-continuity requirements. Recovery analysis can classify DR as NOT_APPLICABLE/QUESTION depending selected deployment scope; it must not invent cloud replication or backup scheduling.

If recovery becomes required:
- Product/Domain identify state whose loss matters;
- Quality establishes targets;
- Data/System establish protection/reconstruction;
- Verification proves restore;
- Operability exposes failure/recovery evidence.

No residual Recovery Authority remains.

## Validation — NAPMS

NAPMS accepted Quality Design explicitly states numeric latency, throughput, availability and scale targets are absent rather than invented. The same evidence does not establish RPO/RTO.

Persistence contains authoritative history whose semantics matter: published revisions are append-only; policy decision history is retained; active/retired states and provenance have meaning. A restore that simply starts PostgreSQL successfully is insufficient if those invariants are violated.

Observability currently distinguishes backend startup from PostgreSQL connectivity failure but does not claim disaster-recovery coverage.

Legacy material historically contained local backup/recovery procedure, but current accepted design does not elevate that operational mechanism into a current recovery requirement.

Therefore current NAPMS cannot infer production backup/failover/restore guarantees. If such scope is introduced, existing Authorities can own all required decisions.

## Synthetic multi-store case

Assume:
- transactional primary DB;
- object store;
- async search index;
- secrets/keys;
- backups at different points;
- regional outage.

Experiments:
1. DB restored to T1 and object store to T2: Domain/Application must define whether mixed point is valid; System/Data implement coordinated recovery.
2. Search index lost: if reconstructible, Application/Data define source of truth and rebuild semantics; no need to restore it as authoritative state.
3. Key material lost: backup may be useless; Security owns key recovery/protection.
4. Region fails: Quality/Product define acceptable outage/loss; System owns failover topology.
5. Failback after writes in secondary: concurrency/reconciliation semantics belong to Domain/Application/System, not a recovery owner.
6. Restore runs through partially available state: Change Transition owns path validity if intermediate states are material.
7. Backup retained too long: retention is governed by lifecycle/obligation closure, not DR convenience.

No atomic residual remains.

## Recovery closure algorithm

For selected deployment/state scope:

1. inventory authoritative, derived, reconstructible, ephemeral and security-critical state;
2. enumerate loss/corruption/site/runtime failure scenarios;
3. identify business consequence of state loss/unavailability;
4. establish accepted recovery objectives where required;
5. define valid recovery point/state and cross-state consistency;
6. define reconstruct vs restore semantics;
7. define protection/failover topology;
8. define transition ordering, partial-state behavior and reconciliation;
9. include secret/key/credential recovery;
10. include retention/disposition constraints;
11. classify COVERED, NOT_APPLICABLE, DEFERRED_NONBLOCKING or QUESTION;
12. derive Verification/Test restore drills and invariant checks;
13. derive Operability recovery evidence;
14. leave exact commands/scripts/tool selection to implementation/operations.

## Implementation freedoms

After closure:
- backup product/format;
- compression;
- exact script decomposition;
- scheduler;
- storage bucket/layout;
- restore command syntax;
- replica technology satisfying accepted topology/objectives;
- drill automation details.

## Priority findings

### P0
- Backup success must never be treated as proof of recoverability.
- Durability does not imply disaster recovery.
- RPO/RTO must not be invented without Product/Quality basis.
- Restore must preserve accepted domain/data invariants, not merely storage readability.

### P1
- Generic Recovery/Backup/Restore Authorities fail atomicity.
- Recovery closure should be reusable.
- CHANGE-TRANSITION-DESIGN covers material restore-path states when applicable.
- No Core change is justified.

## Canonicalization recommendation

Add a recovery-continuity analysis skill and catalog principles. Do not add a new Authority.
