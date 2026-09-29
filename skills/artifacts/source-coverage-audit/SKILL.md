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

1. Bind the selected immutable source boundary before semantic enumeration. For free-form text, use a lossless line-range partition validated by `source_boundary.py`; a deterministically complete native item inventory may serve the same role for structured sources.
2. Reject uncovered/overlapping source ranges or a source fingerprint mismatch. Boundary coverage proves only that raw source text was not skipped.
3. Enumerate each covered source unit at **statement-level semantic granularity**, not whole-file granularity.
4. Give every independently meaningful source statement a stable audit id and source_ref.
5. For each statement record exactly one disposition:
   - ADMITTED;
   - EXCLUDED_DERIVED_DESIGN;
   - EXCLUDED_OUT_OF_SCOPE;
   - EXCLUDED_DUPLICATE;
   - QUESTION.
6. For ADMITTED, record the exact sanitized statement and the canonical Source Corpus reference that preserves it.
7. When one sentence mixes observable requirement with prior design vocabulary, split/preserve the observable constraint rather than excluding the whole sentence.
8. For exclusions, record a concrete rationale. Never use generic "looks derived" wording when an observable constraint is being discarded.
9. For QUESTION, identify the Authority and unresolved classification/provenance question; coverage remains INCOMPLETE.
10. Run `python source_coverage.py validate <ledger.yaml>`.
11. Perform an independent reverse audit: start from every covered original source unit and verify that all independently meaningful statements entered the ledger before checking their dispositions. Do not read downstream design as justification.
12. Treat `coverage_status: COMPLETE` only as proof of statement disposition coverage. It does not prove raw-source enumeration completeness unless the lossless source boundary also passed, and it does not prove that an ADMITTED `sanitized_statement` preserves every material clause.
13. When the admitted Source Corpus will become a machine-addressable semantic surface, review each admitted canonical statement against its extracted semantic atoms before those atoms are accepted as the downstream derivation baseline. Keep the task statement-local: one source statement -> its candidate atom list.
14. Once an expert-reviewed source atom baseline exists, use deterministic semantic acceptance/derivation checks to reject missing atoms or weakened machine-addressable values; do not ask downstream LLM review to rediscover atoms that should have been admitted upstream.
15. Only a passing source boundary, deterministic `coverage_status: COMPLETE`, and any required semantic-surface admission may provide the source-coverage/semantic baseline used by the selected experiment.
16. Make that capability a prerequisite of Product Requirements or the final reconstruction consumer when source-loss assurance is material.
17. Reevaluate the Engineering Graph target.

## Stop conditions

Do not accept source coverage when:
- the selected raw source has an uncovered/overlapping boundary range or fingerprint mismatch;
- any covered source unit has not been reviewed for statement enumeration when semantic meaning is present;
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

- the immutable selected source has complete lossless boundary coverage;
- every covered semantic source unit was enumerated into independently meaningful statements or explicitly determined to contain no source semantics;
- every in-scope source statement has exactly one disposition;
- every ADMITTED item has a concrete sanitized statement and canonical admitted reference;
- exclusions have explicit reasons and do not erase independently observable semantics;
- duplicates point to another enumerated statement;
- QUESTION means INCOMPLETE;
- COMPLETE is deterministic under `source_coverage.py` and is interpreted only as statement disposition completeness;
- reverse audit finds no source statement absent from the ledger;
- every ADMITTED rewrite used as a semantic baseline has a separate completeness/fidelity review when material meaning was decomposed or rewritten;
- downstream design is not used as evidence for what the original source meant.

## Registration

Register under the Authority chosen by the project for source/reconstruction assurance, normally DISCOVERY or PRODUCT-REQUIREMENTS, and provide a project-specific source-coverage capability. No new Core Authority/entity is required.

For blind/reconstruction assurance, make that capability an explicit prerequisite of downstream product/design closure or the terminal consumer.

## Human projection

Prefer a compact loss/disposition report grouped by source artifact and classification, highlighting exclusions and Questions.
