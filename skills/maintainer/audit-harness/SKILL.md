---
name: audit-harness
description: "Use when a Harness maintainer must systematically evaluate Harness behavior or architecture from reusable audit perspectives and produce evidence-backed findings for classification."
---

# Audit Harness

## Trigger

Use for a deliberate Harness audit, re-audit, architecture review against the
audit matrix, or a request to determine which perspectives remain uncovered.

This is a Maintainer operation. It is not exported to target repositories.

## Inputs

- audit goal/scope;
- current non-main repository state;
- `docs/audit/audit-framework.md`;
- relevant canonical design/spec contracts;
- current HARN/EVO ledgers;
- applicable validators/scenarios/tests.

## Required contracts

- `docs/design/agent-instruction-architecture-v0.md`
- `docs/design/operation-orchestration-v0.md`
- `docs/audit/audit-framework.md`
- `docs/audit/README.md`

## Procedure

1. Confirm repository/branch scope and never modify `main`.
2. Select the smallest perspectives that answer the request. For a broad health
   audit, prioritize UNASSESSED/PARTIAL perspectives and fired re-audit triggers.
3. Define the evidence boundary before drawing conclusions.
4. Inspect each selected perspective. Prefer deterministic reproduction when an
   oracle exists; use semantic analysis where it does not.
5. Search existing HARN/EVO by root cause/direction before emitting a finding.
6. Produce audit-local findings; do not allocate HARN/EVO identifiers directly.
7. Return findings to the coordinator. Registration/classification is a distinct
   responsibility and must be routed as `capture-harness-observation`.
8. After capture returns persisted dispositions, record the `AUD-*` run and
   update perspective coverage only for perspectives actually exercised.

## Output contract

Return audit scope, selected perspective IDs, findings and a pending audit-run
summary. Each finding contains local reference, summary, affected
invariant/surface, evidence, consequence, uncertainty/limitations and suggested
follow-up responsibility.

A finding is not itself a HARN/EVO record.

## Completion conditions

The audit is complete when every selected perspective has an evidence/result
statement, findings are deduplicated, persistent observations have passed
through `capture-harness-observation`, and the final AUD run is recorded.

## Stop conditions

Do not convert an architecture preference into a defect without evidence of a
violated invariant/current contract.

Do not repair findings during the audit unless the user explicitly changes the
task to implementation; corrections route separately through `change-harness`.
