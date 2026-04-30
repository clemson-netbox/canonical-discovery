#!/usr/bin/env python3
"""Bump the Poetry version in pyproject.toml."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


VERSION_PATTERN = re.compile(r'^(version\s*=\s*")(?P<version>\d+\.\d+\.\d+)("\s*)$')


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Bump tool.poetry.version in pyproject.toml.",
    )
    parser.add_argument(
        "part",
        choices=("major", "minor", "patch"),
        help="Version component to bump.",
    )
    parser.add_argument(
        "--file",
        default="pyproject.toml",
        help="Path to the pyproject.toml file.",
    )
    return parser.parse_args()


def bump(version: str, part: str) -> str:
    major, minor, patch = (int(piece) for piece in version.split("."))

    if part == "major":
        return f"{major + 1}.0.0"
    if part == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def main() -> int:
    args = parse_args()
    pyproject_path = Path(args.file)

    if not pyproject_path.exists():
        print(f"error: file not found: {pyproject_path}", file=sys.stderr)
        return 1

    lines = pyproject_path.read_text(encoding="utf-8").splitlines()
    updated_lines: list[str] = []
    current_version: str | None = None

    for line in lines:
        match = VERSION_PATTERN.match(line)
        if match is None or current_version is not None:
            updated_lines.append(line)
            continue

        current_version = match.group("version")
        next_version = bump(current_version, args.part)
        updated_lines.append(f'{match.group(1)}{next_version}{match.group(3)}')

    if current_version is None:
        print("error: could not find a version assignment in pyproject.toml", file=sys.stderr)
        return 1

    pyproject_path.write_text("\n".join(updated_lines) + "\n", encoding="utf-8")
    print(f"bumped version: {current_version} -> {next_version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
