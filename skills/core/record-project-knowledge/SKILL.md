---
name: record-project-knowledge
description: "Use when a discussion produced durable requirements, domain knowledge, architecture decisions, unresolved material questions or execution knowledge that must be fixed in the target repository rather than left in conversation history."
---

# Record Project Knowledge

Use the Harness document/knowledge lifecycle.

1. Harvest only consequential content from discussion/evidence.
2. Split mixed statements by semantic owner: requirement, domain, architecture, ADR rationale, execution state.
3. Preserve source evidence separately from interpretation when later reinterpretation may matter.
4. Mark non-accepted content explicitly as proposal/hypothesis/unknown/conflict.
5. Update the highest target-project canonical owner first; link downward instead of duplicating paragraphs.
6. Use an ADR only when rationale/trade-off/supersession needs durable history.
7. Use baselines only for explicit milestone/provenance value; Git history is the normal archive.
8. Update active execution state only for resumable current work.
9. Remove temporary notes once durable outcomes are absorbed.

Do not persist chat transcripts as project documentation.
