#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

from authority_role_projection_experiment import resolve, load

def main() -> int:
    standard=load(str(ROOT/"spec/research/standard-authority-role-bindings-v1.yaml"))
    empty={"version":1,"project":"EXAMPLE","bindings":{}}

    cli=resolve(
        standard, empty,
        [load(str(ROOT/"examples/greenfield-csv-deduplicator/engineering-graph.yaml"))]
    )
    ui=resolve(
        standard, empty,
        [load(str(ROOT/"examples/user-facing-application/engineering-graph.yaml"))]
    )

    assert not cli["unresolved_authorities"], cli["unresolved_authorities"]
    assert not ui["unresolved_authorities"], ui["unresolved_authorities"]
    assert cli["bindings"]["SYSTEM-ARCHITECTURE"] == ["architecture","reliability"]
    assert ui["bindings"]["SECURITY-ARCHITECTURE"] == ["security-architecture"]
    assert ui["bindings"]["QUALITY-DESIGN"] == ["quality"]

    print(f"authority role projection: cli={len(cli['bindings'])} user-facing={len(ui['bindings'])}")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
