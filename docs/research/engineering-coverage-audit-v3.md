# Engineering Coverage Audit v3 — Closure Baseline

Status: candidate final coverage inventory after the 2026-09 research program.

## Purpose

Determine whether material application-engineering territories remain unowned or unanalysed in Harness, without equating discipline names with Authorities.

## General-purpose coverage

The following areas now have explicit ownership or reusable closure:
- product/problem/requirements;
- strategic/tactical domain and application/use-case design;
- system/interface/data/component/implementation design;
- quality, verification and test design;
- engineering policy;
- security architecture and security analysis;
- operability;
- reliability/failure semantics;
- concurrency/consistency/ordering/backpressure;
- performance/capacity/resource/cost;
- recovery/backup/restore/continuity;
- data governance/privacy/retention;
- external obligations/provenance/applicability;
- change/release/migration/compatibility;
- accepted-knowledge lifecycle/supersession/revalidation;
- external dependencies/acquisition/supply chain;
- build reproducibility/artifact provenance;
- data evidence/fitness/lineage;
- accessibility/usability;
- internationalization/localization/temporal presentation.

## Specialized stress coverage

Multi-tenancy, offline/synchronization and real-time/embedded concerns decompose across existing semantic owners and closure analyses; they do not justify baseline Authorities.

AI/ML/agentic systems do not justify a technology Authority. A specialized AI risk/evaluation analysis remains intentionally uncanonicalized until validated on a real AI project.

Safety/hazard analysis is the only remaining plausible conditional Analysis Authority candidate. Atomicity is plausible, but current Harness validation projects do not provide a genuine safety case. It remains an explicit reopening condition, not a current gap for ordinary software applications.

## Core status

No completed research in this program demonstrated a need to expand Core v0 beyond Authority, CanonicalArtifact, Question, CapabilityId and dependency semantics.

Capability Lifecycle remains a projection above Core.

Project-native runtime, supply-chain, provenance, lineage and verification evidence remain outside Core unless future integration failure demonstrates a common missing primitive.

## Closure criterion

For general-purpose application development, the research inventory has reached closure: no known P0/P1 engineering territory remains both material and unowned/unanalysed.

This is not a claim that every future software domain is covered. New project classes must reopen coverage when they demonstrate semantics that existing Authority/Capability/Question/analysis composition cannot express.

## Explicit reopening triggers

Reopen coverage research when at least one occurs:
- a consumer needs engineering knowledge with no existing semantic owner;
- two existing Authorities must both own the same atomic decision;
- a reusable analysis repeatedly needs to make rather than route semantic decisions;
- project integrations must duplicate the same evidence/history because Harness lacks a minimal common projection;
- a safety-relevant project needs independent hazard/control analysis;
- a real AI/ML/agentic project demonstrates evaluation/risk semantics not expressible through Product/Domain/Quality/Security/Data Evidence/Verification/Change Transition;
- a hardware/real-time project demonstrates an independently changing public contract not captured by System/Interface/Quality/Implementation.

## Conclusion

The next phase should not continue speculative taxonomy research.

Harness should now be evolved by:
1. applying the canonical model to real projects;
2. observing concrete consumer failures;
3. reopening research only from those failures;
4. keeping Core changes evidence-driven.

The remaining work is validation and application, not another broad inventory pass.
