#!/usr/bin/env python3
"""Compare Python estimator to the actual pinned C estimator, not another formula."""
import ctypes
import random
import subprocess
import sys
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
from run_encap_live_b3_short import stq

header = Path(sys.argv[1]).resolve()
with tempfile.TemporaryDirectory() as tmp:
    lib = Path(tmp) / "stq.so"
    source = '#include "' + str(header) + '"\nvoid run(double *o,long long *x,long long n){stq_longlong(o,x,n);}\n'
    subprocess.run(["cc", "-shared", "-fPIC", "-O2", "-x", "c", "-", "-o", str(lib)],
                   input=source, text=True, check=True)
    fn = ctypes.CDLL(str(lib)).run
    fn.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_longlong), ctypes.c_longlong]
    rng = random.Random(768)
    for n in [1,2,3,4,5,7,16,63,64,96,192,864]:
        for _ in range(20):
            values = [rng.randrange(-100000, 100000) for _ in range(n)]
            out = (ctypes.c_double * 3)()
            fn(out, (ctypes.c_longlong * n)(*values), n)
            assert list(out) == stq(values), (n, list(out), stq(values))
    try:
        stq([])
        raise AssertionError("empty accepted")
    except ValueError:
        pass
print("PASS: 240 datasets match pinned C stq_longlong")
