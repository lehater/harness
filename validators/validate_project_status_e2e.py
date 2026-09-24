from pathlib import Path
import tempfile, yaml
import sys
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from project_status import bootstrap_registry, status, validate_registry

catalog={"authorities":[{"id":"PRODUCT-REQUIREMENTS"},{"id":"SECURITY-ARCHITECTURE"},{"id":"OPERABILITY-DESIGN"}]}
core={"authorities":[{"id":"PRODUCT-REQUIREMENTS"},{"id":"SECURITY-ARCHITECTURE"}],
      "artifacts":[{"id":"PRODUCT","authority":"PRODUCT-REQUIREMENTS","path":"product.yaml","provides":["product.intent"],"depends_on":[]}],
      "questions":[{"id":"Q-SEC","authority":"SECURITY-ARCHITECTURE","text":"trust?","blocks":[],"blocks_capabilities":["security.trust"]}]}

# Existing project migration: only provable facts are inferred.
reg=bootstrap_registry(catalog,core=core)
rows={r["authority_id"]:r for r in reg["assessments"]}
assert rows["PRODUCT-REQUIREMENTS"]["applicability"]=="REQUIRED"
assert rows["SECURITY-ARCHITECTURE"]["applicability"]=="UNRESOLVED"
assert rows["OPERABILITY-DESIGN"]["applicability"]=="UNASSESSED"
assert not validate_registry(catalog,reg)

# Idempotent reconcile preserves accepted assessment.
accepted_na={"authority_id":"OPERABILITY-DESIGN","applicability":"NOT_APPLICABLE",
 "evidence":["no-runtime"],"rationale":"No production runtime exists.",
 "depends_on_evidence":["deployment-model"],"reopening_conditions":["production runtime introduced"]}
reg["assessments"]=[accepted_na if r["authority_id"]=="OPERABILITY-DESIGN" else r for r in reg["assessments"]]
reg2=bootstrap_registry(catalog,reg,core)
assert {r["authority_id"]:r for r in reg2["assessments"]}["OPERABILITY-DESIGN"]["applicability"]=="NOT_APPLICABLE"

# Catalog evolution surfaces a new Authority as UNASSESSED.
catalog2={"authorities":catalog["authorities"]+[{"id":"DATA-DESIGN"}]}
reg3=bootstrap_registry(catalog2,reg2,core)
assert {r["authority_id"]:r for r in reg3["assessments"]}["DATA-DESIGN"]["applicability"]=="UNASSESSED"

projection=status(catalog2,reg3,core)
p={r["authority"]:r for r in projection["rows"]}
assert p["PRODUCT-REQUIREMENTS"]["operational_status"]=="IN_PROGRESS"
assert p["SECURITY-ARCHITECTURE"]["operational_status"] is None
assert p["OPERABILITY-DESIGN"]["operational_status"] is None
print("project status end-to-end: OK")


# Authority split migration never propagates old applicability blindly.
old_catalog={"authorities":[{"id":"INTERFACE-DESIGN"}]}
old_reg={"assessments":[{"authority_id":"INTERFACE-DESIGN","applicability":"REQUIRED",
 "evidence":["legacy-interface"],"rationale":"Legacy accepted interface knowledge.",
 "depends_on_evidence":["legacy-interface"],"reopening_conditions":["interface semantics change"]}]}
new_catalog={"authorities":[{"id":"MACHINE-INTERFACE-DESIGN"},{"id":"HUMAN-INTERFACE-DESIGN"}]}
migrated=bootstrap_registry(new_catalog,old_reg,authority_migrations={"INTERFACE-DESIGN":["MACHINE-INTERFACE-DESIGN","HUMAN-INTERFACE-DESIGN"]})
m={r["authority_id"]:r for r in migrated["assessments"]}
assert m["MACHINE-INTERFACE-DESIGN"]["applicability"]=="UNASSESSED"
assert m["HUMAN-INTERFACE-DESIGN"]["applicability"]=="UNASSESSED"
assert migrated["migration_conflicts"][0]["resolution"]=="MANUAL-DECISION"
print("authority split migration: OK")
