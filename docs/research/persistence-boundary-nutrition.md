# Persistence Boundary Experiment — Nutrition

Status: research evidence.

## Goal

Test Engineering Policy + Component Design on a less obvious boundary than the solver: application-to-persistence collaboration inside Nutrition Targeting.

The pressure here is primarily DIP + ISP + CQS. A common unconstrained implementation response is one broad repository interface, a generic repository hierarchy, or direct reliance on a concrete SQLAlchemy repository.

## Accepted design decision

Nutrition Targeting application owns use-case-shaped structural contracts:

- `TargetDerivationSource`: only `profiles_for_household` and `active_standard`;
- `ProfileSink`: only `add_profile`;
- `StandardSink`: only `add_standard`.

The existing concrete `NutritionTargetingRepository` already satisfies these contracts structurally. No wrapper, inheritance hierarchy, generic repository or runtime adapter layer was added.

This is intentionally not a one-interface-per-database-table design. Ports follow application use cases and dependency needs.

## Why this is preferable to one Repository port

A broad `NutritionTargetingRepositoryPort` would make target derivation depend on write/import/activation operations it does not use. That violates the project's ISP obligation and weakens CQS visibility.

A generic `Repository[T]` would erase domain-specific operations and is not justified by accepted variation. It is prohibited by YAGNI policy.

The narrow Protocols allow:

- application service signatures to expose their actual dependencies;
- simple fakes in use-case tests;
- the same concrete SQLAlchemy repository to satisfy multiple narrow consumer views;
- persistence mechanics to remain outside application.

## Implementation result

The coding slice added only application-owned Protocols and type annotations to existing application services/import commands.

No behavioral code, SQL schema, transaction semantics or domain behavior changed.

CI passed.

## Research conclusion

This second slice strengthens the first experiment:

1. Component Design can constrain persistence dependencies without prescribing unnecessary classes.
2. ISP is most useful when translated into **consumer-shaped contracts**, not when treated as a slogan.
3. CQS can guide port separation without requiring CQRS infrastructure.
4. DIP does not imply one wrapper object per port; structural typing lets one concrete repository implement several application-owned views.
5. YAGNI is an important counterweight to SOLID: applying DIP/ISP should reduce coupling, not multiply ceremonial layers.

No new Harness evaluator semantics were needed.

## Remaining risk

The current experiments use Python Protocol/structural typing. The semantic rule must remain language-independent. In Java/C#/TypeScript the same policy may materialize as explicit interfaces; in Go as small interfaces; in a functional language as function/record contracts.

Therefore Component Design skill should describe **consumer-owned contract shape and dependency ownership**, not mandate a language construct.
