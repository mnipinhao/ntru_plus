# ENCAP-H-INGRESS-MA2-H3-ASM

This checkpoint realizes H3-full as one namespaced, aligned AVX2 leaf.  It
closes correctness and linked-machine feasibility only; it does not authorize
or run a benchmark.

## Realized contract

```text
(PK bytes, r Natural-Q scale-4, m Natural-Q scale-4)
    -> c MA2 scale-4
```

The function returns exactly the public invalid-key result of Official
`poly_frombytes`.  For valid keys its 2,304-byte output is raw bit-exact with:

```text
H1 Natural-Q decoder
-> resident h[1152]
-> preprojected-h MA2
```

H3 itself never constructs or stores that resident `h` object.

## Linked schedule correction

The first prototype caught a stale liveness assumption in the symbolic
schedule: the decoder still writes `ymm6` while extracting `d1`, so forming
tile-A `h0` in `ymm6` immediately after `d0/d4` would overwrite a live result.
The faithful linked realization uses a one-pair-delayed formation pipeline:

```text
decode/validate pair j
-> decode/validate pair j+1
-> dual-form pair j into its final tile-A/tile-B registers
```

After pair 3, pairs 2 and 3 are drained in order.  The final allocation remains
the planned one:

```text
tile A h0..h3: ymm6, ymm11, ymm12, ymm13
tile B h0..h3: ymm7, ymm8,  ymm9,  ymm10
```

Mechanical backward liveness remains 12 YMM through decode/formation.  Tile A
still reaches the intended exact 16/16 cut, tile B peaks at 12, and the linked
leaf has no frame, spill, call, branch, or `vzeroupper`.

## Correctness closure

The test gate covers:

- all 4,096 possible 12-bit values at one coefficient;
- all four boundary values at every one of 1,152 coefficient positions;
- 1,003 random valid public keys and 1,003 random packed byte strings;
- Official/H1/H3 accept-reject equivalence;
- raw H1-preprojected MA2 versus H3 output equality for valid keys;
- output alias with `r` and with `m` on selected valid trials;
- PK, `r`, and `m` immutability plus output canaries;
- ASan/UBSan and the experiment-wide `make check` gate.

No intermediate `h` array is added for testing; only the H1 control
materializes one.

## Linked H3 versus H1

The actual combined H1 path is the H1 decoder plus preprojected-h MA2.  The
linked object reports:

```text
                         H1       H3       delta
logical instructions    3678     3587       -91
h vector stores           72        0       -72
h vector reloads          72        0       -72
vperm2i128               198      198         0
vpshufb                  144      144         0
vpor                      72       72         0
Montgomery/add/sub       same     same         0
.text bytes             22881    22072      -809
.rodata bytes            5408     5408         0
```

Pairwise public validation costs 54 more logical instructions than H1's tree
reduction, while merging two function returns removes one instruction.  The
144 eliminated boundary memory instructions therefore produce the exact net
`-91` logical-instruction delta.  All 360 lane-aligning routes remain because
they are the first presentation required by MA2; pure `h`-ABI routing remains
zero.

## Terminal hook

Every coefficient-plane output reaches a zero-instruction
`H3_TERMINAL_C(tile, coefficient, ymm4)` hook immediately before its aligned
store.  This preserves the future coefficient-streaming H4 attachment point
without retaining four outputs simultaneously or changing the current leaf.

## Decision

H3-full is now a production-capable research primitive at the isolated leaf
contract:

```text
resident h object       eliminated
h stores/reloads        0 / 0
pure h-ABI routes       0
MA2 arithmetic          unchanged
validation semantics    Official-exact
raw valid output        H1-exact
peak YMM                16
stack/spill             0 / 0
entry/constants         32-byte aligned
```

Benchmarking, caller integration, H4, and native KEM remain outside this
checkpoint.
