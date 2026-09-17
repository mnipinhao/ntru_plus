# SLOTHY-optimized NTRU+1152 kernels

One directory per microarchitecture.  Each contains the final assembly plus a
`build/` directory holding the two intermediate stages and a JSON report
recording the SLOTHY version, the model file actually used, and the input and
output hashes.

## Two passes, not one

`optimize.py` runs SLOTHY twice, as the NTRU+864 campaign established:

| stage | `functional_only` | `allow_reordering` | `allow_renaming` | what it does |
|---|---|---|---|---|
| `ra` | yes | no | yes | allocate the symbolic registers |
| `timing` | no | yes | no | schedule, with software pipelining and the split heuristic |

Splitting them keeps each solve tractable and makes a failure attributable to
one or the other.  mlkem-native does a single pass because its clean tier
already has concrete registers; ours does not, by design.

## Which model is used

The virtualenv's bundled SLOTHY has no `cortex_a76` model, and silently falling
back to a different microarchitecture would invalidate every number this
campaign has produced.  `optimize.py` therefore puts `$SLOTHY_ROOT` first on the
path and **asserts** that both the architecture and the microarchitecture module
resolve inside it.

## Register discipline

The kernels stash nothing, so `v8-v15` are reserved along with `x18-x30` and
`sp`.  The four modulus constants live in physical `v0-v3`, also reserved: a
symbolic register defined outside the optimized region cannot be allocated, and
recomputing the constants inside the loop would cost eight instructions per
group.  That leaves `v4-v7` and `v16-v31` for SLOTHY.

## Target coverage

`scripts/instruction_coverage.py` answers this by **asking each model** --
calling `get_units`, `get_latency` and `get_inverse_throughput` on a parsed
instance and catching `UnknownInstruction` -- rather than by reading its tables.
Reading the tables under-reports `cortex_a76`, which resolves several classes
through explicit `isinstance` branches in `get_resource_usages`.

| instruction | SLOTHY class | a76 | neoverse_n1 | m1_firestorm | m1_icestorm |
|---|---|---|---|---|---|
| `smull` / `smull2` | `vsmull` / `vsmull2` | yes | yes | **no** | **no** |
| `smlal` / `smlal2` | `vsmlal` / `vsmlal2` | yes | yes | **no** | **no** |
| `smlsl` / `smlsl2` | `vsmlsl` / `vsmlsl2` | yes | yes | **no** | **no** |
| `subs` | `subs_imm` | yes | yes | **no** | **no** |
| `mul` | `vmul` | yes | yes | yes | yes |
| `uzp1` / `uzp2` | `vuzp1` / `vuzp2` | yes | yes | yes | yes |
| `add` / `sub` | `add_imm` / `vsub` | yes | yes | yes | yes |
| `and` / `cmgt` | `vand` / `cmgt` | yes | yes | yes | yes |
| `ldr` / `str` (q) | `q_ldr_with_inc` / `q_str_with_inc` | yes | yes | yes | yes |

**`cortex_a76` and `neoverse_n1_experimental` cover every instruction these
kernels use** -- confirmed by running the `ra` pass against both.  Only the A76
can be measured here.

**Both Apple M1 models need exactly seven classes added**: the six widening
multiply-accumulate forms `vsmull`, `vsmull2`, `vsmlal`, `vsmlal2`, `vsmlsl`,
`vsmlsl2`, and `subs_imm`.  Nothing else is missing.  Today
`make apple_m1_firestorm` fails with

```
UnknownInstruction: Couldn't find <class '...aarch64_neon.vsmull'>
                    for smull v16.4S, v26.4H, v25.4H
```

`dev/slothy_models/apple_m1_ntruplus.py` supplies them, and the numbers are
neither guessed nor measured here.  Two independent things fix them:

- the models already carry `vumull` and `vumlal`, the **unsigned** widening
  forms, at `ExecutionUnit.V()`, inverse throughput 1, latency 3.  The signed
  forms are absent, not different.
- Dougall Johnson's reverse-engineered Firestorm tables give, for the 4S
  variants, `SMULL`/`SMULL2`/`SMLAL`/`SMLAL2`/`SMLSL`/`SMLSL2` at **LAT 3,
  TP 0.25, units u11-14** -- identical to `MUL (vector, 8H)`, and `u11-14` is
  the four vector pipes the model numbers `VEC0`-`VEC3`, so TP 0.25 is one pipe
  for one cycle.  That is exactly the `vumull` entry, confirmed from outside the
  model.  The integer tables give `SUBS (immediate, 64-bit)` at **LAT 1,
  TP 0.333, units u1-3**, three of the six integer pipes rather than all six,
  so `subs_imm` gets `SCALAR_I0..I2`.

The upstream checkout is not modified; the loaded module's tables are extended,
which is what its own `get_units`, `get_latency` and `get_inverse_throughput`
read.  With the patch all four models cover every instruction these kernels use.

**An M1 schedule still cannot be validated here.**  This repository's host is an
Apple M2 Pro, whose P-core is Avalanche and not Firestorm, so any M1 result is a
prediction from published data until it is run on M1 silicon.  What *can* be
checked here is that the M1-scheduled code is correct, by running it on the Pi:
it should produce identical output and be slower than the A76 schedule.
