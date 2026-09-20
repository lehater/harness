#!/usr/bin/env python3
from pathlib import Path
import sys, yaml

ROOT = Path(__file__).resolve().parents[1]

def load(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)

def leaf_ids(catalog):
    result=[]
    def walk(node):
        children=node.get("children",[]) or []
        if not children:
            result.append(node["id"])
        else:
            for child in children:
                walk(child)
    for root in catalog.get("concerns",[]) or []:
        walk(root)
    for leaf in catalog.get("quality_attribute_leaves",[]) or []:
        result.append(leaf["id"])
    return result

def main():
    catalog=load(ROOT/"spec/research/engineering-concerns-v1.yaml")
    proofs=load(ROOT/"spec/research/concern-proof-contract-v1.yaml")
    roles=load(ROOT/"spec/research/authority-role-contract-v1.yaml")

    leaves=set(leaf_ids(catalog))
    proof_map=proofs.get("proofs",{}) or {}
    missing_proof=sorted(leaves-set(proof_map))
    assert not missing_proof, f"leaf concerns without proof contract: {missing_proof}"

    producible=set()
    for spec in (roles.get("roles",{}) or {}).values():
        producible.update(spec.get("can_produce",[]) or [])

    unproducible={}
    for concern,spec in proof_map.items():
        kinds=set(spec.get("accepted_knowledge_kinds",[]) or [])
        if concern in leaves and not (kinds & producible):
            unproducible[concern]=sorted(kinds)
    assert not unproducible, f"proof kinds without producer role: {unproducible}"

    print(f"coverage proof model: ok ({len(leaves)} leaves)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
