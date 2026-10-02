"""Source-tree package bridge into the canonical src/harness package."""
from pathlib import Path as _Path

__path__ = [str(_Path(__file__).resolve().parents[1] / "src" / "harness")]
