# Completion criteria — CSV Deduplicator

Status: accepted greenfield pilot implementation criteria.

Implementation is complete only when all of the following are true:

- the package exposes the supported `csv-deduplicate` command;
- full-row and selected-key duplicate semantics match Product Requirements;
- the first occurrence is retained and retained row order is preserved;
- output uses the accepted header order and UTF-8 representation;
- failed transformations never publish a partial successful output;
- existing output is protected unless `--force` is supplied;
- source and destination cannot be the same file;
- the CLI maps accepted contract errors to exit status `2`;
- operational failures map to exit status `1`;
- success emits the accepted summary and exit status `0`;
- the supported operation performs no network I/O;
- temporary output is removed after failure;
- the accepted Verification Design evidence passes in CI;
- implementation documentation contains no behavior contradicting canonical
  Product Requirements, Architecture or CLI Contract.

Completion does not require features listed as out of scope.
