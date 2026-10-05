# Process Simplicity and Efficiency v0
Status: canonical global constraint.

## Normative rule

When procedures preserve the same guarantees, require the simpler one: fewer
steps, artifacts, round trips, persisted state, recomputation and coordination.
Target **minimum sufficient process**, not minimum validation.

Validate at the cheapest sufficient layer; reuse unchanged CURRENT state;
evaluate affected closure; aggregate independent blockers; keep intermediate
state non-current.

CI is a verification boundary, not an interactive exploration mechanism.
Repeated generic project glue belongs in Harness.

Preserve semantic correctness, Authority, no fabricated acceptance,
reproducibility, currentness, traceability, compatibility and atomic/CAS
publication. Persist only invariant-bearing state. **automate mechanics, not
authority**.
