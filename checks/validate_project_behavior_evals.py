from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
data = yaml.safe_load((ROOT / "spec/research/project-behavior-evals-v1.yaml").read_text())
assert data["kind"] == "harness-project-behavior-evals"
assert data["rules"]["context_policy"] == "selective"
scenarios = data["scenarios"]
required_ids = {"crud-single-process","payments-concurrency","multi-model-domain","security-heavy-service","legacy-migration","ephemeral-cli"}
assert required_ids <= {s["id"] for s in scenarios}

for s in scenarios:
    expect = s["expect"]
    assert s.get("evidence"), s["id"]
    assert expect.get("context_topics"), s["id"]
    required = set(expect.get("required", []))
    na = set(expect.get("not_applicable", []))
    unresolved = set(expect.get("unresolved", []))
    assert not (required & na), s["id"]
    assert not (required & unresolved), s["id"]
    assert not (na & unresolved), s["id"]
    blob = " ".join(s.get("evidence", []) + list(required) + list(na))
    for forbidden in data["rules"]["forbidden_justifications"]:
        assert forbidden not in blob, (s["id"], forbidden)

crud = next(s for s in scenarios if s["id"] == "crud-single-process")
assert "distributed-failure-semantics" in crud["expect"]["not_applicable"]
assert "distributed.coordination" in crud["expect"]["forbidden_capabilities"]

payments = next(s for s in scenarios if s["id"] == "payments-concurrency")
assert "concurrent-state-semantics" in payments["expect"]["required"]
assert "security.architecture" in payments["expect"]["required_capabilities"]

multi = next(s for s in scenarios if s["id"] == "multi-model-domain")
assert "product-capability-is-bounded-context" in multi["expect"]["forbidden_inferences"]
assert "subdomain-is-bounded-context" in multi["expect"]["forbidden_inferences"]

print("project behavior evals: OK")
