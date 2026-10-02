from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
data = yaml.safe_load((ROOT / "spec/research/reference-applicability-project-graph-v1.yaml").read_text())
assert data["kind"] == "harness-reference-applicability-research"
assert set(data["states"]) == {"REQUIRED", "NOT_APPLICABLE", "UNRESOLVED"}
cases = data["cases"]
assert len(cases) >= 10
domains = {c["domain"] for c in cases}
for required in {"ddd","concurrency","distributed-systems","security","data","performance-quality","operability","migration-change","verification"}:
    assert required in domains, required

for c in cases:
    assert c["status"] in data["states"]
    assert c.get("evidence"), c["id"]
    assert c.get("depends_on_evidence"), c["id"]
    assert c.get("rationale"), c["id"]
    assert c.get("reopening_conditions"), c["id"]
    blob = " ".join(str(v).lower() for v in c.values())
    assert "simple project" not in blob and "simple-project" not in blob, c["id"]
    if c["status"] == "REQUIRED":
        assert c.get("produces"), c["id"]
        assert c.get("consumer") or c.get("terminal_reason"), c["id"]
        if c.get("consumer"):
            assert c.get("consumer_output"), c["id"]
    elif c["status"] == "NOT_APPLICABLE":
        assert not c.get("produces"), c["id"]
    elif c["status"] == "UNRESOLVED":
        assert c.get("question"), c["id"]

print("reference applicability research: OK")
