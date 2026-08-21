# Checkpoint D: Official stage baseline, persistent NTT9, and NTT9-first oracle

This checkpoint moves the primary local comparator from C0/C2 to the pinned
Official NTRU+1152 AVX2 dataflow. All numbers remain repository-local
diagnostics and are not SUPERCOP promotion evidence.

## Official stage partitions

`tools/generate_official_stage_partitions.py` mechanically extracts three
callable functions from the immutable `upstream/supercop-avx2/ntt.s`:

- `T0`: the unchanged top split;
- `T3x3`: levels 1 and 2, the two radix-3 layers;
- `T2x4`: merged levels 3 through 6, the four radix-2 layers.

The generated assembly is never edited by hand. A 10,003-case differential
requires `T0 -> T3x3 -> T2x4` to be bit-exact with the original `poly_ntt`.
Input reset is outside every timed interval. Sixteen paired blocks per launch
use symmetric `O-C-C-O` / `C-O-O-C` ordering and 96 observations per slot.

Nine fresh launches on Intel Core Ultra 7 155H CPU 1, GCC 15.2 `-O3 -mavx2`:

| Partition / implementation | Median cycles |
| --- | ---: |
| Official T0 | 70 |
| Official T3x3 | 252 |
| D-A persistent NTT9, four pairs / eight streams | 321 |
| Official T2x4 | 474 |
| C4 from-Z, four pairs / eight streams | 422 |
| C4 natural, four pairs / eight streams | 630 |
| Official full forward | 754 |

The partition medians include separate function boundaries and therefore must
not be summed as an exact reconstruction of the monolithic 754-cycle function.
The paired comparisons are the intended evidence:

- D-A minus Official T3x3: **+69 cycles**, or 1.274x;
- C4 from-Z minus Official T2x4: **-52 cycles**, or 0.890x;
- C4 natural minus Official T2x4: **+156 cycles**, or 1.329x.

The natural producer tax is independently recovered as `630 - 422 = 208`
cycles, consistent with C4's earlier 210.136-cycle estimate. The persistent
radix-2 body is competitive; natural-to-GT orientation is the dominant
blocker.

## D-A: persistent S/D to vector NTT9

`ntruplus1152_exp001_gt9x16_ntt9_d_a` consumes C4's
`state[row][S_or_D][lane]` ABI directly. It performs two radix-3 layers with
the same three-chain Montgomery reduction schedule as Official. The first
version intentionally stores and reloads between layers. It performs no
terminal-major reconstruction and no lane permutation.

The kernel passes 10,003 bit-exact cases against the two-layer reference,
including in-place alias cases. Its leaf audit reports 36 Montgomery chains,
no routing instructions, calls, frame, stack references, spills, or
`vzeroupper`. Four calls cover eight NTT9 streams, matching Official's 144
radix-3 Montgomery chains. The current four-call D-A baseline is 27.4% slower
than Official T3x3 and is retained as a correctness/performance baseline, not
selected production code.

## D-B: NTT9-first phase absorption

`generated/gt9x16-ntt9-first-oracle.json` derives the convention from the
actual two-radix3 transform rather than assuming a sign. The implementation is

```text
NTT9(R)_p = sum_a R_a rho^(a p)
```

and therefore the current shear satisfies

```text
Y_a[v] = R_(a+v)[v]
NTT9(Y)_p[v] = rho^(-v p) NTT9(R)_p[v].
```

For each two-trit-reversed output row `p`, define
`phase_base = rho^(-p)`. The oracle proves that the lane phase can be absorbed
without an extra Montgomery layer by replacing every radix-2 stage twiddle at
distance `d` with

```text
adjusted_zeta = ordinary_zeta * phase_base^d.
```

Evidence is exact over the field and includes 1,296 scalar shear/phase basis
checks, 144 phase-absorbed NTT16 basis checks, all 144 combined 9x16 basis
vectors, and all 288 branch/component-oracle entries. Four-bit-reversed NTT16
lanes and two-trit-reversed NTT9 rows remain unchanged.

## Decision

D-B is the next implementation checkpoint:

```text
natural rows -> Official-style NTT9 first -> p-dependent adjusted NTT16
```

The gate is a hand-written adjusted-NTT16 diagnostic using the generated
tables, followed by a full-forward differential and the same paired stage
harness. D-A remains available as the fair C4-order baseline. Evidence:
`results/official-stages-intel155h-20260821-001/official-stage-paired.json`.
