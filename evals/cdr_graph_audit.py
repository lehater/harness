"""On-demand, read-only CDR structural graph audit.

Structural reachability cannot prove a semantic prerequisite redundant. Run
separately from Capability creation; no recursive full-graph audit on each
new Capability, and never a graph edit.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict, deque
from pathlib import Path
from typing import Any

from evals.project_discovery_snapshot import DiscoveryError, _commit
from evals.cdr_operational import _producers


def audit_graph(root: Path, *, sha: str) -> dict[str, Any]:
    root=root.resolve()
    _commit(root,sha)
    producers=_producers(root)
    if len(producers)>5000:
        raise DiscoveryError("explicit audit bound exceeded: over 5000 Capabilities")
    adjacency={cid:sorted(x["capability"] for x in v["requires"])
               for cid,v in producers.items()}
    missing=sorted({
        (cid,target) for cid,needs in adjacency.items() for target in needs
        if target not in producers
    })
    self_links=sorted(cid for cid,needs in adjacency.items() if cid in needs)
    state={}
    stack=[]
    cycles=set()
    def visit(start: str) -> None:
        # Iterative DFS prevents recursion failures on large authority graphs.
        frames=[(start,iter(adjacency[start]))]
        state[start]=1
        stack.append(start)
        while frames:
            current,it=frames[-1]
            try:other=next(it)
            except StopIteration:
                frames.pop()
                stack.pop()
                state[current]=2
                continue
            if other not in adjacency:continue
            if state.get(other)==1:
                idx=stack.index(other)
                cyc=stack[idx:]+[other]
                cycles.add(tuple(cyc))
            elif state.get(other) is None:
                state[other]=1
                stack.append(other)
                frames.append((other,iter(adjacency[other])))
    for cid in sorted(producers):
        if cid not in state:
            visit(cid)

    def path(start: str, goal: str) -> list[str] | None:
        seen={start}
        q=deque([[start]])
        while q:
            seq=q.popleft()
            if seq[-1]==goal:return seq
            for nxt in adjacency.get(seq[-1],()):
                if nxt not in seen and nxt in adjacency:
                    seen.add(nxt)
                    q.append(seq+[nxt])
        return None

    shadow=[]
    for cid in sorted(adjacency):
        needs=adjacency[cid]
        for goal in needs:
            paths=[]
            for other in needs:
                if other==goal:continue
                candidate=path(other,goal)
                if candidate is not None:
                    paths.append([cid]+candidate)
            if paths:
                shadow.append({
                    "target_capability":cid,
                    "direct_provider":goal,
                    "alternative_structural_paths":paths,
                    "status":"TRANSITIVE_REACHABILITY_ONLY",
                    "semantic_redundancy_proven":False,
                    "remove_candidate_allowed":False,
                    "review_question":(
                        "Does an accepted immediate intermediate contract "
                        "fully discharge the target's unique semantic need?"
                    ),
                })
    reverse=defaultdict(set)
    for cid,needs in adjacency.items():
        for v in needs:
            if v in adjacency:reverse[v].add(cid)
    impacts=[]
    for cid in sorted(producers):
        seen={cid}
        q=deque([(cid,0)])
        level={}
        while q:
            node,depth=q.popleft()
            for dependent in sorted(reverse[node]):
                if dependent not in seen:
                    seen.add(dependent)
                    level[dependent]=depth+1
                    q.append((dependent,depth+1))
        impacts.append({
            "changed_provider":cid,
            "direct_consumers":sorted(reverse[cid]),
            "potential_transitive_consumers":sorted(level),
            "impact_is_structural_not_semantic":True,
        })
    return {
        "kind":"harness-cdr-readonly-graph-audit-v1",
        "source_snapshot":sha,
        "status":"INVALID_STRUCTURE_REQUIRES_REVIEW" if missing or cycles or self_links
                 else "STRUCTURAL_REVIEW_ONLY",
        "capability_count":len(producers),
        "direct_edge_count":sum(map(len,adjacency.values())),
        "unknown_provider_edges":[{"consumer":c,"provider":p} for c,p in missing],
        "self_dependencies":self_links,
        "cycles":[list(c) for c in sorted(cycles)],
        "structural_transitive_edge_flags":shadow,
        "change_impact":impacts,
        "missing_semantic_edges_exhaustively_detected":False,
        "semantic_redundancy_verified":False,
        "REMOVE_CANDIDATE":[],
        "automatic_writeback_allowed":False,
    }


def main() -> int:
    p=argparse.ArgumentParser(description="Read-only pinned Engineering Graph audit")
    p.add_argument("--project-root",type=Path,required=True)
    p.add_argument("--commit",required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    try:
        result=audit_graph(args.project_root,sha=args.commit)
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        print(json.dumps({
            "status":result["status"],
            "capabilities":result["capability_count"],
            "edges":result["direct_edge_count"],
            "transitively_reachable_direct_edges":len(result["structural_transitive_edge_flags"]),
            "unknown_sources":len(result["unknown_provider_edges"]),
            "cycles":len(result["cycles"]),
            "automatic_writeback_allowed":False,
        }))
        return 0 if result["status"]=="STRUCTURAL_REVIEW_ONLY" else 2
    except (DiscoveryError,ValueError,TypeError,KeyError,OSError) as e:
        print(json.dumps({"status":"INVALID","error":str(e)},ensure_ascii=False))
        return 2

if __name__=="__main__":
    raise SystemExit(main())
