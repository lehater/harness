# Prep target-scoped Knowledge exploration thin slice v0

Status: completed; executable scenario validated by the unchanged harness core.

## Purpose

Trace one active Prep user-facing idea from accepted problem evidence to the last pre-code implementation-design boundary:

selected LearningTarget -> target-relevant Knowledge -> canonical relations -> list/search/detail + graph exploration -> preserved target/exploration context.

The experiment does not evaluate production source code.

## Baselines

Harness: lehater/harness@6bb9586c3a93bc99665e1c1794cd61ebee0818dc

Prep: lehater/prep@b3ec3b0fec0d8ba29f2ca66867737e8838332592

Pinned Prep Engineering Graph fixture:
spec/scenario-suite/fixtures/external/prep-engineering-graph.yaml

Executable scenario:
spec/scenario-suite/scenarios/real-project-prep-target-knowledge-exploration-thin-slice.yaml

## Selected semantic thread

This is one thin slice with two inseparable obligations:

1. TARGET_SCOPE — a chosen LearningTarget determines the relevant Knowledge scope and that target context survives exploration;
2. REPRESENTATION_INDEPENDENCE — canonical Knowledge identity and relation semantics do not depend on graph geometry or any single visualization; list/search/detail remains equivalent access.

The product-level behavior is a composition rather than one Product Capability alone:

- PC-01 establishes the prepared target and reusable required scope;
- PC-03 makes reusable Knowledge identities and accepted relationships inspectable and navigable without prescribing one visualization.

Therefore "the knowledge graph" is not itself the product capability. It is one projection used to realize target-scoped Knowledge exploration.

## Canonical chain

Problem Space:
- desired-state knowledge scope can be uncertain;
- relevant information can be fragmented/inconsistent/redundant.

Vision:
- learner obtains a coherent view of the knowledge relevant to the chosen target;
- structure is instrumental and should serve navigation/understanding rather than become an end in itself.

Product Capabilities:
- PC-01 defines target scope;
- PC-03 defines navigable reusable Knowledge/relationships while explicitly refusing to prescribe graph/ontology/hierarchy representation.

Application Design:
- projects KnowledgeNodes currently relevant to a LearningTarget;
- projects accepted KnowledgeRelations among selected target-relevant nodes.

Task Model / User Journey:
- learner searches, filters, selects and navigates target-relevant Knowledge;
- equivalent list/search/detail and graph access use the same canonical identities;
- graph degradation does not remove non-graph access;
- recoverable failures preserve target/filter context.

Human Interface:
- TARGET-KNOWLEDGE is target-scoped;
- Target Workspace preserves selected LearningTarget;
- I-L-KNOWLEDGE keeps target/filter context and reversible focus;
- L-03-TARGET-KNOWLEDGE shows nodes reached from current target alignments and the same nodes in the interactive target-scoped graph.

Machine Interface:
- learning.target.knowledge.list requires target_id;
- learning.target.knowledge.graph requires target_id and returns canonical Knowledge plus accepted relations.

Frontend System Architecture:
- Learning owns selected LearningTarget context;
- Knowledge Exploration receives explicit global or target-derived scope;
- graph is renderer-neutral and preserves canonical Knowledge identity/relation semantics.

Component Design:
- KnowledgeExplorer coordinates list/search/detail and graph over one explicit KnowledgeScope;
- target scope is identified by canonical LearningTarget id;
- KnowledgeQueryPort exposes list/search/detail and graph for explicit global or target scope.

Verification / Test Design:
- target context preservation is a verification obligation;
- graph/non-graph equivalence is an executable oracle over canonical identities and relation semantics.

Implementation Design:
- FI-02 establishes prepared target context, Knowledge ports, list/search/detail and renderer-neutral graph contract;
- FI-03 adds the concrete 3D renderer behind that contract while retaining non-graph fallback;
- FI-04 realizes the Learning Knowledge workspace.

## Validation result

The unchanged Scenario Suite accepts the real canonical slice end-to-end through frontend implementation design.

Accepted transitions include:

- problem evidence -> product intent;
- product intent -> PC-01 + PC-03 product surface;
- product capabilities -> application projections;
- application -> task model -> user journey;
- user journey -> Information Architecture + Interaction Design;
- Information Architecture -> Interface Topology -> Screen/View;
- Interaction Design -> Screen/View;
- Screen/View -> Frontend System Architecture -> Component Design;
- Product Capability -> Frontend Verification -> Frontend Test Design;
- Component Design + Test Design -> Frontend Implementation Design.

No real semantic omission was found in this selected slice.

The two sensitivity controls are rejected exactly as intended:

- removing target scope from Screen/View produces UNDISPOSITIONED_SOURCE owned by HUMAN-INTERFACE-DESIGN;
- removing representation independence from Component Design produces UNDISPOSITIONED_SOURCE owned by COMPONENT-DESIGN.

The experiment therefore distinguishes intact real derivation from the two concrete semantic-loss mutations without a new Harness mechanism.

## Result interpretation

The real canonical slice is ACCEPTED end-to-end through frontend implementation design.

Two sensitivity controls prove that the check is discriminating:

- remove target scope from Screen/View -> RED owned by HUMAN-INTERFACE-DESIGN;
- remove representation independence from Component Design -> RED owned by COMPONENT-DESIGN.

No new Harness abstraction is introduced.
