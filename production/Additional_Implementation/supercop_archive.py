#!/usr/bin/env python3
"""Write this repository's SUPERCOP leaves into one archive.

    python3 supercop_archive.py OUTPUT.zip       (or OUTPUT.tar.gz)

The archive holds crypto_kem/ntruplus{768,864,1152}/avx2-opt and
crypto_kem/ntruplus{768,864,1152}/aarch64-opt, each written by its package's
scripts/export_supercop.py, and unpacks over a SUPERCOP tree.  Entries are
sorted, with fixed timestamps and modes, so the same sources give the same
archive.  Run it on Linux/AArch64 with GCC: NTRU+768's AArch64 exporter
compiles its sources to find the symbols it namespaces.  Run make check in the
six packages first.
"""
import gzip
import hashlib
import io
import platform
import subprocess
import sys
import tarfile
import tempfile
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
LEAVES = [(HERE / arch / f"NTRU+{n}", f"crypto_kem/ntruplus{n}/{name}")
          for n in ("768", "864", "1152")
          for arch, name in (("avx2", "avx2-opt"), ("aarch64", "aarch64-opt"))]


def export(stage, leaves):
    """Run each package's exporter into stage and return the leaves' files."""
    for package, leaf in leaves:
        dest = stage / leaf
        dest.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run([sys.executable, "scripts/export_supercop.py", str(dest)],
                       cwd=package, check=True, stdout=subprocess.DEVNULL)
    # The exporters write their metadata beside each leaf; only the leaves go in.
    files = [p for _, leaf in leaves for p in (stage / leaf).rglob("*") if p.is_file()]
    return sorted(files, key=lambda p: p.relative_to(stage).as_posix())


def write_archive(out, stage, files):
    entries = [(p.relative_to(stage).as_posix(), p.read_bytes()) for p in files]
    if out.name.endswith(".zip"):
        with zipfile.ZipFile(out, "x") as archive:
            for name, data in entries:
                info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                info.external_attr = 0o644 << 16
                info.compress_type = zipfile.ZIP_DEFLATED
                archive.writestr(info, data)
    else:
        with open(out, "xb") as raw, \
             gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed, \
             tarfile.open(fileobj=compressed, mode="w", format=tarfile.USTAR_FORMAT) as archive:
            for name, data in entries:
                info = tarfile.TarInfo(name)
                info.size, info.mode, info.mtime = len(data), 0o644, 0
                archive.addfile(info, io.BytesIO(data))


def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    out = Path(sys.argv[1]).resolve()
    if not out.name.endswith((".zip", ".tar.gz")):
        raise SystemExit("OUTPUT must end in .zip or .tar.gz")
    if out.exists():
        raise SystemExit(f"{out} exists; choose a fresh path")
    if (platform.system(), platform.machine()) != ("Linux", "aarch64"):
        raise SystemExit("run on Linux/AArch64: NTRU+768's AArch64 exporter needs its GCC")
    with tempfile.TemporaryDirectory(prefix="ntruplus-supercop-") as tmp:
        stage = Path(tmp)
        files = export(stage, LEAVES)
        write_archive(out, stage, files)
    digest = hashlib.sha256(out.read_bytes()).hexdigest()
    print(f"{out}: {len(files)} files in {len(LEAVES)} leaves, sha256 {digest}")


if __name__ == "__main__":
    main()
