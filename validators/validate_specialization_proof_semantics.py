#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

from reference_materializer import load_yaml, materialize

CATALOG=ROOT/"spec/engineering-coverage/concern-catalog-v1.yaml"
PROOF=ROOT/"spec/engineering-coverage/semantic-proof-contract-v1.yaml"
AUTHORITIES=ROOT/"catalogs/software-authorities-v0.yaml"
MODEL=ROOT/"spec/research/reference-engineering-model-v0.yaml"
HOLDOUTS=ROOT/"spec/research/reference-materializer-fixtures/holdouts-v0.yaml"
RESEARCH=ROOT/"spec/research/specialization-proof-semantics-v0.yaml"


def load(path):
    value=yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    assert isinstance(value,dict),path
    return value


def main():
    catalog=load(CATALOG); proof=load(PROOF); authorities=load(AUTHORITIES)
    model=load_yaml(MODEL); holdouts=load(HOLDOUTS); research=load(RESEARCH)

    specialization_ids={x["id"] for x in catalog.get("specializations",[]) or []}
    assert {"specialized.safety","specialized.ai"}<=specialization_ids

    canonical_proofs=set((proof.get("proofs",{}) or {}).keys())
    assert "specialized.safety" not in canonical_proofs
    assert "specialized.ai" not in canonical_proofs

    authority_ids={x["id"] for x in authorities.get("authorities",[]) or []}
    specs=research["specializations"]
    for sid in ("specialized.safety","specialized.ai"):
        row=specs[sid]
        assert row["canonicalization"]=="blocked"
        obligations=row.get("proof_obligations",[]) or []
        assert len(obligations)>=3
        assert len({x["id"] for x in obligations})==len(obligations)
        used=set()
        for obligation in obligations:
            owners=obligation.get("candidate_authorities",[]) or []
            assert owners and set(owners)<=authority_ids
            assert isinstance(obligation.get("responsibility"),str) and obligation["responsibility"].strip()
            used.update(owners)
        assert len(used)>=3, (sid,used)
        assert row.get("unresolved"),sid

    by_id={x["id"]:x for x in holdouts["scenarios"]}
    for scenario_id, concern in (
        ("holdout-safety-critical","specialized.safety"),
        ("holdout-ai-agentic","specialized.ai"),
    ):
        scenario=by_id[scenario_id]
        assert concern in scenario["project_facts"]["activated_concerns"]
        result=materialize(model,authorities,proof,scenario["project_facts"],scenario["request"])
        assert result["status"]=="REFERENCE_MODEL_GAP",(scenario_id,result)
        codes={x["code"] for x in result.get("diagnostics",[]) or []}
        assert "REFERENCE_MODEL_GAP" in codes,(scenario_id,codes)

    decision=research["decision"]
    assert decision["reference_model_behavior"]=="keep-reference-model-gap"
    assert decision["harness_core_change"]=="none"

    print("specialization proof semantics research: PASS")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
