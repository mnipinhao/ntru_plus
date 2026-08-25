#!/usr/bin/env python3
"""Install one NTRU+ implementation into a SUPERCOP crypto_kem tree."""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


SOURCE_SUFFIXES = {".c", ".s", ".S"}
INCLUDE_RE = re.compile(r'^\s*#\s*include\s+"([^"]+)"', re.MULTILINE)


@dataclass(frozen=True)
class PackageFile:
    source: Path
    destination: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--impl", required=True, type=Path)
    parser.add_argument("--supercop-root", required=True, type=Path)
    parser.add_argument("--scheme", required=True)
    parser.add_argument("--implementation", required=True)
    return parser.parse_args()


def validate_name(value: str, label: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.+-]*", value):
        raise SystemExit(f"invalid {label}: {value!r}")
    return value


def dry_run_sources(impl: Path) -> list[PackageFile]:
    result = subprocess.run(
        ["make", "-n", "test"], cwd=impl, text=True, capture_output=True
    )
    if result.returncode:
        raise SystemExit(result.stdout + result.stderr)
    tokens = (result.stdout + "\n" + result.stderr).replace("\\\n", " ").split()
    sources: list[PackageFile] = []
    for token in tokens:
        candidate = Path(token)
        if candidate.suffix not in SOURCE_SUFFIXES or token == "test/test.c":
            continue
        if token == "randombytes.c":
            continue
        source = (impl / candidate).resolve()
        destination = candidate if ".." not in candidate.parts else Path(candidate.name)
        packaged = PackageFile(source, destination)
        if source.exists() and packaged not in sources:
            sources.append(packaged)
    if not sources:
        raise SystemExit(f"no implementation sources found through make -n test in {impl}")
    return sources


def collect_headers(impl: Path, sources: list[PackageFile]) -> set[PackageFile]:
    pending = list(sources)
    headers: set[PackageFile] = set()
    visited: set[PackageFile] = set()
    while pending:
        packaged = pending.pop()
        if packaged in visited:
            continue
        visited.add(packaged)
        source = packaged.source
        try:
            text = source.read_text()
        except UnicodeDecodeError:
            continue
        for include in INCLUDE_RE.findall(text):
            impl_local = (impl / include).resolve()
            source_local = source.parent / include
            match = impl_local if impl_local.exists() else source_local
            if not match.exists():
                continue
            destination = packaged.destination.parent / include
            header = PackageFile(match.resolve(), destination)
            if header in headers:
                continue
            headers.add(header)
            pending.append(header)
    for required in ("api.h", "params.h", "poly.h", "symmetric.h"):
        path = Path(required)
        if (impl / path).exists():
            headers.add(PackageFile((impl / path).resolve(), path))
    return headers


def copy_file(destination: Path, packaged: PackageFile) -> None:
    target = destination / packaged.destination
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(packaged.source, target)


def main() -> int:
    args = parse_args()
    impl = Path(os.path.abspath(os.fspath(args.impl)))
    supercop_root = Path(os.path.abspath(os.fspath(args.supercop_root)))
    scheme = validate_name(args.scheme, "scheme")
    implementation = validate_name(args.implementation, "implementation")
    if not (impl / "Makefile").is_file():
        raise SystemExit(f"implementation has no Makefile: {impl}")
    if not (supercop_root / "do-part").exists():
        raise SystemExit(f"not a SUPERCOP checkout (missing do-part): {supercop_root}")

    destination = supercop_root / "crypto_kem" / scheme / implementation
    if destination.exists():
        raise SystemExit(f"destination already exists; remove or rename it explicitly: {destination}")

    sources = dry_run_sources(impl)
    headers = collect_headers(impl, sources)
    destination.mkdir(parents=True)
    files = set(sources) | headers
    destinations: dict[Path, Path] = {}
    for packaged in files:
        previous = destinations.setdefault(packaged.destination, packaged.source)
        if previous != packaged.source:
            raise SystemExit(
                f"package path collision: {packaged.destination}: {previous} vs {packaged.source}"
            )
    for packaged in sorted(files, key=lambda item: item.destination.as_posix()):
        copy_file(destination, packaged)

    (destination / "PROVENANCE").write_text(
        f"source={impl}\npackager=bench/supercop/package_impl.py\n"
    )
    print(destination)
    print(f"copied {len(sources)} sources and {len(headers)} headers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
