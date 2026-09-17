#!/usr/bin/env python3
"""Shared, dependency-free helpers for the pinned SUPERCOP workflow."""

from __future__ import annotations

import hashlib
import os
import shutil
import stat
import tarfile
from pathlib import Path, PurePosixPath


REPO_ROOT = Path(__file__).resolve().parents[1]
LOCK_PATH = REPO_ROOT / "bench" / "supercop.lock"
REQUIRED_LOCK_KEYS = (
    "version",
    "url",
    "archive_sha256",
    "ntruplus864_avx2_tree_sha256",
    "ntruplus1152_avx2_tree_sha256",
)


def read_lock(path: Path = LOCK_PATH) -> dict[str, str]:
    values: dict[str, str] = {}
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ValueError(f"{path}:{number}: expected key=value")
        key, value = line.split("=", 1)
        if not key or not value or key in values:
            raise ValueError(f"{path}:{number}: invalid or duplicate entry")
        values[key] = value
    missing = [key for key in REQUIRED_LOCK_KEYS if key not in values]
    if missing:
        raise ValueError(f"{path}: missing {', '.join(missing)}")
    return values


def write_lock(values: dict[str, str], path: Path = LOCK_PATH) -> None:
    body = (
        "# Pinned production-performance baseline. Update only with\n"
        "# scripts/refresh_supercop_lock.py and review the resulting source hashes.\n"
        + "\n".join(f"{key}={values[key]}" for key in REQUIRED_LOCK_KEYS)
        + "\n"
    )
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(body, encoding="utf-8")
    os.replace(temporary, path)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_tree(root: Path) -> str:
    """Hash relative names, file content hashes, and symlink targets."""
    if not root.is_dir():
        raise ValueError(f"missing tree: {root}")
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            digest.update(f"L\0{relative}\0{os.readlink(path)}\n".encode())
        elif path.is_file():
            digest.update(f"F\0{relative}\0{sha256_file(path)}\n".encode())
    return digest.hexdigest()


def implementation_path(root: Path, parameter: str) -> Path:
    if parameter not in ("864", "1152"):
        raise ValueError(f"unsupported NTRU+ parameter: {parameter}")
    return root / "crypto_kem" / f"ntruplus{parameter}" / "avx2"


def verify_supercop(root: Path, lock: dict[str, str]) -> dict[str, str]:
    root = root.resolve()
    version_file = root / "version"
    if not version_file.is_file():
        raise ValueError(f"not a SUPERCOP tree (missing version): {root}")
    actual_version = version_file.read_text(encoding="utf-8").strip()
    if actual_version != lock["version"]:
        raise ValueError(f"SUPERCOP version mismatch: {actual_version} != {lock['version']}")
    hashes = {}
    for parameter in ("864", "1152"):
        actual = sha256_tree(implementation_path(root, parameter))
        expected = lock[f"ntruplus{parameter}_avx2_tree_sha256"]
        if actual != expected:
            raise ValueError(f"NTRU+{parameter} AVX2 tree mismatch: {actual} != {expected}")
        hashes[parameter] = actual
    return hashes


def safe_extract(archive: Path, destination: Path) -> Path:
    """Extract one SUPERCOP top-level directory without path traversal."""
    destination.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive, "r:*") as bundle:
        members = bundle.getmembers()
        roots = {PurePosixPath(member.name).parts[0] for member in members if member.name}
        if len(roots) != 1:
            raise ValueError("archive must contain exactly one top-level directory")
        destination_abs = destination.resolve()
        for member in members:
            parts = PurePosixPath(member.name).parts
            if member.name.startswith("/") or ".." in parts:
                raise ValueError(f"unsafe archive member: {member.name}")
            target = (destination / member.name).resolve()
            if destination_abs not in (target, *target.parents):
                raise ValueError(f"archive member escapes destination: {member.name}")
        bundle.extractall(destination, members=members, filter="data")
    return destination / next(iter(roots))


def make_read_only(root: Path) -> None:
    for path in [root, *root.rglob("*")]:
        # chmod(..., follow_symlinks=False) is not implemented by every
        # Python/platform combination.  The target of an archive symlink is
        # visited separately when it is inside the pristine tree, so leave
        # the symlink itself alone and make only real files/directories
        # read-only.
        if path.is_symlink():
            continue
        mode = stat.S_IMODE(path.lstat().st_mode)
        path.chmod(mode & ~0o222)


def copy_tree_nonoverwriting(source: Path, destination: Path) -> None:
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(f"refusing to overwrite: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination, symlinks=True)
