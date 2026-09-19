# System architecture — CSV Deduplicator

Status: accepted greenfield pilot architecture.

## Runtime shape

The product is one local command-line process. It has no server component,
database, background worker or network dependency.

The process executes one bounded transformation:

```text
open input
→ validate CSV header
→ stream rows
→ derive duplicate identity
→ retain first occurrence
→ write retained rows to temporary output
→ publish output only after successful completion
→ emit summary
```

## Structural responsibilities

- **CSV reader** — parses the header and data rows and exposes ordered column values.
- **identity projector** — derives the duplicate identity from either configured
  key columns or all columns.
- **deduplication engine** — keeps a set of identities already observed and
  decides retain/remove while preserving traversal order.
- **CSV writer** — writes the original header order and retained rows.
- **result publisher** — prevents accidental replacement and only publishes a
  completed output.
- **reporter** — emits deterministic transformation counts and diagnostics.

These are implementation responsibilities, not independent services.

## Data and memory

Input rows are processed sequentially. The implementation may retain duplicate
identities in memory but does not need to retain all full input rows.

The accepted MVP places no explicit maximum file size or memory target beyond
successful processing on the execution environment. If measurable scale targets
become product requirements, they must be routed back to Product Requirements /
Quality Design rather than invented here.

## File safety

The final output path must not expose a partially written successful result.

A conforming implementation writes to a temporary file in the destination
filesystem and publishes it only after parsing/transformation succeeds.

Existing output is protected according to Product Requirements.

## Encoding and CSV representation

The architecture does not redefine CSV semantics. A standards-capable CSV parser
and writer must be used so quoting, delimiters inside quoted fields and embedded
newlines are handled by the CSV layer rather than ad-hoc string splitting.

The project fixes UTF-8 as the supported MVP text encoding.

## Network/security

The process performs no network I/O as part of its supported operation.

## Excluded architecture

No web service, persistence database, message bus, plugin system or distributed
component is justified by current requirements.
