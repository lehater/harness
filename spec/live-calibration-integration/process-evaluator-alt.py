#!/usr/bin/env python3
"""Second external-process fixture with intentionally different executable bytes."""
from __future__ import annotations
import json
import sys

payload = json.load(sys.stdin)
json.dump(
    {
        "version": 1,
        "kind": "harness-live-semantic-evaluator-response",
        "results": [
            {"case_request_id": case["case_request_id"], "status": "ACCEPTED"}
            for case in payload.get("cases", [])
        ],
    },
    sys.stdout,
)
