# Deep audit — ENGINEERING-POLICY

Verdict: KEEP with strict anti-bucket invariant.

Decision: select project-wide normative engineering obligations that constrain multiple semantic/design Authorities without owning their semantics.

Accepted knowledge: reviewable engineering-policy obligations, e.g. dependency/supply-chain discipline or architecture discipline translated into observable constraints.

Consumers: repository evidence explicitly has Component Design consume engineering-policy obligations; repository realization/Implementation consumes policy together with architecture/security/quality/verification. Integration guidance models policy as upstream of applicable architecture/application/component production.

Necessity: a cross-cutting project rule can remain normative while individual architecture/component decisions change; duplicating it into every semantic Authority creates conflicting ownership.

Encapsulation: policy states constraints, not product/domain/security/data decisions. Externally imposed law/contract/license provenance belongs to OBLIGATION-ANALYSIS.

Independent lifecycle: project engineering discipline can change/version independently and invalidate multiple downstream realizations.

Anti-bucket invariant: instantiate only when an accepted obligation has cross-Authority consumers and independent project lifecycle/provenance. Principle names, local preferences or single-Authority constraints are insufficient.

Final research decision: confirmed conditional Authority. Remove from further boundary work.
