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

Adding them is a small, well-bounded patch -- an execution unit, an inverse
throughput and a latency for each -- but the numbers have to be **measured**,
and this repository's development host is an **Apple M2 Pro**, a different
microarchitecture from either M1 core.  Measurements taken here would not
validate an M1 model.  That is the only thing between this tree and a second
schedulable target.
