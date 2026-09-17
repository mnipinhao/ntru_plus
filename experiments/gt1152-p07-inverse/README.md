# GT1152-P07 — can the inverse Slothy artifacts be remapped?

Decision **D6** assumed the three inverse kernels transfer to 1152 by remapping
immediates alone, because the per-call work is invariant. This gate checks that
statically, against the real sources.

**Answer: yes for two of the three. D6 is wrong about the tail.**

```sh
make check      # analyze.py + verify864.py
```

## The reference, validated first

`verify864.py` builds NTRU+864's decapsulation arithmetic chain on this arm64
host and checks it end to end:

```
forward -> basemul_rinv -> invntt_ternary  ==  crepmod3(schoolbook product)
```

6 random ternary cases, exact. This pins the chain's I/O contract before
anything is remapped, and gives the 1152 port something to be checked against.

(The 864 package targets Linux; `darwin_shim.S` from G3a supplies the one
missing symbol alias, and `support_abi.S` is left out because it drags in
cbd/sotp wrappers the inverse path does not use.)

## The accounting that settles it

Output coefficients per call, from static `strh` counts:

| kernel | per call | 864 calls | 1152 calls | per-call work |
|---|---:|---:|---:|---|
| `packed_i9` | 72 (9 rows × 8 lanes) | 12 | 16 | **invariant** |
| `invntt16_asm` | 128 | 6 | 8 | **invariant** |
| `invntt16_tail_asm` | 96 | 1 | 1 | **not invariant** |

```
864 : 6 × 128 + 96  = 864   ✓
1152: 8 × 128 + ?   = 1152  →  the tail must produce 128, not 96
```

D6's reasoning was that component count and total coefficients both grow by
4/3, so per-call work is unchanged. That holds for the two kernels driven by a
per-component loop. It does **not** hold for the tail, which is called once and
covers all components at once — so its work grows with the component count.

## But the fix is small, and the arithmetic is already right

| | `inverse16.S` | `inverse16_tail.S` |
|---|---:|---:|
| vector arithmetic | 311 | 309 |
| `umov` | 128 | 96 |
| `strh` | 128 | 96 |

**The tail's vector arithmetic is already eight-lane and essentially identical
to the main kernel's.** NTRU+864 packs 2 tops × 3 branches into 6 of 8 lanes and
simply never stores the other two — but it computes them. For 1152 those two
lanes carry real data (2 tops × 4 branches fills all eight), so the results are
already there.

The gap is exactly `128 − 96 = 32 = 2 padding lanes × 16 t`, in `umov`/`strh`
pairs only.

## Immediate maps for the two that do transfer

**`inverse9.S`** — one change. Only `x2` carries a layout-dependent stride:

```
[x2, #96k] -> [x2, #128k]     9 offsets, the Good-Thomas row stride
```

Every other base (`x0`, `x3`, `x16`) uses 16-byte strides and is unaffected.

**`inverse16.S`** — all 128 `strh` offsets are multiples of 6, because the
branch is folded into the base pointer by the driver (`x0 = out + component*2 +
half*24`). So they are `6m` and scale by `8/6` exactly:

```
[x0, #6m] -> [x0, #8m]        range [0..1692] becomes [0..2256]
```

**`inverse16_tail.S`** — offsets decompose as `6m + 2b` with `b ∈ {0,1,2}`,
because this kernel writes all branches itself. 1152 needs `b ∈ {0,1,2,3}`,
which is precisely why the store count grows.

## The tail's structure, measured

Decision taken: rewrite the tail in intrinsics C for Milestone 1, with assembly
as the eventual target.

`invntt16_tail_asm` emits raw values — `crepmod3_raw.S` does the ternary step
afterwards — so it is **linear in its scratch input** for fixed tables. That
makes it measurable rather than readable: `probe_tail.c` builds it standalone
and `tail-map.json` records the full map recovered from 128 delta probes.

Three findings, in order of usefulness:

1. **Each bank's input affects 32 outputs**, and banks overlap completely,
   because the terminal performs the α/β inverse CRT — one input lane reaches
   both halves.
2. **The three branch maps are byte-for-byte identical.** So the kernel is
   three independent copies of one *2 banks (top 0 and 1) × 16 t → 32 outputs*
   map, with outputs at int16 index `3m + branch`.
3. Each column has exactly 32 non-zero entries, at output `m` indices that are
   all multiples of 9 — the `s = 8` row, as expected (the driver's `out + 48`
   shifts them to `m ≡ 8 mod 9`).

**So the 1152 tail is the same map run four times instead of three**, with
outputs at `4m + branch`. And the map itself carries over unchanged: the
16-point inverse and the α/β CRT are leaf-degree independent, and `n/d = 288`
for both parameter sets, so the scale is identical too.

That reduces the C rewrite from "reimplement 1205 lines of Slothy output" to
"apply a measured 32×32 map per branch".

## Cost, stated honestly

A dense 32×32 map per branch is 1024 multiplies × 4 branches, against the 589
instructions of the 864 assembly. It is correct and it is directly derived from
the validated kernel, which is what Milestone 1 needs — but it is materially
slower, and the assembly version stays the target.

## Still to do in G6b

- the C tail itself, against `tail-map.json`
- `inverse9.S` and `inverse16.S` immediate remaps (maps already derived above)
- `inverse.S` driver edits for the new call counts and offsets
- `crepmod3_raw.S` loop count 27 → 36
- full differential against the G1 oracle

No Pi 5 measurement and no performance claim.
