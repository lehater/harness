# Experimental Artifact Schemas

Status: research-only. These schemas are not canonical Harness contracts.

They test whether recurring CanonicalArtifact semantic shapes can use reusable
machine-verifiable profiles without changing Core, Capability identity, Authority
boundaries, or project-native canonical ownership.

## product-requirements/v0-experiment

Required:

- purpose;
- one or more goals;
- one or more named requirement groups;
- every group has one or more requirement statements.

Optional:

- constraints;
- acceptance examples;
- non-goals;
- structured evidence/provenance records when the requirements artifact itself owns them.

The profile deliberately does not require acceptance examples merely because the
artifact is Product Requirements. Acceptance becomes mandatory only if the concrete
artifact claims an acceptance capability and its semantic acceptance process
establishes that the corresponding fields are sufficient.

## implementation-design/v0-experiment

Required:

- purpose;
- one or more named design sections containing concrete implementation-facing
  decisions;
- one or more implementation slices;
- one or more completion criteria.

Optional:

- forbidden decisions;
- open questions;
- design references;
- explicit authorization semantics.

The profile does not prescribe language, framework, persistence technology,
repository layout, or a fixed number of sections.

## Test rule

Structural PASS is not semantic acceptance. Each candidate also carries:

- the original canonical source path;
- the CapabilityIds it is intended to materialize.

The experiment succeeds only if manual source comparison finds no missing or
invented semantics and the project can discard the candidate without changing its
current canonical state.


## cli-contract/v0-experiment

Required:

- command syntax;
- one or more argument contracts;
- one or more success semantics.

Optional:

- failure classes with optional concrete exit status;
- representation rules;
- outer-adapter/boundary rules;
- explicit scope exclusions.

The profile intentionally does not assume HTTP-style operations or a fixed stderr
format. It is one Interface Contract profile alongside standard-native profiles
such as OpenAPI.
