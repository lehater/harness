# View Boundary Method — Prep topology pilot v0

Status: known-project analytical pilot; non-normative project evidence.

## Purpose

Exercise the proposed Interface Topology view-boundary method against an accepted
real-project topology without rewriting project truth.

Pinned inputs:

- Harness baseline: `3d89d4e7d5574fed37acc6c517b13d8f0ce0c09d`
- Prep baseline: `263592a3615d51a05b72646c431f0c289a848013`

Prep sources inspected:

- `docs/application/task-model.yaml`
- `docs/interface/information-architecture.yaml`
- `docs/interface/interaction-design.yaml`
- `docs/interface/interface-topology.yaml`
- `docs/interface/screen-view-design.md`

The pilot asks whether the method finds useful boundary questions beyond the
existing Task -> Interaction Context -> View closure checks, and whether it
avoids forcing arbitrary merges/splits.

## Evaluation dimensions

For each material boundary inspect:

- current user goal/decision continuity;
- simultaneous or persistent information dependency;
- transient working-state continuity;
- commit/cancel/recovery semantics;
- mode/role/authorization change;
- independent revisit/deep-link/resume value;
- repeated context switching/refinding cost.

These dimensions are decision evidence, not a score.

## Boundary results

### VIEW-TARGETS -> VIEW-TARGET — KEEP

`VIEW-TARGETS` owns comparison of plausible target directions. `VIEW-TARGET`
owns establishment/refinement of the chosen active Target and its requirements.

The transition has a meaningful outcome boundary: candidate comparison ends with
a chosen direction (or remains unresolved), after which active-Target work has a
different responsibility and state context.

A merge is possible as a presentation treatment, but there is sufficient
semantic evidence for independent topology identities.

### VIEW-TARGET -> VIEW-CURRENT — KEEP

Current-position interpretation depends on an established active Target and has
its own primary decision surface: evidence-backed state, gaps/uncertainty and
Next focus.

The Target view owns target establishment/requirements rather than ongoing
current-state diagnosis. Separate responsibilities and a meaningful prerequisite
boundary justify the current topology.

### VIEW-CURRENT <-> VIEW-KNOWLEDGE — MATERIAL REVIEW

This is the strongest boundary question found by the method.

Evidence for keeping separate:

- Knowledge is independently findable in accepted Information Architecture;
- `IX-KNOWLEDGE` has a coherent exploration responsibility;
- Knowledge may be explored without a selected Next focus;
- Knowledge selection must not mutate Target/focus state.

Evidence for keeping context together:

- Knowledge is often entered from a concrete current gap/focus;
- active Target and optional Next focus must remain recoverable;
- representative work may alternate Current -> Knowledge -> Current while the
  higher-level goal remains unchanged;
- loss of the originating gap/focus would impose refinding/reconstruction cost.

Disposition:

No topology defect is proven from repository semantics alone. The boundary is a
material decision that should be challenged as:

1. separate navigation destinations with preserved context;
2. one workspace with persistent/supporting Knowledge context;
3. contextual Knowledge surface from Current while retaining independently
   addressable Knowledge entry where justified.

Representative task-flow evidence is needed to discriminate these candidates.
The current topology remains valid pending that evidence.

### VIEW-ACTIVITY -> VIEW-EVIDENCE-CHANGE — KEEP

Although both views map to `IX-ACTIVITY`, the split has an explicit operational
boundary:

- the activity attempt is completed/submitted;
- evidence processing follows;
- the next view owns interpretation of a reviewable evaluated result and
  continuation choice.

The transition therefore changes the primary responsibility and result/recovery
semantics. One Interaction Context spanning multiple Views is not itself a
defect.

### contextual -> VIEW-PREPARE-SUPPORT -> origin — KEEP CONTEXTUAL

The current topology already models this as contextual rather than primary
global navigation.

Separate identity is supported by:

- a PreparationRequest lifecycle;
- requesting/partial/unresolved/rejected/dependency-unavailable states;
- resumable source/provenance context;
- accepted partial results plus explicit remainder;
- explicit return-to-origin semantics.

A short modal/disclosure would be weaker for the long-lived/partial/recovery
cases represented by accepted semantics. The current contextual View is
therefore justified while remaining non-global.

## What the pilot demonstrates

The method adds information that the existing deterministic closure evaluator
does not provide:

- it can justify an existing split from goal/state/commit semantics;
- it can identify one materially contestable boundary without declaring the
  whole topology invalid;
- it distinguishes a semantic View decision from downstream pane/layout choice;
- it does not infer boundaries from domain entities, APIs or routes;
- it can surface where empirical task-flow evidence is the remaining
  discriminator.

The pilot does not justify a deterministic merge/split validator or promotion of
the research D0-D3 labels into canonical project truth.

## v1 consequence for Harness

The minimum useful integration is:

1. canonical boundary dimensions in `frontend-design-v0.md`;
2. an executable boundary review in `interface-topology-design/SKILL.md`;
3. a Decision Governance `view-boundaries` axis;
4. local-only composition alternatives retained in `screen-view-design`;
5. deterministic validators continue to enforce structural closure rather than
   pretending to calculate UX correctness.

Further formalization should wait for materially different project topologies or
a demonstrated repeated failure mode.
