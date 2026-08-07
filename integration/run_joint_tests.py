"""Joint-test entry point: python integration/run_joint_tests.py

Wires the real implementations of all three repositories together. The consumer
sources are located through environment variables so a caller can point them at
any candidate revision:

    CHECKOUT_SRC=/path/to/repomesh-e2e-checkout/src
    BILLING_SRC=/path/to/repomesh-e2e-billing/src

RepoMesh fills these in from a ValidationSnapshot's candidate refs.
"""

import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _consumer_source(variable: str, fallback: Path) -> Path:
    configured = os.environ.get(variable, "").strip()
    path = Path(configured) if configured else fallback
    if not path.is_dir():
        raise SystemExit(
            f"{variable} must point at an existing source directory (looked at {path})"
        )
    return path


if __name__ == "__main__":
    siblings = ROOT.parent
    checkout_src = _consumer_source("CHECKOUT_SRC", siblings / "repomesh-e2e-checkout" / "src")
    billing_src = _consumer_source("BILLING_SRC", siblings / "repomesh-e2e-billing" / "src")

    sys.path.insert(0, str(ROOT / "src"))
    sys.path.insert(0, str(checkout_src))
    sys.path.insert(0, str(billing_src))

    print(f"pricing-core src : {ROOT / 'src'}")
    print(f"checkout src     : {checkout_src}")
    print(f"billing src      : {billing_src}")

    suite = unittest.defaultTestLoader.discover(str(ROOT / "integration"), pattern="test_*.py")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
