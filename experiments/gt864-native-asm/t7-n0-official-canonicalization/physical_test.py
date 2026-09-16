#!/usr/bin/env python3
"""Execute the complete scheduled T7-N0 ToBytes boundary on Apple arm64."""

from __future__ import annotations

import ctypes as ct
import json
import random
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE = HERE / "build/package"
LIBRARY = HERE / "build/t7-n0-tobytes.dylib"


def table(path: Path, name: str) -> list[int]:
    text = path.read_text().split(name, 1)[1].split("=", 1)[1].split(";", 1)[0]
    return list(map(int, re.findall(r"-?\d+", text)))


def oracle(values: list[int], wire: list[int]) -> list[int]:
    result: list[int] = []
    for i in range(0, 864, 2):
        a = values[wire[i]] % 3457
        b = values[wire[i + 1]] % 3457
        result.extend([a & 255, (a >> 8) | ((b & 15) << 4), b >> 4])
    return result


def main() -> None:
    sources = [
        "gt864_tobytes.c", "gt864_tobytes_public.S", "gt864_tobytes_full_core.S",
        "gt864_tobytes_small_core.S", "gt864_pair_merge_full.S", "gt864_pair_merge_small.S",
    ]
    subprocess.run(
        ["clang", "-dynamiclib", "-arch", "arm64", "-O3", "-I", str(PACKAGE),
         *(str(PACKAGE / source) for source in sources), "-o", str(LIBRARY)],
        check=True,
    )
    dll = ct.CDLL(str(LIBRARY))
    wire = table(PACKAGE / "tables.h", "map_f")
    if len(wire) != 864:
        raise AssertionError(len(wire))
    rng = random.Random(0x864070)
    reports = {}
    modes = {
        "full": (dll.gt864_fr0_tobytes_full, -32768, 32767, [-32768, -32767, -3457, -1, 0, 1, 3457, 32767]),
        "small": (dll.gt864_fr0_tobytes_small, -3456, 3456, [-3456, -3023, -1, 0, 1, 3023, 3456]),
    }
    for mode, (function, low, high, edges) in modes.items():
        function.argtypes = [ct.c_void_p, ct.c_void_p]
        function.restype = None
        cases = [[edge] * 864 for edge in edges]
        cases += [list(range(864)), [low if i & 1 else high for i in range(864)]]
        cases += [[rng.randint(low, high) for _ in range(864)] for _ in range(256)]
        for case_number, values in enumerate(cases):
            source = (ct.c_int16 * 866)(0x2222, *values, 0x3333)
            output = (ct.c_uint8 * 1298)(*([0xA5] * 1298))
            before = bytes(source)
            function(ct.byref(output, 1), ct.byref(source, 2))
            if list(output)[1:1297] != oracle(values, wire):
                raise AssertionError((mode, case_number, "wire mismatch"))
            if output[0] != 0xA5 or output[1297] != 0xA5:
                raise AssertionError((mode, case_number, "output canary"))
            if bytes(source) != before:
                raise AssertionError((mode, case_number, "input modified"))
        reports[mode] = {"cases": len(cases), "wire_bytes": 1296, "canaries": True, "input_unchanged": True}
    result = {"gate": "T7-N0", "complete_physical_tobytes": "pass", "reports": reports}
    (HERE / "build/physical-results.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
