"""Empirical cross-check of the analytic degree-4 bounds.

Instruments the G1 declared oracle and runs complete KEM operations, recording
the extremes actually reached by every montgomery_reduce accumulator and by
each leaf kernel's inputs and outputs.

This is a necessary, not sufficient, condition: an observed maximum below the
analytic bound supports the derivation, and an observed maximum *above* it
falsifies it outright.  bounds.py is what proves; this is what catches a
derivation written down wrong.
"""

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "experiments/gt1152-p01-ring-profile"))

import ntruplus1152 as P  # noqa: E402
from nistkat import CtrDrbg  # noqa: E402


class Tracker:
    def __init__(self):
        self.data = {}

    def observe(self, key, *values):
        lo, hi = self.data.get(key, (None, None))
        for v in values:
            lo = v if lo is None or v < lo else lo
            hi = v if hi is None or v > hi else hi
        self.data[key] = (lo, hi)

    def report(self):
        return {k: {"lo": v[0], "hi": v[1], "abs_max": max(abs(v[0]), abs(v[1]))}
                for k, v in sorted(self.data.items())}


T = Tracker()


def install():
    """Wrap the oracle's primitives so every call is recorded."""
    mont = P.montgomery_reduce

    def traced_mont(a):
        out = mont(a)
        T.observe("montgomery_reduce/input", a)
        T.observe("montgomery_reduce/output", out)
        return out

    P.montgomery_reduce = traced_mont

    for name in ("basemul", "basemul_add", "baseinv"):
        original = getattr(P, name)

        def wrap(original=original, name=name):
            def traced(*args):
                # Leading positional args are coefficient vectors; the trailing
                # one is the leaf zeta.
                for i, arg in enumerate(args[:-1]):
                    T.observe(f"{name}/in{i}", *arg)
                T.observe(f"{name}/zeta", args[-1])
                out = original(*args)
                vec = out[1] if name == "baseinv" else out
                T.observe(f"{name}/out", *vec)
                return out
            return traced

        setattr(P, name, wrap())

    # The module-level poly_* helpers captured the originals at import time.
    for poly_name, leaf in (("poly_basemul", "basemul"),
                            ("poly_basemul_add", "basemul_add"),
                            ("poly_baseinv", "baseinv")):
        src = getattr(P, poly_name)
        src.__globals__[leaf] = getattr(P, leaf)
    P.poly_basemul.__globals__["montgomery_reduce"] = P.montgomery_reduce


def run(iterations):
    install()
    rng = CtrDrbg(bytes(range(48)))
    for i in range(iterations):
        pk, sk = P.crypto_kem_keypair(rng)
        ct, ss = P.crypto_kem_enc(pk, rng)
        fail, ss_dec = P.crypto_kem_dec(ct, sk)
        if fail or ss_dec != ss:
            raise SystemExit(f"KEM round trip failed at iteration {i}")
        print(f"  iteration {i} ok", flush=True)

    observed = T.report()
    analytic = json.loads((HERE / "bounds-report.json").read_text())

    # The decapsulation first product is the widest documented case; compare the
    # observed leaf-kernel outputs against the widest analytic domain.
    widest = max(
        analytic["results"][d][k]["abs_max"]
        for d in analytic["results"] for k in ("basemul", "basemul_add")
    )
    checks = []

    def expect(key, bound, note):
        got = observed.get(key)
        if got is None:
            checks.append({"key": key, "status": "not_observed", "note": note})
            return
        ok = got["abs_max"] <= bound
        checks.append({"key": key, "observed_abs_max": got["abs_max"],
                       "analytic_bound": bound, "within": ok, "note": note})
        print(f"[{'pass' if ok else 'FAIL'}] {key}: observed {got['abs_max']} "
              f"<= analytic {bound}  ({note})")

    expect("basemul/out", widest, "widest analytic basemul/basemul_add bound")
    expect("basemul_add/out", widest, "widest analytic basemul/basemul_add bound")
    expect("baseinv/out", max(analytic["results"][d]["baseinv"]["abs_max_out"]
                              for d in analytic["results"]),
           "widest analytic baseinv bound")
    expect("montgomery_reduce/output", 32767, "must fit int16")
    expect("montgomery_reduce/input", (1 << 31) - 1, "must fit int32")

    report = {
        "iterations": iterations,
        "observed": observed,
        "checks": checks,
        "pass": all(c.get("within", True) for c in checks),
    }
    (HERE / "empirical-report.json").write_text(json.dumps(report, indent=2) + "\n")

    print("\nobserved extremes:")
    for key, v in observed.items():
        print(f"  {key:32s} [{v['lo']:12d}, {v['hi']:12d}]  |.| <= {v['abs_max']}")

    if not report["pass"]:
        print("\nFAIL: an observed value exceeds its analytic bound", file=sys.stderr)
        return 1
    print("\nPASS -> empirical-report.json")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, default=3)
    args = parser.parse_args()
    raise SystemExit(run(args.iterations))
