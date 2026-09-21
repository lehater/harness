#!/usr/bin/env python3
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]

def load(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)

def leaf_ids(catalog):
    out=[]
    def walk(node):
        children=node.get("children",[]) or []
        if children:
            for child in children: walk(child)
        else:
            out.append(node["id"])
    for root in catalog.get("concerns",[]) or []: walk(root)
    for leaf in catalog.get("quality_attribute_leaves",[]) or []:
        out.append(leaf["id"])
    return set(out)

def main():
    catalog=load(ROOT/"spec/research/engineering-concerns-v1.yaml")
    policy=load(ROOT/"spec/research/concern-activation-policy-v1.yaml")
    leaves=leaf_ids(catalog)

    referenced=set(policy.get("baseline",[]) or [])
    ids=set()
    for rule in policy.get("rules",[]) or []:
        rid=rule["id"]
        assert rid not in ids, f"duplicate activation rule: {rid}"
        ids.add(rid)
        referenced.update(rule.get("activate",[]) or [])

    unknown=sorted(referenced-leaves)
    assert not unknown, f"activation policy references non-leaf concerns: {unknown}"
    print(f"concern activation policy: ok ({len(ids)} rules, {len(referenced)} referenced leaves)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
