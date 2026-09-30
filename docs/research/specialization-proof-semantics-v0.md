# Safety and AI specialization proof semantics v0

Status: research result. No canonical proof-contract or Reference Model change.

## Question

Do `specialized.safety` and `specialized.ai` have stable project-independent proof semantics that can be materialized by Reference Engineering Model v0?

## Existing Harness state

The canonical Concern Catalog already declares both specializations and requires explicit activation evidence.

The canonical semantic proof contract deliberately has no entries for either specialization. Reference Model v0 therefore returns `REFERENCE_MODEL_GAP` for the existing safety-critical and AI/agentic hold-outs.

That fail-closed behavior is retained.

## Safety result

NASA software-safety guidance makes three independently meaningful semantic products visible:

1. hazard analysis identifies hazardous events, causes, unsafe states, controls and mitigations;
2. safety-critical software requirements are derived from those hazards and mitigations;
3. verification evidence must trace back to hazardous events/requirements and demonstrate the safety behavior.

Sources:

- https://swehb.nasa.gov/spaces/SWEHBVC/pages/50888880/SWE-023+-+Software+Safety-Critical+Requirements
- https://swehb.nasa.gov/spaces/SWEHBVC/pages/50889421/SWE-192+-+Software+Hazardous+Requirements

This falsifies a simple “add one SAFETY capability” solution. Safety semantics cross requirements, architecture/design and verification ownership.

The obligations are stable enough for research vocabulary, but Harness does not yet have evidence for one canonical Authority assignment or stable semantic claim names.

## AI result

NIST AI RMF structures AI risk management across Govern, Map, Measure and Manage rather than one engineering artifact. It explicitly requires context/risk mapping, measurement and evaluation, lifecycle management, and human oversight. Measurement guidance calls out AI-specific failure modes, data dependence, socio-technical context, uncertainty, benchmarks and documented evaluation.

Sources:

- https://www.nist.gov/itl/ai-risk-management-framework
- https://airc.nist.gov/airmf-resources/airmf/5-sec-core/
- https://airc.nist.gov/airmf-resources/playbook/measure/

The resulting candidate obligations are:

- intended-use/risk context and capability boundaries;
- human oversight;
- measurement/evaluation with uncertainty;
- post-deployment risk monitoring.

These obligations span Product Requirements, Quality, Human Interface, Verification and Operability. They are not evidence for one `AI-RISK` Capability Type.

As of this research, NIST also states that AI RMF 1.0 is being revised. Harness should not freeze a canonical AI-specific vocabulary around a moving external framework.

## Decision

Keep both specializations as explicit `REFERENCE_MODEL_GAP` outcomes.

Do not:

- add a generic SAFETY or AI Capability Template merely to remove the gap;
- map the specialization to generic Quality or Security and claim closure;
- change Harness Core.

A future canonicalization task must first establish:

1. one canonical semantic owner for each independent proof obligation;
2. stable semantic claim names in the canonical proof contract;
3. positive and omission-sensitive executable fixtures;
4. evidence that the resulting templates remain project-independent.

Until then, the gap is the correct model output.
