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

## Target coverage: only `cortex_a76` works today

The three target directories exist because the structure is worth having, but
**only `cortex_a76` can currently schedule these kernels.**  SLOTHY's
microarchitecture models differ sharply in completeness:

| model | lines | has `Vmull` / `Vmlal` |
|---|---:|---|
| `cortex_a76` | 869 | **yes** |
| `neoverse_n1_experimental` | - | no |
| `apple_m1_firestorm_experimental` | 480 | no — and no `Vmul`, `Vmla` or `Vqdmulh` either |
| `apple_m1_icestorm_experimental` | - | no |

Running `make apple_m1_firestorm` fails with

```
UnknownInstruction: Couldn't find <class '...aarch64_neon.vsmull'>
                    for smull v16.4S, v26.4H, v25.4H
```

and `neoverse_n1` fails the same way.  Every NTRU+1152 kernel admitted here is
built on widening multiplies, so none of them can be scheduled for those
targets without first extending the models.

Extending them is possible but would have to be *measured*, not guessed, and
this repository's development host is an **Apple M2 Pro** — a different
microarchitecture from either M1 core, so numbers taken here could not validate
an M1 model.  The Pi 5's Cortex-A76 remains the only target this repository can
both schedule and measure.
