# Acceptance scenarios — CSV Deduplicator

Status: accepted greenfield pilot verification scenarios.

## S1 — full-row duplicate removal

Given a valid CSV with rows A, B, A and no `--key`,
when the command succeeds,
then the output contains A, B in original order,
`input_rows=3`, `retained_rows=2`, `removed_rows=1`,
and exit status is 0.

## S2 — selected-key duplicate removal

Given columns `id,name` and rows `1,Alice`, `2,Bob`, `1,Alicia`,
when invoked with `--key id`,
then the third row is removed even though the non-key value differs,
and the first `id=1` occurrence is retained.

## S3 — several key columns

Given repeated values in one key column but unique tuples over
`--key account --key date`,
then only rows with equal values across both selected columns are duplicates.

## S4 — no duplicates and deterministic rerun

Given valid input with no duplicate identity,
run the same input/options twice to two fresh outputs.
Both outputs must be byte-equivalent and summary counts equal.

## S5 — CSV quoting

Given quoted fields containing delimiters and embedded newlines,
then duplicate comparison uses parsed field values and output remains valid CSV.

## S6 — missing key column

Given `--key missing` where no such header exists,
then exit status is 2, stderr begins `error:`,
no success summary is emitted and no final output is published.

## S7 — invalid header

For each of:

- absent header;
- empty header name;
- duplicate header name;

the command returns exit status 2 and does not publish final output.

## S8 — malformed CSV / read failure

Malformed CSV and unreadable input return exit status 1,
emit an `error:` diagnostic and do not publish final output.

## S9 — existing destination protection

Given an existing output path and no `--force`,
then exit status is 2 and existing bytes remain unchanged.

With `--force`, a successful transformation replaces the destination only after
the temporary output is complete.

## S10 — source equals destination

If input and output resolve to the same file,
then exit status is 2 and the source remains unchanged.

## S11 — failure cleanup

Force a write/publish failure after temporary output creation.
No final successful output is published and temporary artifacts are cleaned up.

## S12 — supported operation is offline

Run the acceptance suite in an environment without external network access.
All supported successful scenarios remain executable.

## Traceability

S1–S4 prove duplicate identity, first-retained semantics, ordering and
determinism. S5 proves standards-capable CSV handling. S6–S11 prove accepted
failure and file-safety behavior. S12 proves the local/offline product boundary.
