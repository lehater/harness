# NAPMS Coding Slice — Component Design Constraint

Status: research evidence.

## Goal

After model-level portability passed, test whether the same Component Design rules constrain a real existing NAPMS implementation without redesigning it.

Selected slice: Access Policy application-to-persistence dependencies.

## Baseline

NAPMS already had a broad application-owned `AccessRuleRepository` Protocol containing identity lookup, inventory query, detail lookup, scoped listing, add, save and commit operations. Several use cases depended on the entire Protocol even though they consumed only a subset.

The concrete PostgreSQL repository is already correctly infrastructure-owned and implements the broad capability.

## Coding change

Three consumer-shaped contracts were added:

- `AccessRuleLookup`: `get_by_id`;
- `AccessRulePageSource`: scoped paginated listing;
- `AccessRuleStateStore`: `get_by_id`, `save`, `commit`.

Then:

- authorized list use case depends on `AccessRulePageSource`;
- authorized detail use case depends on `AccessRuleLookup`;
- operational-state mutation depends on `AccessRuleStateStore`.

The existing `PostgresAccessRuleRepository` satisfies all contracts structurally. No wrapper classes, SQL changes, new transaction layer or runtime framework were introduced.

## Why this is meaningful

This slice was not invented for the experiment. It exposes an actual existing design pressure in NAPMS: a broad repository interface was shared by unrelated read/write consumers.

The Engineering Policy + Component Design guidance selects a minimal correction:

- ISP narrows consumer dependencies;
- DIP keeps contracts application-owned;
- CQS keeps read and mutation views distinguishable;
- YAGNI prevents one wrapper/adapter object per interface;
- KISS preserves the existing concrete repository.

No product/domain/security decision is made by the coding step.

## Result

The implementation shape is compatible with existing NAPMS architecture and requires no Harness-specific project logic.

The repository currently has no workflow trigger for this experiment branch, so GitHub Actions did not automatically provide a branch CI result. This is an integration/trigger limitation, not evidence of test success. The slice remains research-only until executed by an applicable CI path or locally.

## Research conclusion

Across Nutrition and NAPMS, the same rule has now selected useful, non-ceremonial boundaries in existing code:

> design the dependency contract from the consumer's responsibility; let one concrete provider satisfy multiple narrow contracts when appropriate.

This strengthens portability of the Component Design skill itself, not only the Engineering Graph model.
