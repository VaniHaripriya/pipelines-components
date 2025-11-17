#!/usr/bin/env python3
"""Validate module-level imports are limited to Python's standard library.

This script enforces the repository’s import guard strategy: third-party or
heavy dependencies must be imported within the function or pipeline body rather
than at module import time.

Usage examples:

    python scripts/check_imports.py components pipelines scripts
    python scripts/check_imports.py --config scripts/import_exceptions.json .

The optional configuration file allows whitelisting specific modules or files:

{
  "modules": ["kfp"],
  "files": {
    "scripts/generate_readme.py": ["jinja2"]
  }
}
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import pkgutil
import sys
import sysconfig
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple


DEFAULT_CONFIG_PATH = Path("scripts/import_exceptions.json")
DEFAULT_REQUIREMENT_FILES = ("dev-requirements.txt", "test-requirements.txt")


class ImportGuardConfig:
    """Holds allow-list data for the import guard."""

    def __init__(
        self,
        module_allowlist: Optional[Iterable[str]] = None,
        file_allowlist: Optional[Dict[str, Iterable[str]]] = None,
    ) -> None:
        """Initialize configuration from module and path allow lists."""
        self.module_allowlist: Set[str] = {canonicalize_module_name(item) for item in module_allowlist or []}
        self.file_allowlist: Dict[Path, Set[str]] = {}
        for raw_path, modules in (file_allowlist or {}).items():
            normalized = Path(raw_path).resolve()
            self.file_allowlist[normalized] = {canonicalize_module_name(mod) for mod in modules}

    @classmethod
    def from_path(cls, path: Path) -> "ImportGuardConfig":
        """Instantiate configuration from a JSON file if it exists."""
        if not path.exists():
            return cls()
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        modules = data.get("modules", [])
        files = data.get("files", {})
        return cls(modules, files)

    def is_allowed(self, module: str, file_path: Path) -> bool:
        """Return True when a module is allow-listed for the given file path."""
        canonical_module = canonicalize_module_name(module)
        if canonical_module in self.module_allowlist:
            return True
        resolved = file_path.resolve()
        for path, modules in self.file_allowlist.items():
            if path == resolved:
                return canonical_module in modules
            if path.is_dir() and path in resolved.parents:
                return canonical_module in modules
        return False


def canonicalize_module_name(name: str) -> str:
    """Return the top-level portion of a dotted module path."""
    return name.split(".")[0]


def discover_python_files(paths: Sequence[str]) -> List[Path]:
    """Collect Python files from individual files or by walking directories."""
    python_files: List[Path] = []
    for raw_path in paths:
        path = Path(raw_path)
        if path.is_file() and path.suffix == ".py":
            python_files.append(path)
        elif path.is_dir():
            for candidate in path.rglob("*.py"):
                if any(part.startswith(".") for part in candidate.parts):
                    continue
                python_files.append(candidate)
    return python_files


def build_stdlib_index() -> Set[str]:
    """Return a set containing names of standard-library modules."""
    candidates: Set[str] = set(sys.builtin_module_names)
    stdlib_path = Path(sysconfig.get_paths()["stdlib"]).resolve()
    for module in pkgutil.walk_packages([str(stdlib_path)]):
        module_name = canonicalize_module_name(module.name)
        candidates.add(module_name)
    return candidates


def extract_top_level_imports(node: ast.AST) -> Iterable[Tuple[str, int]]:
    """Yield (module, line) tuples for top-level import statements."""
    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.Import, ast.ImportFrom)):
            if isinstance(child, ast.ImportFrom) and child.level > 0:
                continue  # relative import is considered safe
            module_name = None
            if isinstance(child, ast.Import):
                if not child.names:
                    continue
                module_name = child.names[0].name
            else:
                if child.module is None:
                    continue
                module_name = child.module
            if module_name:
                yield canonicalize_module_name(module_name), child.lineno
        elif isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            # Imports within functions/classes are intentionally allowed.
            continue
        else:
            yield from extract_top_level_imports(child)


def find_asset_root(path: Path) -> Optional[Path]:
    """Find the nearest directory containing metadata for an asset."""
    for parent in [path] + list(path.parents):
        if (parent / "metadata.yaml").exists():
            return parent
    return None


def ensure_dependency_files(asset_root: Path) -> Optional[str]:
    """Return warning message when dev/test requirement files are absent."""
    for filename in DEFAULT_REQUIREMENT_FILES:
        if (asset_root / filename).exists():
            return None
    return f"{asset_root} is missing a dev/test requirements file " f"({', '.join(DEFAULT_REQUIREMENT_FILES)})"


def check_imports(files: Sequence[Path], config: ImportGuardConfig) -> int:
    """Validate import style across a collection of Python files."""
    stdlib_modules = build_stdlib_index()
    violations: List[str] = []
    dependency_warnings: Set[str] = set()

    for file_path in files:
        try:
            with file_path.open("r", encoding="utf-8") as handle:
                tree = ast.parse(handle.read(), filename=str(file_path))
        except SyntaxError as exc:
            violations.append(f"{file_path}: failed to parse ({exc})")
            continue

        for module_name, lineno in extract_top_level_imports(tree):
            if module_name in stdlib_modules:
                continue
            if config.is_allowed(module_name, file_path):
                asset_root = find_asset_root(file_path.parent)
                if asset_root:
                    warning = ensure_dependency_files(asset_root)
                    if warning:
                        dependency_warnings.add(warning)
                continue
            violations.append(f"{file_path}:{lineno} imports non-stdlib module '{module_name}' at top level")

    for warning in sorted(dependency_warnings):
        print(f"WARNING: {warning}", file=sys.stderr)

    if violations:
        for entry in violations:
            print(entry, file=sys.stderr)
        return 1
    return 0


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Ensure top-level Python imports are limited to the standard library.")
    parser.add_argument(
        "paths",
        nargs="+",
        help="Files or directories to inspect (recursively).",
    )
    parser.add_argument(
        "--config",
        default=str(DEFAULT_CONFIG_PATH),
        help="Path to JSON configuration file with allowed modules/files.",
    )
    return parser.parse_args()


def main() -> int:
    """Run the import guard script."""
    args = parse_args()
    config = ImportGuardConfig.from_path(Path(args.config))
    python_files = discover_python_files(args.paths)
    if not python_files:
        print("No Python files found to inspect.", file=sys.stderr)
        return 0
    return check_imports(python_files, config)


if __name__ == "__main__":
    sys.exit(main())
