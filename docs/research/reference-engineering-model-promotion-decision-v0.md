# Reference Engineering Model promotion decision v0

Status: closed decision.

## Decision

Do **not** promote Reference Engineering Model v0 to canonical Harness status yet.

Keep it as an optional, deterministic, fail-closed research layer that materializes the existing Engineering Graph without changing Harness Core.

## Evidence

### R1 — independent external hold-outs

Result: PASS.

A second frozen external batch covered:

- Chrome browser extension;
- Stripe webhook consumer;
- Airflow DAG pipeline;
- Prometheus exporter.

Reference Engineering Model v0 was not changed to fit the batch. After one oracle correction in the Prometheus fixture, all hold-outs materialized successfully and generated graphs remained valid.

Evidence:

- `docs/research/reference-engineering-model-external-holdouts-v1.md`
- `spec/research/reference-materializer-fixtures/holdouts-v1.yaml`

### R2 — evolution and migration

Result: PASS with promotion blocker.

The experiment established deterministic snapshot fingerprints, explicit rename/split/merge/predicate migration mapping, rematerialization on model change, and obsolete CapabilityId detection.

The current materialization result does not carry the Reference Model fingerprint. Therefore persisted evidence cannot independently identify the exact model snapshot that produced it.

Evidence:

- `docs/research/reference-engineering-model-evolution-v0.md`
- `spec/research/reference-model-evolution-contract-v0.yaml`

### R3 — Safety and AI specialization semantics

Result: research obligations identified; canonicalization remains blocked.

Safety and AI both have independently meaningful proof obligations, but they span multiple Authority boundaries and do not yet have stable canonical semantic claim names or ownership.

Reference Model v0 must continue to return `REFERENCE_MODEL_GAP` for these specializations.

Evidence:

- `docs/research/specialization-proof-semantics-v0.md`
- `spec/research/specialization-proof-semantics-v0.yaml`

## Remaining promotion blockers

1. Materialization evidence must bind the exact Reference Model snapshot/fingerprint.
2. Historical evidence must also bind accepted project-truth snapshot, request identity, and materializer semantics/version.
3. Safety proof obligations need canonical Authority ownership and semantic claim vocabulary.
4. AI proof obligations need canonical Authority ownership and semantic claim vocabulary.
5. Positive and omission-sensitive executable fixtures are required before either specialization can leave `REFERENCE_MODEL_GAP`.

## Architecture preserved

```text
optional Reference Engineering Model
        ↓
deterministic materializer
        ↓
canonical existing Engineering Graph
        ↓
unchanged Harness Core
```

No Core extension is justified by the completed promotion-evidence cycle.

## Reopen condition

Reopen canonical-promotion evaluation only after the provenance blocker is closed and the specialization semantics have an explicit canonical disposition.
