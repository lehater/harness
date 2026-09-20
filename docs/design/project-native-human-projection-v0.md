# Project-native Human Projection v0

Status: experimental contract validated against Nutrition Management.

## Problem

Harness already defines generated documentation for Harness-managed typed knowledge under `.harness/knowledge/**`. Nutrition Management demonstrates a second case: the accepted engineering knowledge is intentionally project-native Markdown plus an Engineering Graph/Core realization. Copying that knowledge into Harness-managed YAML merely to render documentation would create a second semantic source and violate Integration Contract v0.

A human projection is still useful, but it must be derived without becoming another Authority or canonical knowledge store.

## Boundary

Human Projection owns **navigation, assembly and faithful summarization of already accepted engineering knowledge**.

It MUST NOT:
- decide product/domain/architecture/implementation semantics;
- repair contradictions;
- resolve Questions;
- infer applicability that canonical analysis has not established;
- register capabilities;
- replace canonical artifacts;
- require project-native knowledge to be copied into `.harness/knowledge/**`.

Generated output is disposable and may be deleted/rebuilt without loss of accepted knowledge.

## Inputs

A project-native projection reads:
1. the selected Engineering Graph and Consumer;
2. the Core realization used to satisfy that Consumer;
3. canonical artifact paths/providers in the resulting capability closure;
4. optional accepted project-native coverage/conformance artifacts;
5. optional project-owned projection configuration controlling document grouping and destination.

The projection must identify its source baseline and selected Consumer.

## Source discipline

Only accepted CanonicalArtifacts in the selected closure may supply engineering assertions.

A renderer may quote, reorganize or summarize those artifacts, but every generated section must retain source traceability.

If canonical sources conflict, omit the disputed synthesized claim and expose the conflict/source references. Do not choose a winner.

If a required human section cannot be written without a new semantic decision, projection fails for that section; it does not create design truth.

## Output contract

The recommended project-native output is a generated documentation set with:
- a generated index/overview;
- topic projections useful to the project's audience;
- explicit canonical-source references per section;
- current Consumer/readiness statement derived from Harness evaluation;
- unresolved Questions and applicability/reopening notes when canonical sources expose them.

The exact document taxonomy is presentation policy, not a Core contract. Projects may group the same canonical knowledge differently.

Every generated file must carry a notice equivalent to:

> Generated projection from accepted canonical project knowledge. Do not edit as a source of truth.

## Two projection modes

### Managed knowledge projection

Existing `workspace.py render` remains authoritative for typed `.harness/knowledge/**` artifacts.

### Project-native projection

When canonical artifacts already exist in project-owned formats, use an adapter/renderer that reads those artifacts directly. Do not migrate them to managed schemas only for rendering.

Both modes obey the same invariant: generated documentation is not canonical.

## Nutrition validation

Nutrition uses direct Engineering Graph/Core integration but its accepted semantic artifacts are project-native Markdown.

For Consumer `IMPLEMENTATION`, the closure already exposes requirements, context/domain design, architecture, application/data/interface/component design, implementation design and verification design. The accepted current-Harness conformance artifact supplies cross-cutting applicability/reopening conclusions.

A useful human projection can therefore be generated without creating any new engineering Capability.

Nutrition also demonstrates why projection must not simply concatenate files:
- one artifact may serve several human topics;
- one human topic may require several Authorities;
- project-specific domain Authorities should be explained in domain terms rather than renamed to catalog names;
- implementation-readiness is derived from the Consumer closure, not from a document status sentence alone.

## Acceptance checks

A project-native projection is conforming when:
1. every substantive engineering statement is traceable to accepted canonical input;
2. no generated file is registered as a capability provider merely because it was generated;
3. deleting generated output leaves Harness target state unchanged;
4. regeneration from the same accepted baseline is deterministic in structure/content except explicitly non-semantic metadata;
5. unresolved Questions remain visible and are not silently answered;
6. project-native canonical files remain the semantic source;
7. the renderer contains no project-specific semantic decision logic.

## Integration consequence

Integration Contract v0 does not change.

Human Projection is an optional view above the Engineering Graph/Core boundary. It may be implemented by generic tooling plus project-owned grouping configuration.

A project-specific grouping configuration is acceptable because presentation/navigation is project-owned. Project-specific semantic branches inside Harness are not.

## Promotion criterion

Do not add a generic universal documentation schema to Core.

Promote renderer/configuration conventions only after at least two structurally different projects can produce useful projections without duplicating semantic truth or adding project-specific semantics to Harness.
