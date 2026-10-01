#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import os
import sys
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--mode", default="pass")
args = parser.parse_args()
if args.mode == "fail":
    print("synthetic infrastructure failure", file=sys.stderr)
    raise SystemExit(3)
if args.mode == "malformed":
    print("not-json")
    raise SystemExit(0)

request = json.load(sys.stdin)
if args.mode == "reasoning":
    response = {"version": 1, "kind": "harness-agent-behavioral-eval-response", "run_status": "COMPLETED", "reasoning": "forbidden"}
elif args.mode == "incomplete":
    response = {"version": 1, "kind": "harness-agent-behavioral-eval-response", "run_status": "INCOMPLETE", "execution_findings": [{"code": "STUB_INCOMPLETE"}]}
else:
    assert "oracle_ref" not in request
    assert "pass_criteria" not in request
    assert "previous_runs" not in request
    response = {
        "version": 1,
        "kind": "harness-agent-behavioral-eval-response",
        "run_status": "COMPLETED",
        "output": {"capabilities": [{"name": "free wording", "support_atoms": ["E2", "E1"]}]},
        "trace": [{"event": "observable-environment", "isolated_cwd": Path.cwd().name == "work", "home_isolated": Path(os.environ["HOME"]).name == "home"}],
        "provenance": {"provider": "deterministic-stub", "model": "deterministic-stub"},
    }
json.dump(response, sys.stdout)
sys.stdout.write("\n")
