#!/usr/bin/env python3
"""No-network tests: pinned reviewed Core discovery and oracle-free process runner."""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from evals.project_discovery_snapshot import DiscoveryError, generate
from evals.project_discovery_reconcile import compare
from harness.application.scenario_suite import load_driver_modules, run_scenario
from evals.dependency_resolution_process_driver import (
    build_blinded_request, _validate_discovery_inputs,
    execute_dependency_resolution_process, EXECUTABLE_ENV,
)

CONFIG = ROOT / "spec/dependency-resolution/project-pilots/prep-mvp-v1.yaml"
pilot = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))
assert len(pilot["targets"]) == 2
assert pilot["project_commit"] == "c52ff8ec1a4732285b2b299bf11dca9869fb2fee"


def put(root: Path, relative: str, value: str) -> None:
    p = root / relative
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(value, encoding="utf-8")


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(root), *args], text=True,
        stderr=subprocess.DEVNULL,
    ).strip()


with tempfile.TemporaryDirectory(prefix="harness-cdr-project-snapshot-") as tmp:
    base = Path(tmp)
    git(base, "init")
    git(base, "config", "user.name", "CDR Test")
    git(base, "config", "user.email", "cdr@example.invalid")

    put(base, ".harness/core.yaml", yaml.safe_dump({
        "authorities": [{"id": "PRODUCT"}, {"id": "MODEL-CONTEXT"}, {"id": "TACTICAL"}],
        "artifacts": [
            {"id": "POLICY", "authority": "PRODUCT", "path": "docs/product.yaml",
             "provides": ["x.accepted-policy"], "depends_on": []},
            {"id": "STRATEGY", "authority": "MODEL-CONTEXT", "path": "docs/context.md",
             "provides": ["x.strategy"], "depends_on": ["POLICY"]},
            {"id": "UNREVIEWED", "authority": "PRODUCT", "path": "docs/unreviewed.yaml",
             "provides": ["x.unreviewed"], "depends_on": []},
        ],
        "questions": [],
    }, sort_keys=False))
    put(base, ".harness/engineering-graph.yaml", yaml.safe_dump({
        "authorities": [
            {"id": "PRODUCT", "produces": [
                {"capability": "x.accepted-policy", "knowledge_kind": "product-requirements", "requires": []},
                {"capability": "x.unreviewed", "knowledge_kind": "product-requirements", "requires": []},
            ]},
            {"id": "MODEL-CONTEXT", "produces": [
                {"capability": "x.strategy", "knowledge_kind": "model-context", "requires": [{"capability": "x.accepted-policy"}]},
            ]},
            {"id": "TACTICAL", "responsibility": "Define scoped accepted model concepts",
             "produces": [{"capability": "x.target-domain", "knowledge_kind": "domain-model",
                           "requires": [{"capability": "x.accepted-policy"}]}]},
        ],
    }, sort_keys=False))
    put(base, ".harness/semantic-baseline.yaml", yaml.safe_dump({
        "reviews": [
            {"capability": "x.accepted-policy", "revision": 1},
            {"capability": "x.strategy", "revision": 2},
        ],
    }, sort_keys=False))
    put(base, "docs/product.yaml", yaml.safe_dump({
        "content": {"requirements": [
            {"id": "REQ-01", "statement": "An approved actor must be verified before acting.", "status": "ACCEPTED"},
            {"id": "REQ-02", "statement": "Unaccepted draft authorization must never govern execution.", "status": "DRAFT"},
        ]},
    }, sort_keys=False))
    put(base, "docs/unreviewed.yaml", yaml.safe_dump({"content": {"requirements": [
        {"id": "REQ-03", "statement": "Unreviewed account deletion contract.", "status": "ACCEPTED"}
    ]}}, sort_keys=False))
    put(base, "docs/context.md", (
        "# Strategy\n\n## MC-01 Business Scope\n\n"
        "Own accepted meanings of accounts and customer operations.\n\n"
        "- Keep actions distinct from activity history.\n\n"
        "## MC-02 Not Part Of Scope\n\nUnrelated billing language.\n"
    ))
    put(base, "docs/future-unregistered.md", "# Future\nUnregistered rules do not count.")

    git(base, "add", ".")
    git(base, "commit", "-m", "pinned fixture")
    sha = git(base, "rev-parse", "HEAD")
    targets = [{
        "capability": "x.target-domain", "scope_source": "docs/context.md",
        "scope_headings": ["MC-01 Business Scope"],
    }]
    inputs = generate(base, sha=sha, targets=targets)
    assert inputs["source_snapshot"] == sha
    assert inputs["evidence_contract"] == "source-grounded-v1"
    assert len(inputs["cases"]) == 1
    case = inputs["cases"][0]
    providers = {x["capability"]: x for x in case["provider_catalog"]}
    assert set(providers) == {"x.strategy", "x.accepted-policy"}
    assert providers["x.strategy"]["review_revision"] == 2
    assert len(providers["x.accepted-policy"]["semantic_surface"]) == 1
    assert "REQ-01" in providers["x.accepted-policy"]["semantic_surface"][0]
    assert "REQ-02" not in repr(providers)
    assert "x.unreviewed" not in repr(inputs)
    assert "Unrelated billing" not in case["target"]["output_obligations"][0]["description"]
    assert "Keep actions distinct" in case["target"]["output_obligations"][0]["description"]
    assert "requires" not in repr(case["target"])
    assert "baseline_requires" not in repr(inputs)
    _validate_discovery_inputs(inputs)

    bind = build_blinded_request(inputs, run_id="REAL-SNAPSHOT-SMOKE", adapter_binding={"id": "fake"})
    assert bind["cases"][0]["target"]["capability"] == "x.target-domain"
    assert "x.accepted-policy" in repr(bind)
    assert "baseline_requires" not in repr(bind)

    try:
        generate(base, sha="0" * 40, targets=targets)
    except DiscoveryError:
        pass
    else:
        raise AssertionError("must reject mismatched project snapshot")
    put(base, "docs/context.md", (base / "docs/context.md").read_text() + "\nAdded without commit.\n")
    try:
        generate(base, sha=sha, targets=targets)
    except DiscoveryError:
        pass
    else:
        raise AssertionError("must reject dirty tracked project files")
    git(base, "checkout", "--", "docs/context.md")

    # Fake model supplies syntactically grounded real-project predictions.
    script = base / "fake_provider.py"
    script.write_text(
        "#!/usr/bin/env python3\n"
        "import json, sys\n"
        "x = json.load(sys.stdin)\n"
        "out=[]\n"
        "for c in x['cases']:\n"
        "  p=c['provider_catalog'][0]['capability']\n"
        "  ob=c['target']['output_obligations'][0]['id']\n"
        "  out.append(dict(case_request_id=c['case_request_id'],status='RESOLVED',"
        "proposed_requires=[p],unresolved_obligations=[],input_needs=[dict("
        "obligation=ob,provider=p,claim_index=0,basis='DIRECT_ACCEPTED',"
        "consumption_rationale='This directly constrains the scoped model output.')]))\n"
        "print(json.dumps(dict(version=1,kind='harness-dependency-resolution-evaluator-response',"
        "request_id=x['request_id'],results=out,provenance=dict(provider='github-copilot'))))\n",
        encoding="utf-8",
    )
    previous = os.environ.get(EXECUTABLE_ENV)
    os.environ[EXECUTABLE_ENV] = str(script)
    try:
        evaluation = execute_dependency_resolution_process(
            inputs=inputs, run_id="REAL-SNAPSHOT-NO-ORACLE"
        )
        assert evaluation["status"] == "DISCOVERY_REQUIRES_REVIEW", evaluation
        assert evaluation["calibration_claim"] == "NOT_APPLICABLE_NO_ORACLE"
        assert evaluation["edge_comparison"] is None
        assert evaluation["automatic_writeback_allowed"] is False
        assert evaluation["source_snapshot"] == sha
        assert evaluation["bound_predictions"]["cases"][0]["proposed_requires"]
        assert evaluation["evidence_assessment"]["semantic_entailment_verified"] is False
        assert evaluation["oracle_is_expert_validated"] is False

        # Exercise the checked-in oracle-free template through Scenario Suite
        # (fake process only); this tests fixture paths and scenario wiring.
        smoke = base / "smoke-project-pilot"
        scripts = smoke / "scenarios"
        scripts.mkdir(parents=True)
        (smoke / "generated-prep-discovery.yaml").write_text(
            yaml.safe_dump(inputs, sort_keys=False), encoding="utf-8"
        )
        original = (ROOT / "spec/dependency-resolution/project-pilots/scenarios/"
                    "prep-discovery-run.yaml.tmpl").read_text(encoding="utf-8")
        scenario_file = scripts / "run.yaml"
        scenario_file.write_text(
            original.replace("__RUN_ID__", "SCENARIO-REAL-PROJECT-SMOKE"),
            encoding="utf-8"
        )
        load_driver_modules(["evals.dependency_resolution_process_driver"])
        scenario_result = run_scenario(scenario_file)
        assert scenario_result.status == "PASSED", scenario_result.as_dict()

        # Phase B is intentionally separate and begins only after the blinded
        # model result and its valid reference assessment exist.
        comparison = compare(base, sha=sha, inputs=inputs, evaluation=evaluation)
        assert comparison["status"] == "READ_ONLY_RECONCILIATION"
        assert comparison["automatic_writeback_allowed"] is False
        assert comparison["cases"][0]["KEEP"] == ["x.accepted-policy"]
        assert comparison["cases"][0]["ADD"] == []
        assert comparison["cases"][0]["REMOVE_CANDIDATE"] == []

        broken = copy.deepcopy(evaluation)
        broken["source_snapshot"] = "0" * 40
        try:
            compare(base, sha=sha, inputs=inputs, evaluation=broken)
        except DiscoveryError:
            pass
        else:
            raise AssertionError("Phase B must reject wrong project snapshot")

        broken = copy.deepcopy(evaluation)
        broken["evidence_assessment"]["status"] = "INVALID"
        try:
            compare(base, sha=sha, inputs=inputs, evaluation=broken)
        except DiscoveryError:
            pass
        else:
            raise AssertionError("Phase B must recompute proof references")
    finally:
        if previous is None:
            os.environ.pop(EXECUTABLE_ENV, None)
        else:
            os.environ[EXECUTABLE_ENV] = previous

print("dependency resolution pinned project discovery: PASS")
