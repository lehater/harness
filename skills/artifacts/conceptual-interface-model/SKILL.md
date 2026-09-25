---
name: conceptual-interface-model
description: "Define the user-facing conceptual model between accepted task/journey/domain semantics and information/interaction structure."
---
# Conceptual Interface Model

## Trigger
Use when actionable work has `knowledge_kind: conceptual-interface-model`.

Owner: HUMAN-INTERFACE-DESIGN.

## Responsibility
Define concepts, modes, user-visible state vocabulary and relationships the interface uses to make accepted product behavior understandable. This is not the tactical Domain Model and not a screen map.

## Inputs
Accepted Product Requirements, Task Model, User Journeys, exposed Domain/Application semantics, and material security/policy distinctions.

## Procedure
1. Enumerate concepts the user must recognize to complete accepted tasks.
2. Map every concept to upstream meaning; do not invent domain/product semantics.
3. Define user-visible modes only when they materially change available work or interpretation.
4. Define shared visible state vocabulary where it crosses multiple interactions.
5. Record conceptual relationships needed by IA and Interaction Design.
6. Keep navigation locations, screens and layout downstream.
7. Route missing meaning as Questions.
8. Produce/register the project-native contract and reevaluate.

## Output contract
Concept ids and meaning/upstream refs; material modes; shared state vocabulary; conceptual relationships; unresolved Questions.

## Acceptance checks
Every concept traces upstream; domain entities are not copied mechanically; modes are not authorization roles unless upstream says so; no navigation/page/layout decision is used as conceptual truth; downstream IA/Interaction can proceed without inventing concepts.

## Human projection
Concept diagrams and vocabulary maps are projections, not required file formats.
