#!/usr/bin/env python3
"""Consumer API v0 Application compatibility facade."""
from harness.application.coverage_application import *
from harness.application.coverage_application import __all__
from harness.application.coverage_application import main

if __name__ == "__main__":
    raise SystemExit(main())
