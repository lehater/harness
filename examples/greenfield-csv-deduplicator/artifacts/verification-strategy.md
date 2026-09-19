# Verification strategy — CSV Deduplicator

Status: accepted greenfield pilot verification design.

## Evidence levels

### Unit evidence

Test pure identity/retention behavior without filesystem or CLI concerns:

- full-row identity;
- one key and several keys;
- later duplicates removed;
- first occurrence retained;
- retained order preserved.

### Service integration evidence

Exercise CSV parsing, validation, transformation and safe publication using
temporary files:

- quoted delimiters and embedded newlines;
- no duplicates;
- malformed CSV;
- missing/duplicate/empty header names;
- missing selected key;
- existing destination with and without force;
- temporary-file cleanup after failure;
- published output appears only after success.

### CLI acceptance evidence

Invoke the supported console command as a subprocess and verify:

- argument syntax;
- exit status 0/1/2 semantics;
- stdout success summary;
- stderr error prefix;
- no success summary on failure;
- full-row and key-column end-to-end results.

## Traceability

Every Product Requirements acceptance expectation must be covered by at least one
service or CLI acceptance scenario.

Architecture-only implementation constraints such as temporary publish behavior
must have integration evidence even when not directly visible in final CSV
contents.

## Determinism

At least one acceptance case runs the same valid input/options twice and compares
the produced output bytes and summary counts.

## Network constraint

The implementation design contains no network component. Verification reviews
the implementation dependency surface and tests supported behavior without
network availability. A later network feature would require upstream design
re-entry.

## Excluded evidence

Performance benchmarks are diagnostic only because no numeric performance/scale
target is currently accepted.
