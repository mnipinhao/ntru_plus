# NTRU+768: absorb modular-half scale into CT twiddles

This follows the [correlated-range/butterfly gate](ntruplus768-correlated-range-butterfly.md). It is an executable scalar and interval **schedule candidate**, not linked AVX2 inverse ASM or a benchmark. The current Official GS and caller-lazy implementation are unchanged.

## What a fixed twiddle can and cannot absorb

An ordinary CT merge computes `a ± w·b`. A modular-half merge computes `(a ± w·b)/2`. Merely changing the lower operand's fixed twiddle cannot implement the latter: set `b=0, a=1`; any `a ± K·b` remains 1, whereas the desired result is `1/2 = 1729 (mod 3457)`. Thus the upper operand must be half-scaled or the merge must perform real data-dependent work. In particular, the signed-average parity correction is not a constant that can be put into a twiddle table.

There is nevertheless a useful mixed-gauge identity. If the upper child already stores `a/2` and the lower child stores unscaled `b`, then

```text
upper: a_half = a/2
lower: b
merge: a_half ± Mont(b, w/2)
```

has the required half-scaled output. Where `w≠1`, this changes an existing Montgomery constant and its companion without adding a multiplication chain. Where `w=1`, `w/2` is nonidentity and **a new chain is required**. The low-word Montgomery semantics and full representative intervals are checked by the executable model, not assumed from field algebra alone.

## A concrete 32-leaf schedule

`U` means unchanged scale; `H` means a factor `1/2` is carried in the stored value. The merge keeps the same CT pairing and factor identities:

| Node | Children | Merge | Output scale |
| --- | --- | --- | --- |
| `U2`, `U4` | two unchanged children | ordinary CT | 1 |
| `H2` | two `U1` | modular-half CT | 1/2 |
| `H4` | `H2` upper, `U2` lower | ordinary CT with lower `w/2` | 1/2 |
| `H8` | `H4` upper, `U4` lower | ordinary CT with lower `w/2` | 1/2 |
| `H16` | two `H8` | ordinary CT | 1/2 |
| `H32` | two `H16` | modular-half CT | 1/4 |

For a single 32-leaf/degree block, this takes 20 modular-half butterflies: four at `H2` and 16 at `H32`. The earlier uniform-stage, no-other-repair screen required 64 per block. In exchange, eight identity twiddles become real fixed multiplications, and 16 already-present twiddles change constants. Across all 24 cohort×degree blocks this is **480 modular-half butterflies, +192 fixed multiplication chains, and 384 changed existing twiddles** relative to the plain CT twiddle ledger. It is not a comparison against the full Official GS inverse; the initial/final true-twist work and top tail still need to be included.

The uniform four-level comparator carries `1/16` scale out of radix-2,
whereas this schedule carries `1/4`. Their final-scale constants and remaining
tail work therefore differ; the 1536→480 count is a local structural contrast,
not a complete work delta.

The complete 768-cell interval screen proves signed-i16 safety for this radix-2 recipe. The largest screened intermediate is 29708 at `H32`; `U4` reaches 30576 before its consumer Montgomery reduction, still within signed i16. On 101 actual compiled BaseMulScale outputs × 24 blocks, every result equals eight times the independent fully normalized CT inverse modulo 3457, as expected from two rather than five halved levels. This implies an algebraic final-scale anchor of `R/48 = 213 (mod q)` in place of the old `R/192 = 2646`; it does **not** authorize substituting a single tail constant without regenerating and proving the radix-3/trinomial schedule.

This specific recipe uses 20 distinct fixed-factor residues versus 16 in the original radix-2 twiddle set; four residues are new. These residue counts are not table bytes, constant-memory operands or load uops. Their AVX2 placement, companion words, routing, register lifetime and final scale remain unpriced. The materialized Official ABI is a goal, not yet a proven output of a complete linked kernel.

## Decision

Twiddle absorption is **real but partial**: it removes the parity/bias work at the `H4` and `H8` merges, not at `H2` or `H32`. It converts a large uniform q-half network into a mixed arithmetic trade-off; no cycle winner can be inferred. The next machine gate should lower this exact recipe together with initial/final twists and the top radix-3/trinomial tail, then compare its full constant, routing and dependency ledger against selective repair and Official GS. Only a complete ≤16-YMM, range-closed schedule should proceed to namespaced ASM and Decap timing.

Reproduce from the experiment directory:

```sh
python3 tools/research_twiddle_half_absorption.py
```

The machine-readable output is `results/yang-true-y-twist-twiddle-half-absorption-20260923.json`.
