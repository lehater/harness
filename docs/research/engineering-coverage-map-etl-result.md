# Tiny ETL stress test

Status: synthetic research fixture.

The baseline Engineering Concern Catalog remains usable for a one-process CSV transformation script.

Key result:
- the same concern IDs still make sense;
- many rows become explicit NOT_APPLICABLE with evidence instead of requiring fake artifacts;
- data classification/privacy and safety remain UNASSESSED when facts are genuinely unknown;
- operability, dependency provenance, reproducibility, verification and error behavior remain meaningful even for a tiny script;
- Component Design can be explicitly NOT_APPLICABLE without claiming that "design does not matter";
- Architecture remains lightweight: one process + file boundaries is still an architecture decision, but does not require C4 ceremony.

This supports the original hypothesis that a stable cross-project concern catalog can apply from scripts to larger applications, provided applicability is first-class and the catalog does not mandate one artifact per concern.
