# Scoped capabilities research — v0

Status: experimental conclusion for Engineering Graph v0.

## Problem

NAPMS has several subject-specific artifacts under one semantic producer
Authority. For example, several Bounded Context tactical models all provide the
broad semantic class `engineering.domain.tactical-model`.

A target may need to prove that *each selected subject* has such knowledge.
Treating Design Profile `subject` as descriptive only is insufficient for that
coverage check.

## Current proven solution

NAPMS projects explicit subject-scoped CapabilityIds into the transient Core
model and Engineering Graph, then evaluates those CapabilityIds exactly like any
other knowledge.

This is fail-closed and already validated by the Resource Catalogue coverage
negative test.

## Why Core subject-aware providers are deferred

Making `subject` first-class in Core would require more than provider filtering.

A parameterized production contract must answer how subject flows through every
upstream requirement. Examples include:

- subject-specific tactical model may depend on a global strategic model;
- it may depend on a subject-specific use-case model;
- some subjects may legitimately share one upstream artifact;
- a downstream capability may aggregate several subjects rather than inherit one.

A generic rule such as "propagate the same subject to every prerequisite" is
therefore incorrect.

Supporting first-class parameterized capabilities would need a binding language
or equally explicit production-instance semantics. That would materially enlarge
Core/Engineering Graph before a second independent consumer demonstrates the
same need.

## Evidence from current consumers

- NAPMS needs independently provable coverage for several Bounded Context
  subjects and uses scoped CapabilityIds.
- Nutrition Management currently names its context/domain capabilities explicitly
  and does not require one repeated base CapabilityId parameterized over subjects.
- the greenfield CSV pilot has one project subject and no repeated subject
  coverage problem.

## v0 decision

For Engineering Graph v0:

- CapabilityId remains the fully resolved provider key;
- `subject` remains expectation/work-item identity metadata;
- independent per-subject coverage must resolve to independent CapabilityIds
  before target-state evaluation;
- target adapters/project policy may derive those CapabilityIds from canonical
  coverage metadata;
- no universal scoped-ID string syntax is mandated yet.

Revisit first-class parameterization only after another project independently
requires repeated semantic capabilities over a subject set and its prerequisite
binding needs are understood.
