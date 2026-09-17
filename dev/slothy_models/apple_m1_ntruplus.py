"""Fill the seven gaps in SLOTHY's Apple M1 models, from published Firestorm data.

`scripts/instruction_coverage.py` showed that both M1 models cover every
instruction NTRU+1152's kernels use except seven classes: the six signed
widening multiply-accumulate forms and `subs_imm`.  Running `make
apple_m1_firestorm` fails on the first `smull`.

The numbers below are **not guessed and not measured here**.  Two independent
things fix them:

1. The models already carry `vumull` and `vumlal` -- the *unsigned* widening
   forms -- at `ExecutionUnit.V()`, inverse throughput 1, latency 3.  The signed
   forms are simply absent, not different.

2. Dougall Johnson's reverse-engineered Firestorm tables
   (https://dougallj.github.io/applecpu/firestorm-simd.html) give, for the
   4S variants:

       SMULL / SMULL2 / SMLAL / SMLAL2 / SMLSL / SMLSL2   LAT 3  TP 0.25  u11-14
       MUL (vector, 8H)                                   LAT 3  TP 0.25  u11-14
       UZP1 / ADD / SUB / AND / CMGT                       LAT 2  TP 0.25  u11-14

   `u11-14` is the four vector pipes, which the model numbers `VEC0`-`VEC3`, so
   TP 0.25 is one pipe for one cycle: inverse throughput 1.  That is exactly the
   `vumull` entry, confirmed from outside the model.

   And from the integer tables
   (https://dougallj.github.io/applecpu/firestorm-int.html):

       SUBS (immediate, 64-bit)                           LAT 1  TP 0.333  u1-3

   `u1-3` is three of the six integer pipes, not all six -- flag-setting is
   restricted -- so `subs_imm` gets `SCALAR_I0..I2` rather than `I()`.

The upstream checkout is not modified: this patches the loaded module's tables,
which is what its own `get_units`, `get_latency` and `get_inverse_throughput`
read through `lookup_multidict`.

**A schedule produced with this cannot be validated here.**  This repository's
development host is an Apple M2 Pro, whose P-core is Avalanche, not Firestorm.
Any M1 result is a prediction from published data until someone runs it on M1.
"""
from slothy.targets.aarch64.aarch64_neon import (
    vsmull, vsmull2, vsmlal, vsmlal2, vsmlsl, vsmlsl2, subs_imm,
)

WIDENING = (vsmull, vsmull2, vsmlal, vsmlal2, vsmlsl, vsmlsl2)


def patch(model):
    """Add the seven classes to one M1 model, idempotently."""
    if WIDENING in model.execution_units:
        return model
    EU = model.ExecutionUnit
    flag_units = [EU.SCALAR_I0, EU.SCALAR_I1, EU.SCALAR_I2]   # Dougall's u1-3

    model.execution_units[WIDENING] = EU.V()
    model.inverse_throughput[WIDENING] = 1
    model.default_latencies[WIDENING] = 3

    model.execution_units[subs_imm] = flag_units
    model.inverse_throughput[subs_imm] = 1
    model.default_latencies[subs_imm] = 1
    return model
