import ast
import shutil
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
FORBIDDEN_IMPORTS = {"pandas", "numpy"}
EXCLUDED_DIRS = {
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "env",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "build",
    "dist",
    "node_modules",
    "generated",
    "cache",
}


def _iter_python_files(root: Path):
    for path in root.rglob("*.py"):
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        yield path


def _scan_python_file(path: Path) -> list[str]:
    violations: list[str] = []
    source = path.read_text(encoding="utf-8")

    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        raise AssertionError(f"Cannot parse Python file '{path}': {exc}") from exc

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root_name = alias.name.split(".")[0]
                if root_name in FORBIDDEN_IMPORTS:
                    violations.append(
                        f"{path}: forbidden import '{root_name}' at line {node.lineno}."
                    )
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                root_name = node.module.split(".")[0]
                if root_name in FORBIDDEN_IMPORTS:
                    violations.append(
                        f"{path}: forbidden import-from '{root_name}' at line {node.lineno}."
                    )
        elif isinstance(node, ast.Attribute):
            if node.attr == "values":
                violations.append(f"{path}: forbidden '.values' usage at line {node.lineno}.")

    return violations


def _scan_non_python_file(path: Path) -> list[str]:
    """Fallback text scan for non-Python files when AST is not suitable."""
    violations: list[str] = []
    content = path.read_text(encoding="utf-8")

    if ".values" in content:
        violations.append(f"{path}: forbidden '.values' usage found in text content.")

    return violations


def find_quality_gate_violations(root: Path) -> list[str]:
    violations: list[str] = []

    for py_file in _iter_python_files(root):
        violations.extend(_scan_python_file(py_file))

    return violations


class TestQualityGate(unittest.TestCase):
    def test_repository_has_no_forbidden_patterns(self) -> None:
        violations = find_quality_gate_violations(PROJECT_ROOT)
        self.assertEqual(
            violations,
            [],
            "Quality gate violations found:\n" + "\n".join(violations),
        )

    def test_detects_forbidden_imports_and_values_usage(self) -> None:
        temp_dir = Path(tempfile.mkdtemp(prefix="quality_gate_"))
        self.addCleanup(lambda: shutil.rmtree(temp_dir, ignore_errors=True))

        probe = temp_dir / "probe.py"
        probe.write_text(
            "import pandas\nimport numpy as np\nclass X:\n    def f(self):\n        return self.values\n",
            encoding="utf-8",
        )

        violations = find_quality_gate_violations(temp_dir)
        joined = "\n".join(violations)
        self.assertIn("forbidden import 'pandas'", joined)
        self.assertIn("forbidden import 'numpy'", joined)
        self.assertIn("forbidden '.values' usage", joined)

    def test_excluded_directories_are_not_scanned(self) -> None:
        temp_dir = Path(tempfile.mkdtemp(prefix="quality_gate_excluded_"))
        self.addCleanup(lambda: shutil.rmtree(temp_dir, ignore_errors=True))

        excluded_path = temp_dir / "__pycache__"
        excluded_path.mkdir(parents=True, exist_ok=True)
        hidden_violation = excluded_path / "hidden.py"
        hidden_violation.write_text("import pandas\n", encoding="utf-8")

        violations = find_quality_gate_violations(temp_dir)
        self.assertEqual(violations, [])

    def test_plain_text_fallback_for_non_python_files(self) -> None:
        temp_dir = Path(tempfile.mkdtemp(prefix="quality_gate_fallback_"))
        self.addCleanup(lambda: shutil.rmtree(temp_dir, ignore_errors=True))

        probe = temp_dir / "notes.txt"
        probe.write_text("this contains .values usage", encoding="utf-8")

        violations = _scan_non_python_file(probe)
        self.assertEqual(len(violations), 1)
        self.assertIn("forbidden '.values' usage", violations[0])
