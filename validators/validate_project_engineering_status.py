from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
data = yaml.safe_load((ROOT / "spec/research/project-engineering-status-v1.yaml").read_text())

assert data["kind"] == "harness-project-engineering-status-research"
assert set(data["applicability_states"]) == {"UNASSESSED", "REQUIRED", "NOT_APPLICABLE", "UNRESOLVED"}
assert "PARTIALLY_APPLICABLE" in data["forbidden_applicability_states"]
assert data["registry"]["default"] == "UNASSESSED"
assert data["registry"]["copy_authority_definition"] is False
assert {"completion", "operational_status"} <= set(data["registry"]["forbidden_stored_fields"])
assert data["operational_projection"]["persisted"] is False
assert data["rules"]["partial_applicability"] == "forbidden"

fixture = data["fixture"]
records = fixture["records"]
assert len(records) == len(fixture["catalog"])
assert {r["authority_id"] for r in records} == set(fixture["catalog"])

def operational(states):
    if "WAIT" in states:
        return "BLOCKED"
    if states and all(s == "SATISFIED" for s in states):
        return "COMPLETE"
    if any(s == "SATISFIED" for s in states):
        return "IN_PROGRESS"
    return "NOT_STARTED"

actual = []
for r in records:
    state = r["applicability"]
    assert state in data["applicability_states"]
    if state != "UNASSESSED":
        for field in data["rules"]["non_unassessed_requires"]:
            assert r.get(field), (r["authority_id"], field)
    if state == "UNRESOLVED":
        assert r.get("question"), r["authority_id"]
    actual.append([r["authority_id"], state, operational(r["runtime"]) if state == "REQUIRED" else None])

assert actual == fixture["expected"], (actual, fixture["expected"])

# Catalog evolution must surface new reference Authorities as UNASSESSED.
catalog2 = fixture["catalog"] + ["OPERABILITY-DESIGN"]
existing = {r["authority_id"]: r for r in records}
bootstrapped = [existing.get(a, {"authority_id": a, "applicability": data["registry"]["default"]}) for a in catalog2]
assert bootstrapped[-1] == {"authority_id": "OPERABILITY-DESIGN", "applicability": "UNASSESSED"}

print("project engineering status research: OK")
