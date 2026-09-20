---
name: source-coverage-audit
description: "Use for reconstruction/blind CREATE work that must prove every independently evidenced source statement has an explicit admitted/excluded/question disposition before downstream design can claim semantic closure."
---

# Source Coverage Audit

## Trigger

Use when actionable work has `knowledge_kind: source-coverage-audit`, or whenever a reconstruction/blind workflow sanitizes original requirements/evidence into a smaller Source Corpus whose losses could create false downstream closure.

## Inputs

- the selected original source baseline and provenance boundary;
- every independently evidenced source artifact in scope;
- the sanitized/admitted Source Corpus;
- accepted scope rules and source-vs-derived-design classification policy;
- any existing source classification registry.

## Read boundary

Read original source/provenance and the sanitized Source Corpus. Do not read prior derived target design merely to decide whether a source statement should survive. Existing old design may be used only after the blind/reconstruction freeze or when the experiment explicitly permits it.

## Procedure

1. Enumerate the source baseline at **statement-level semantic granularity**, not whole-file granularity.
2. Give every independently meaningful source statement a stable audit id and source_ref.
3. For each statement record exactly one disposition:
   - ADMITTED;
   - EXCLUDED_DERIVED_DESIGN;
   - EXCLUDED_OUT_OF_SCOPE;
   - EXCLUDED_DUPLICATE;
   - QUESTION.
4. For ADMITTED, record the exact sanitized statement and the canonical Source Corpus reference that preserves it.
5. When one sentence mixes observable requirement with prior design vocabulary, split/preserve the observable constraint rather than excluding the whole sentence.
6. For exclusions, record a concrete rationale. Never use generic "looks derived" wording when an observable constraint is being discarded.
7. For QUESTION, identify the Authority and unresolved classification/provenance question; coverage remains INCOMPLETE.
8. Run `python source_coverage.py validate <ledger.yaml>`.
9. Perform an independent reverse audit: start from every original source statement and verify its exact disposition without reading downstream design as justification.
10. Only a deterministic `coverage_status: COMPLETE` may provide the source-coverage capability.
11. Make that capability a prerequisite of Product Requirements or the final reconstruction consumer when source-loss assurance is material.
12. Reevaluate the Engineering Graph target.

## Stop conditions

Do not accept source coverage when:
- any source statement has no disposition;
- a statement is excluded only because it contains some design vocabulary while also carrying independent observable semantics;
- provenance cannot establish whether a candidate is source-level;
- an admitted sanitized statement weakens/removes scope, time, cardinality, negative constraints or acceptance conditions;
- classification requires consulting forbidden prior derived design;
- a QUESTION remains.

## Output contract

Produce a project-native or Harness-shaped YAML ledger accepted by `source_coverage.py`:

```yaml
version: 1
kind: harness-source-coverage
id: PROJECT-SOURCE-COVERAGE
source_baseline: repository@revision
coverage_status: COMPLETE
statements:
  - id: SRC-001
    source_ref: requirements.md#request-authority
    text: Actor requires effective request authority for relevant scope/time.
dispositions:
  - statement_id: SRC-001
    classification: ADMITTED
    admitted_ref: source-corpus.yaml#request-authority
    sanitized_statement: Request authority is evaluated for the relevant scope and time.
```

The ledger proves preservation/disposition only. It does not become product/domain truth.

## Acceptance checks

- every in-scope source statement has exactly one disposition;
- every ADMITTED item has a concrete sanitized statement and canonical admitted reference;
- exclusions have explicit reasons and do not erase independently observable semantics;
- duplicates point to another enumerated statement;
- QUESTION means INCOMPLETE;
- COMPLETE is deterministic under `source_coverage.py`;
- reverse audit finds no source statement absent from the ledger;
- downstream design is not used as evidence for what the original source meant.

## Registration

Register under the Authority chosen by the project for source/reconstruction assurance, normally DISCOVERY or PRODUCT-REQUIREMENTS, and provide a project-specific source-coverage capability. No new Core Authority/entity is required.

For blind/reconstruction assurance, make that capability an explicit prerequisite of downstream product/design closure or the terminal consumer.

## Human projection

Prefer a compact loss/disposition report grouped by source artifact and classification, highlighting exclusions and Questions.
