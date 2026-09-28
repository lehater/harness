#!/usr/bin/env python3
"""External-process fixture proving live-calibration execution plumbing."""
from __future__ import annotations
import json
import sys

request = json.load(sys.stdin)
cases = request.get("cases", []) if isinstance(request, dict) else []
json.dump(
    {
        "version": 1,
        "kind": "harness-live-semantic-evaluator-response",
        "results": [
            {
                "case_request_id": item["case_request_id"],
                "status": "ACCEPTED",
                "rationale": "transport fixture: accept all",
            }
            for item in cases
        ],
    },
    sys.stdout,
)
