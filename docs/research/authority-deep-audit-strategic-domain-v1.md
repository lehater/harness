# Deep audit — STRATEGIC-DOMAIN-DESIGN

Verdict: SPLIT.

The current Authority fails applicability atomicity.

## Family A — DOMAIN-STRATEGY
Decision: classify problem-space/domain responsibilities and strategic importance/investment.
Accepted knowledge: subdomain landscape, strategic classification, domain vision/investment constraints.
Consumers: model-context strategy when strategic ownership constrains model boundaries; system architecture and tactical design when strategic classification changes isolation/investment choices.
Independent applicability: can be N/A for one coherent business responsibility even when several model languages/translation boundaries exist.

## Family B — MODEL-CONTEXT-STRATEGY
Decision: decide where a model/language applies and how independently modeled contexts relate/translate.
Accepted knowledge: model-context map, relationship/translation contracts.
Consumers: tactical domain, application, interface/integration design.
Independent applicability: can be N/A when one coherent model applies, even when domain-strategy classification/investment is material.

Both families have independent decision identity, outputs, consumers and lifecycle. They can be REQUIRED/N/A in opposite combinations.

Final research decision: replace current Authority with two candidate Authorities. Do not use PARTIALLY_APPLICABLE.
