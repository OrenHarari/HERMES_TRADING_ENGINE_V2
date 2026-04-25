"""Stage 3 quality gate tests for banned imports and attribute usage."""

from __future__ import annotations

import ast
import os
from pathlib import Path
import tempfile
import textwrap
import unittest


EXCLUDED_DIRS = {
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "env",
    "build",
    "dist",
    "cache",
    "generated",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
}

BANNED_MODULES = {"pandas", "numpy"}


def _iter_python_files(root: Path) -> list[Path]:
    """Return Python files under root while pruning excluded directories."""
    files: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIRS]
        for filename in filenames:
            if filename.endswith(".py"):
                files.append(Path(dirpath) / filename)
    return files


def _quality_gate_violations(root: Path) -> list[str]:
    """AST-only quality gate checks for banned imports and `.values` usage."""
    violations: list[str] = []

    for path in _iter_python_files(root):
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
        display_path = path.relative_to(root)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    top_level = alias.name.split(".", 1)[0]
                    if top_level in BANNED_MODULES:
                        violations.append(
                            f"{display_path}:{node.lineno} uses banned import '{alias.name}'. "
                            f"Remove {top_level} dependency and use standard-library logic."
                        )
            elif isinstance(node, ast.ImportFrom):
                module_name = node.module or ""
                top_level = module_name.split(".", 1)[0] if module_name else ""
                if top_level in BANNED_MODULES:
                    violations.append(
                        f"{display_path}:{node.lineno} uses banned import-from '{module_name}'. "
                        f"Remove {top_level} dependency and use standard-library logic."
                    )
            elif isinstance(node, ast.Attribute) and node.attr == "values":
                violations.append(
                    f"{display_path}:{node.lineno} uses banned '.values'. "
                    "Use explicit standard-library structures instead of `.values`."
                )

    return sorted(violations)


class QualityGateTest(unittest.TestCase):
    def test_repository_currently_passes_quality_gate(self) -> None:
        root = Path(__file__).resolve().parents[1]
        violations = _quality_gate_violations(root)
        self.assertEqual([], violations, "\n".join(violations))

    def test_detects_pandas_import(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "sample.py").write_text("import pandas as pd\n", encoding="utf-8")
            violations = _quality_gate_violations(root)
            self.assertEqual(1, len(violations))
            self.assertIn("banned import 'pandas'", violations[0])

    def test_detects_numpy_import(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "sample.py").write_text("import numpy\n", encoding="utf-8")
            violations = _quality_gate_violations(root)
            self.assertEqual(1, len(violations))
            self.assertIn("banned import 'numpy'", violations[0])

    def test_detects_from_pandas_import(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "sample.py").write_text("from pandas import DataFrame\n", encoding="utf-8")
            violations = _quality_gate_violations(root)
            self.assertEqual(1, len(violations))
            self.assertIn("banned import-from 'pandas'", violations[0])

    def test_detects_from_numpy_import(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "sample.py").write_text("from numpy import array\n", encoding="utf-8")
            violations = _quality_gate_violations(root)
            self.assertEqual(1, len(violations))
            self.assertIn("banned import-from 'numpy'", violations[0])

    def test_detects_values_usage(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "sample.py").write_text(
                textwrap.dedent(
                    """
                    data = {"a": 1}
                    output = data.values
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )
            violations = _quality_gate_violations(root)
            self.assertEqual(1, len(violations))
            self.assertIn("banned '.values'", violations[0])

    def test_ignores_excluded_directories(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".venv").mkdir()
            (root / ".venv" / "bad.py").write_text("import pandas\n", encoding="utf-8")
            (root / "safe.py").write_text("x = 1\n", encoding="utf-8")
            violations = _quality_gate_violations(root)
            self.assertEqual([], violations)


if __name__ == "__main__":
    unittest.main()
