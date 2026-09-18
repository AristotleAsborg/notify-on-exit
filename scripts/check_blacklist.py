#!/usr/bin/env python3
"""Fail if rule formulas are hard-coded in the package source.

Real rule content belongs in external configuration, not in the Python code.
This is a literal scan: comments and docstrings count as source too.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PACKAGE_DIRS = (REPO_ROOT / "src" / "notify_on_exit",)

FORBIDDEN_LITERALS = (
    "(STR - 10) // 2",
    "(DEX - 10) // 2",
    "str_mod =",
    "dex_mod =",
)


def iter_python_files():
    for base in PACKAGE_DIRS:
        if base.is_dir():
            yield from sorted(base.rglob("*.py"))


def main() -> int:
    violations = []
    for path in iter_python_files():
        text = path.read_text(encoding="utf-8")
        for needle in FORBIDDEN_LITERALS:
            if needle in text:
                violations.append((path, needle))

    if violations:
        for path, needle in violations:
            print(f"blacklist hit: {path.relative_to(REPO_ROOT)}: {needle!r}")
        return 1

    print("check_blacklist: no hard-coded rule formulas found")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
