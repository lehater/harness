# Product requirements — CSV Deduplicator

Status: accepted greenfield pilot requirements.

## Product intent

Provide a deterministic local command-line tool that removes duplicate data rows
from a CSV file without changing the relative order of retained rows.

The tool is intended for repeatable preprocessing of exported datasets before
analysis. It operates entirely on local files.

## Required behavior

1. Input CSV must contain a header row with unique, non-empty column names.
2. The user may supply one or more key columns.
3. If key columns are supplied, two data rows are duplicates when their values
   are equal for every selected key column.
4. If no key columns are supplied, duplicate identity is full-row equality across
   all input columns.
5. For each duplicate identity, retain the first occurrence in input order and
   remove later occurrences.
6. Preserve the input order of all retained rows.
7. Write a new CSV with the same column order and header names as the input.
8. Report the number of input data rows, retained rows and removed duplicate rows.
9. Processing must not send file contents to any network service.
10. Equivalent valid inputs and options must produce byte-equivalent CSV output
    apart from platform newline normalization explicitly fixed by implementation.

## Failure behavior

The operation fails without replacing an existing output when:

- the input cannot be opened;
- the CSV is malformed;
- the header is absent, contains an empty name or repeats a column name;
- a requested key column is absent;
- the output path already exists unless overwrite is explicitly requested;
- the output cannot be written.

A failed operation must return a non-zero process status and a human-readable
diagnostic on stderr.

## Acceptance expectations

- full-row mode removes later exactly repeated rows;
- key-column mode removes later rows with equal selected key values even when
  non-key values differ;
- the first occurrence is retained;
- retained row order and column order are preserved;
- no-duplicate input is reproduced semantically unchanged;
- missing key column is rejected;
- malformed CSV is rejected;
- an existing output is not overwritten without explicit permission;
- summary counts equal the observed transformation;
- the supported operation requires no network access.

## Out of scope

- fuzzy matching;
- normalization of whitespace/case/numeric formats before comparison;
- combining several input files;
- editing the source file in place;
- interactive UI;
- persistence/database integration.
