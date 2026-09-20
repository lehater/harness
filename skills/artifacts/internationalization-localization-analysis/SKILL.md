---
name: internationalization-localization-analysis
description: "Use to analyze locale, language, formatting, timezone/calendar and localization concerns while preserving domain semantics and routing decisions to Product, Domain, Interface, Data, Obligation and Verification owners."
---

# Internationalization / Localization Analysis

## Trigger

Use when an application serves multiple languages/locales/markets or when number, currency, date/time, timezone, calendar, collation, directionality or localized content can affect accepted behavior.

## Inputs

- accepted market/language/locale scope;
- domain temporal/monetary/text semantics;
- Interface and Data Design;
- applicable obligations;
- Verification/Test obligations.

## Read boundary

Framework locale defaults, OS timezone, translation libraries and formatting APIs are implementation evidence/mechanics, not accepted semantics.

## Procedure

1. Identify supported locale/language/market scope.
2. Separate domain meaning from presentation formatting.
3. Identify timezone/calendar rules that affect use-case semantics.
4. Identify number/currency/text/collation/directionality presentation requirements.
5. Route market/language scope to Product.
6. Route business meaning to Domain/Application.
7. Route presentation/interaction to Interface Design.
8. Route canonical storage representation to Data Design.
9. Route local legal/content variants to Obligation Analysis and the semantic owner.
10. Route proof to Verification/Test.
11. Record COVERED, NOT_APPLICABLE, DEFERRED_NONBLOCKING or QUESTION.

## Stop conditions

Stop when the analysis would otherwise choose supported locales, authoritative timezone/calendar, monetary semantics, translation meaning, collation/search semantics or local legal variant without an accepted owner decision.

## Output contract

Produce locale/temporal presentation coverage with semantic owner, presentation owner, canonical representation, applicable obligations, verification evidence and coverage state.

## Acceptance checks

- display timezone is not conflated with domain effective time;
- formatted currency is not conflated with monetary semantics;
- translated labels do not become identifiers;
- framework defaults do not create semantic decisions;
- local obligations route through Obligation Analysis;
- locale-specific proof traces to accepted scope.

## Registration

Register as reusable cross-Authority analysis, not I18N-DESIGN or LOCALIZATION-DESIGN Authority.

## Human projection

Prefer a matrix of semantic concern versus supported locale/market only where scope is accepted; otherwise surface routed Questions.
