# Document and knowledge lifecycle

## Purpose

Define how target-project knowledge moves from discussion/evidence into durable accepted repository truth without turning project documentation into an archive dump.

## Roles

- **Living canonical artifact** — current accepted truth owned by the target project.
- **ADR** — consequential accepted choice plus rationale and supersession history.
- **Active execution artifact** — resumable current work, not product truth.
- **Baseline/provenance artifact** — intentionally retained historical snapshot when later comparison/audit/migration has demonstrated value.
- **Git history** — normal historical archive.

Knowledge is fixed enough for downstream reliance when its owner is identified, blocking unknowns/conflicts are resolved or explicitly non-blocking, the accepted statement is written in the smallest canonical project owner, consequential rationale is recorded when needed, and the change is versioned through the project's normal integration path.

When accepted truth changes, update the highest affected canonical owner first, revalidate only dependent artifacts, supersede changed ADR decisions explicitly, and avoid copying the same invariant into every downstream document.

Do not persist full chat transcripts, rejected brainstorming, duplicated canonical explanations, obsolete temporary analysis or completed plans solely for history.
