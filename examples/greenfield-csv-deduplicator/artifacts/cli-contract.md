# CLI contract — CSV Deduplicator

Status: accepted greenfield pilot interface contract.

## Command

```text
csv-deduplicate INPUT --output OUTPUT [--key COLUMN ...] [--force]
```

## Arguments

- `INPUT` — path to the UTF-8 CSV source file.
- `--output OUTPUT` — required destination path. The source path and output path
  must not resolve to the same file.
- `--key COLUMN` — repeatable. Each occurrence adds one header name to the
  duplicate identity key. With no `--key`, full-row equality is used.
- `--force` — permits replacement of an already existing output after the
  transformation succeeds.

At least one `--key` value is not required. Repeating the same key column is
invalid.

## Success output

On success, stdout contains exactly one summary line:

```text
input_rows=<N> retained_rows=<N> removed_rows=<N> output=<PATH>
```

The counts exclude the header row.

Exit status is `0`.

## Errors

Usage/contract errors return exit status `2`, including:

- missing required arguments;
- duplicate `--key` option values;
- source and output resolving to the same file;
- requested key column absent from the CSV header;
- existing output without `--force`;
- invalid/duplicate/empty header names.

Operational failures return exit status `1`, including:

- input cannot be opened/read;
- malformed CSV cannot be parsed;
- temporary output cannot be created/written/published.

Errors are written to stderr as one human-readable line beginning with
`error:`.

No successful summary is written on failure.

## Representation rules

Header names and row field values are compared exactly as parsed. The CLI does
not trim, lowercase or otherwise normalize values for duplicate identity.

Output preserves the input header order and retained row order.
