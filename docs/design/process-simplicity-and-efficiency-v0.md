# Process Simplicity and Efficiency v0
## Normative rule

For equal guarantees use minimum sufficient process. CI is a verification boundary. Reuse unchanged state; aggregate independent blockers; automate mechanics, not authority.

## Current-state only; Git owns history

**Canonical project state is not an archive.** Git history is the historical record. Active canonical knowledge, documentation, registries and agent-facing context must contain only current, decision-relevant information. If an item is obsolete, invalid, superseded, duplicated or no longer needed, **remove it** from the active artifact instead of retaining it with `RETIRED`, `DEPRECATED`, `LEGACY`, `SUPERSEDED` or any equivalent tombstone/status/history list. Do not create old-version copies, long historical changelogs or migration residue merely "for traceability". A stable ID need not be reused; the previous object is recoverable from Git.

Apply the smallest safe mutation:
- Keep accepted decisions, genuine open Questions and required provenance to *current* sources; deleting stale content must not silently erase live product semantics.
- When an obsolete item is referenced by accepted downstream contracts, first identify and update/revalidate affected accepted consumers using their standard semantic admission and atomic publication. If that cannot be done, report the actual blocker; do not fake `CURRENT`.
- Preserve data only when a concrete external retention/audit obligation, an active reproducibility contract or an immutable published event genuinely requires it. Record that obligation explicitly; "might need later" is not a retention reason.
- Do not load or show historical run reports, retired entries or old variants to an agent unless they are specifically needed for the requested change or investigation.
- Delete unused files/sections entirely rather than relabeling them as obsolete. Avoid empty archival folders and reference lists.

This rule governs **what the active project contains**, not immutable Git commits, provenance of current facts or required safety/event audit records.
