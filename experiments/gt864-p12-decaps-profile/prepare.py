#!/usr/bin/env python3
"""Freeze the exact current GT864 production package for the P12 profiler."""

from pathlib import Path
import io
import subprocess
import tarfile

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
# P11 (1c790870) changed only this package's roadmap and intentionally left the
# production kernel frozen.  Archive the last production revision so its signed
# source manifest remains internally consistent.
REVISION = "dd8c3146"
CONTROL_REVISION = "1c790870"
PACKAGE = "ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864"

archive = subprocess.check_output(["git", "archive", REVISION, PACKAGE], cwd=REPO)
with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
    for member in tar.getmembers():
        if not member.isfile():
            continue
        destination = HERE / "gt-source" / Path(member.name).relative_to(PACKAGE)
        destination.parent.mkdir(parents=True, exist_ok=True)
        extracted = tar.extractfile(member)
        assert extracted is not None
        destination.write_bytes(extracted.read())

(HERE / "gt-source-revision.json").write_text(
    '{\n  "production_revision": "' + REVISION +
    '",\n  "control_revision": "' + CONTROL_REVISION +
    '",\n  "reason": "P11 changed only the roadmap; production stayed P10/P8"\n}\n'
)
