# Research — Autonomous Engineering Coverage loop pilot

Status: research only. No main/canonical Harness changes.

## Goal

Test whether the unified Engineering Coverage evaluator can drive a real project from derived gaps to completion without a manually maintained required-concern checklist.

## Project

Nutrition Management research branch.

Consumers:
- IMPLEMENTATION;
- FRONTEND-IMPLEMENTATION.

## Loop

The exercised control loop was:

```text
evaluate selected Consumer
→ derive activated concerns
→ derive semantic proof gaps
→ classify work frontier
→ repair graph/model defects first
→ route missing knowledge
→ extend/create canonical project knowledge
→ materialize capabilities
→ reevaluate
```

## Defects found by the loop

The pilot exposed several structural defects before knowledge production:

1. two unconsumed public BLS capabilities that existed only in Harness metadata;
2. one stale Core artifact pointing at the accepted Component Design path with the wrong Authority;
3. over-activation of `governance.privacy` from personal-data presence despite no independent normative source;
4. missing conditional `OPERABILITY-DESIGN` and `SECURITY-ANALYSIS` responsibilities for the frontend;
5. a tendency to invent `coverage.*` project capabilities for concern gaps.

The last item was rejected. Once canonical artifacts were extended, the correct model was to attach additional semantic claims to existing project capabilities rather than create a second Coverage-specific ontology.

## Backend result

Initial evaluated state after activation/proof migration:

- 33 activated concerns;
- 26 remaining gaps.

After eliminating metadata-only false gaps and performing one routed knowledge loop:

- privacy over-activation was removed;
- accepted Data, Interface, Engineering Policy, Component, Verification and Implementation artifacts were extended where real knowledge was missing;
- existing canonical capabilities received the resulting semantic claims.

Final backend result:

```text
activated: 32
remaining: 0
completion_ready: true
work_items: 0
question_frontier: 0
```

## Frontend result

Before the frontend completion loop:

```text
activated: 50
remaining: 25
```

The remaining work decomposed into:

- existing canonical capabilities whose semantics needed extension;
- one explicit N/A decision for current-scope i18n;
- independently valuable Operability Design;
- independently valuable Security Analysis.

The loop added project-native canonical contracts for:

- frontend runtime configuration/logging/health/local incident behavior;
- frontend threat/control coverage, vulnerability-management and secure-development obligations;

and extended existing Frontend Architecture, Security Architecture, Component Design, Verification Design and Implementation Design.

Final frontend result:

```text
activated: 50
remaining: 0
completion_ready: true
work_items: 0
question_frontier: 0
```

## Integration result

At the completed Nutrition research head:

- Research Engineering Coverage workflow: SUCCESS;
- existing pinned Harness Integration: SUCCESS;
- project CI/tests: SUCCESS.

Therefore the research Coverage mechanism can coexist with the current pinned Harness integration during migration.

## Important architecture findings

### Coverage is not a second ontology

Do not create project capabilities merely because a concern exists.

A concern may be proven by additional semantic claims on an existing capability when the same Authority/artifact coherently owns the knowledge.

Create a new capability only when the knowledge has an independently useful project producer/consumer contract.

### Structural repair precedes knowledge generation

The autonomous loop must prioritize:

1. invalid/stale graph metadata;
2. applicability mistakes;
3. missing Authority boundary;
4. missing production contract;
5. actual missing canonical knowledge.

Otherwise an agent may generate unnecessary documents to compensate for a bad model.

### Conditional Authorities are real routing decisions

Operability and Security Analysis were instantiated only when the frontend topology created independently valuable pre-code contracts.

Quality Design was not instantiated: the current unquantified quality constraints remained coherently owned by Frontend Architecture.

### Applicability is evidence-driven

Personal-data presence does not itself create a governance/privacy obligation.

Current Nutrition obligation research makes OBLIGATION-ANALYSIS not applicable until a material law/regulation/contract/policy/platform source is introduced.

## Conclusion

The first real autonomous Coverage completion loop succeeded for two different Consumers in the same repository.

The next validation target should be NAPMS because it has more complex domain/security/operability/quality structure and is more likely to expose remaining errors in activation, subject scoping and Authority routing.
