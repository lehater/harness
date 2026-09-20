# Remaining Engineering Coverage Closure Research

Status: research candidate.

This research closes the remaining P1 general-purpose gaps and executes the previously deferred specialized stress cases. It does not assume that a named discipline is an Authority.

## 1. Build / reproducibility / artifact provenance

### External lens

Reproducible Builds defines reproducibility as recreating bit-for-bit identical specified artifacts from the same source, build environment and build instructions. SLSA provenance treats provenance as verifiable information about where, when and how software artifacts were produced, with build provenance linking outputs to source/build process.

References:
- https://reproducible-builds.org/docs/definition/
- https://slsa.dev/spec/v1.2/provenance

### Atomicity

A BUILD-DESIGN Authority fails:
- semantic cohesion: source selection, toolchain/environment constraints, dependency acquisition, build mechanics, provenance, release identity and verification are distinct decisions;
- independent change: reproducibility requirements can change independently of build tooling; build tooling can change behind stable artifact requirements;
- public contract: consumers need concrete artifact identity/provenance/reproducibility properties, not generic "build design".

### Ownership

- Product/Quality: required reproducibility/traceability properties when externally meaningful.
- Engineering Policy/Security: secure/reproducible build constraints and trust policy.
- Implementation Design: concrete build system/toolchain mechanics when constrained.
- External Dependency Analysis: dependency/toolchain acquisition and provenance.
- Verification: proof that produced artifacts satisfy accepted expectations.
- Change Transition: release/build migration with material coexistence/cutover states.

Build provenance is realization evidence. A build attestation does not become design truth merely because it exists.

Verdict: no BUILD-DESIGN or PROVENANCE Authority; no Core entity. Build/reproducibility is closed by existing owners plus External Dependency Analysis and Verification.

## 2. Human-interface quality: accessibility / usability

### External lens

WCAG 2.2 provides technology-independent, testable accessibility success criteria and explicitly notes that accessibility guidance often improves usability, while not covering every user need.

Reference:
- https://www.w3.org/TR/WCAG22/

### Boundary

Accessibility contains at least:
- product/user inclusion requirements;
- interaction semantics and presentation behavior;
- measurable quality constraints;
- externally imposed conformance obligations;
- verification/evaluation evidence.

A generic ACCESSIBILITY-DESIGN Authority would duplicate Product, Interface, Quality, Obligation and Verification.

Usability likewise cannot be owned as a generic score. Task success, error recovery, discoverability and cognitive load must be tied to accepted users/journeys and measurable/observable criteria.

### Ownership

- Product Requirements: target users, required supported interaction modes, user outcomes.
- Interface Design: focus/keyboard behavior, accessible names/relationships/status, interaction/presentation semantics.
- Quality Design: architecture-significant measurable usability/accessibility constraints.
- Obligation Analysis: externally imposed WCAG/legal/contractual applicability and required conformance level.
- Verification/Test: automated + human evidence against accepted criteria.
- Discovery/Product: user research evidence can reopen product/interface Questions; research evidence is not automatically accepted truth.

### NAPMS stress test

NAPMS already owns UI navigation/resource-detail contracts under Interface Design and quality constraints under Quality Design. Accessibility concerns can therefore route to the UI contract owner without a new Authority. If a regulation/contract mandates WCAG conformance, Obligation Analysis supplies applicability; Verification proves it.

Verdict: no ACCESSIBILITY-DESIGN or USABILITY-DESIGN Authority. Add reusable Human Interface Quality Analysis.

## 3. Internationalization / localization / temporal presentation

### External lens

W3C distinguishes internationalization (design/development that enables localization) from localization (adaptation to language, cultural and target-market requirements), including number/date/time formats and more than translation.

Reference:
- https://www.w3.org/International/questions/qa-i18n

### Semantic decomposition

- supported languages/locales/markets: Product;
- domain language and locale-sensitive business semantics: Domain;
- textual/presentation formatting, directionality, labels and interaction: Interface;
- storage/canonical instant/decimal representations: Data Design;
- timezone/calendar rules affecting use-case meaning: Domain/Application;
- local legal/content variants: Obligation + owning semantic Authority;
- resource/catalog selection and fallback mechanics: Implementation after accepted policy;
- verification: locale matrix, boundary cases and invariant preservation.

Critical rule: localization must not mutate domain truth accidentally. Display timezone is not necessarily domain effective time; formatted currency is not monetary semantics; translated labels are not identifiers.

Verdict: no I18N-DESIGN or LOCALIZATION-DESIGN Authority. Add reusable Internationalization/Localization Analysis.

## 4. Specialized stress case: multi-tenancy / isolation

Tenant identity can be Product/Domain semantics; tenant placement/isolation is System/Security/Data; quotas/noisy-neighbor targets are Quality/System; tenant lifecycle is Domain/Application/Data; proof is Verification.

A TENANCY-DESIGN Authority fails because these decisions change independently and have different consumers.

Verdict: no baseline Authority. Existing boundaries are sufficient. A project with tenancy must make tenant identity/ownership and isolation constraints explicit rather than rely on framework defaults.

## 5. Specialized stress case: offline-first / synchronization

Offline-first exposes:
- local/remote authority;
- conflict semantics;
- merge/reconciliation policy;
- causality/order/version identity;
- replay/idempotency;
- stale-data user semantics;
- synchronization transport and persistence.

Conflict resolution is domain/application truth, not a generic synchronization algorithm. Ordering/consistency/replay route through existing concurrency/reliability closure; persistence through Data; connectivity/topology through System; user-visible conflict behavior through Interface.

Verdict: no OFFLINE-DESIGN or SYNC-DESIGN Authority. Existing concurrency/reliability/data/change-transition analyses cover the cross-cutting mechanics once domain conflict semantics are explicit.

## 6. Specialized stress case: AI / ML / agentic systems

### External lens

NIST AI RMF is use-case-agnostic risk-management guidance across AI design, development, deployment and use. The NIST Generative AI Profile identifies risks that are novel to or exacerbated by generative AI and supplies lifecycle risk-management actions.

References:
- https://www.nist.gov/itl/ai-risk-management-framework
- https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence

### Boundary

AI systems introduce model/data/prompt/tool provenance, probabilistic behavior, evaluation sets, drift, human oversight, model/provider changes and sometimes safety/security risks. These do not form one atomic design owner:
- intended behavior/acceptable outcomes: Product/Domain;
- orchestration/tool authority: Application/System/Security;
- model/provider selection: Implementation/System constrained upstream;
- probabilistic quality thresholds: Quality;
- training/evaluation data semantics: Domain/Data Evidence;
- external model provenance: External Dependency Analysis;
- threats: Security Analysis;
- legal/policy duties: Obligation Analysis;
- evaluation: Verification/Test;
- model/provider migration: Capability Lifecycle + Change Transition.

A generic AI-DESIGN Authority would become a technology silo and violate the anti-split rule.

Verdict: no baseline AI/ML/AGENT Authority and no AI Core entity. A reusable AI-specific risk/evaluation analysis may be justified only when Harness is validated on a real AI system; current ordinary application evidence is insufficient to canonicalize it.

## 7. Specialized stress case: safety / hazard analysis

Safety-relevant systems differ from ordinary quality because hazard identification and risk/control coverage can have independent analytical value, similar to Security Analysis.

Candidate HAZARD-ANALYSIS:
- semantic cohesion: plausible — hazard/risk/control coverage against accepted system/use context;
- independent change: plausible — hazard evidence/analysis can evolve without owning underlying product/system decisions;
- public contract: plausible — produces hazard/control coverage and routes missing mitigations to semantic owners.

However no current Harness validation project supplies a genuine safety case. Creating the Authority now would be speculative.

Verdict: CONDITIONAL RESEARCH CANDIDATE, not canonical baseline Authority. Reopen when a safety-relevant project demonstrates hazard-analysis consumers and atomicity against Product, Quality, Security and Verification.

## 8. Specialized stress case: real-time / embedded / hardware-constrained

Hard timing semantics can be Product/Domain requirements; timing/resource budgets belong Quality; scheduling/topology/hardware placement System; device protocols Interface; memory/storage Data/Implementation; verification requires timing/resource evidence; deployment/update constraints may invoke Change Transition.

Hardware differences alone do not create an Authority.

Verdict: no REALTIME-DESIGN, EMBEDDED-DESIGN or HARDWARE-DESIGN baseline Authority. Existing owners remain adequate; a future safety-critical embedded project may additionally trigger Hazard Analysis research.

## Cross-cutting conclusion

The remaining cases reinforce the Harness rule: technology/topic names are poor Authority boundaries.

General-purpose closure after this research:
- build/reproducibility/artifact provenance: covered;
- accessibility/usability: covered with reusable analysis;
- internationalization/localization/temporal presentation: covered with reusable analysis;
- multi-tenancy: stress-tested, covered;
- offline/synchronization: stress-tested, covered;
- AI/ML/agentic: no baseline Authority; real-project validation required before specialized analysis is canonicalized;
- safety/hazard: plausible conditional Analysis Authority but insufficient evidence to instantiate;
- real-time/embedded/hardware: stress-tested, covered by existing boundaries.

No result in this pass requires a Core v0 change.
