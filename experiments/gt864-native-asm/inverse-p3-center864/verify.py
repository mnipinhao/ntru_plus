#!/usr/bin/env python3
"""Differential and memory-boundary checks for center864."""

import ctypes
import random
import subprocess
import tempfile
from pathlib import Path


P = Path(__file__).resolve().parent
Q = 3457
HALFQ = 1728
N = 864
CANARY = -12345


def centered(value: int) -> int:
    residue = value % Q
    return residue - Q if residue > HALFQ else residue


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="gt864-center-") as tmp:
        library = Path(tmp) / "center864.dylib"
        subprocess.run(
            ["clang", "-O3", "-dynamiclib", str(P / "candidate.opt.S"), "-o", str(library)],
            check=True,
        )
        function = ctypes.CDLL(str(library)).center864
        function.argtypes = [ctypes.POINTER(ctypes.c_int16)]
        function.restype = None

        def check(values: list[int]) -> None:
            assert len(values) == N
            storage = (ctypes.c_int16 * (N + 4))()
            storage[0] = storage[1] = storage[N + 2] = storage[N + 3] = CANARY
            for index, value in enumerate(values):
                storage[index + 2] = value
            pointer = ctypes.cast(ctypes.byref(storage, 4), ctypes.POINTER(ctypes.c_int16))
            function(pointer)
            got = list(storage)[2 : N + 2]
            expected = [centered(value) for value in values]
            assert got == expected, next(
                (index, values[index], got[index], expected[index])
                for index in range(N)
                if got[index] != expected[index]
            )
            assert [storage[0], storage[1], storage[N + 2], storage[N + 3]] == [CANARY] * 4

        # Cover every integer in the proven producer range, including endpoints.
        exhaustive = list(range(-6912, 6913))
        for offset in range(0, len(exhaustive), N):
            block = exhaustive[offset : offset + N]
            block += [0] * (N - len(block))
            check(block)

        rng = random.Random(0x864C3)
        for _ in range(4096):
            check([rng.randint(-6912, 6912) for _ in range(N)])
        print("center864 differential: PASS")
        print("exhaustive scalar values: 13825")
        print("random 864-coefficient vectors: 4096")
        print("input/output canaries: PASS")


if __name__ == "__main__":
    main()
