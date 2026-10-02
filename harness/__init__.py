"""Temporary source-tree import bridge; remove when installation owns execution.

Only the canonical src package supplies submodules. No global import path changes.
"""
from pathlib import Path as _Path

__path__ = [str(_Path(__file__).resolve().parents[1] / "src" / "harness")]

from harness.project_model.core import *  # noqa: F403
from harness.project_model.core import __all__
