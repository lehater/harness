# Implementation plan — CSV Deduplicator

Status: accepted greenfield pilot implementation design.

## Realization choice

Implement the MVP as a Python 3.12+ command-line package using the standard
library for argument parsing, CSV parsing/writing, filesystem operations and
temporary files.

No external runtime dependency is required by the accepted design.

## Implementation slices

### 1. Pure duplicate-identity and retention logic

Implement a pure transformation decision layer that:

- receives the ordered header and selected key-column indexes;
- derives row identity from selected columns or the full row;
- tracks seen identities;
- returns retain/remove decisions while preserving traversal order.

This slice performs no filesystem or CLI work.

### 2. CSV validation and transformation service

Implement:

- UTF-8 file opening;
- CSV header validation;
- requested key resolution;
- streaming parse;
- retained-row writing;
- row-count summary.

Malformed input and contract validation produce typed internal failures rather
than printing directly.

### 3. Safe output publishing

Write transformed output to a temporary file in the destination filesystem.

Only after the full transformation succeeds:

- reject existing destination unless force is accepted;
- publish/replace according to the CLI contract;
- ensure failed operations do not expose partial successful output.

### 4. CLI adapter

Implement the accepted command syntax, map internal failures to exit status
`1` or `2`, write diagnostics to stderr and successful summary to stdout.

### 5. Verification implementation

Implement tests from the Verification Design artifact once accepted.

## Intended package boundaries

```text
csv_deduplicator/
  cli.py
  service.py
  deduplication.py
  errors.py
```

The exact function/class decomposition inside these modules is implementation
detail as long as the accepted architecture responsibilities remain separated.

## Migration/deployment

There is no persistent state or schema migration.

Installation must expose the `csv-deduplicate` console command.

## Risks to verify during implementation

- CSV newline/quoting behavior across platforms;
- safe replacement behavior when `--force` is used;
- cleanup of temporary files after any failure;
- distinguishing usage/contract failures from operational I/O failures.
