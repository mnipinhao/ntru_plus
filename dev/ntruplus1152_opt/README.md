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
