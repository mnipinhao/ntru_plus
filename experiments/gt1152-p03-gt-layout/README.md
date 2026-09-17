# GT1152-P03 — GT output layout, measured not guessed

Tier 2's first open question is the GT transform-domain layout: which byte does
each coefficient land at after `ntt_top` → `ntt_tail` → `ntt9`. Both branches of
the "permute back to reference order?" decision need it.

That layout is defined by `.Lntt_one_bank`, 617 instructions of Slothy output.
This host is arm64, so instead of reverse-engineering it, this gate **builds the
real NTRU+864 GT forward locally and measures the layout**.

```sh
make check      # probe864.py (measures) + predict1152.py (carries it to 1152)
```

Nothing here is a performance fact. This is Apple silicon, not Cortex-A76.

## Measured: the NTRU+864 GT output layout

```
int16 index = top*432 + row*48 + halfcol*24 + component*8 + lane
              top ∈ {0,1}   row ∈ 0..8   halfcol ∈ {0,1}
              component ∈ 0..2 (branch)  lane ∈ 0..7
```

Read off `ntt9.S`: each bank issues 18 stores at byte offsets `{0,96,…,768}` and
`{48,144,…,816}` — 9 rows × 2 half-columns at a 48-byte stride; `component`
picks a 16-byte slot inside that stride, and the two tops are 864 bytes apart.

`probe864.py` then confirms it against the running kernel. The GT→reference leaf
permutation is:

- a **bijection** over all 288 leaves,
- **exact mod q with no scale factor** — GT leaf values equal reference leaf
  values, not a Montgomery multiple,
- **stable across 6 independent random inputs**.

### Independent confirmation

`base_tables.h`'s `basemul_zetas[36][8]` turns out to be **exactly the reference
leaf zetas reordered by the measured permutation**. That table was written by
the 864 campaign with no involvement from this probe, so the two derivations
confirm each other.

## Predicted: the NTRU+1152 GT output layout

```
int16 index = top*576 + row*64 + halfcol*32 + component*8 + lane
              component ∈ 0..3      8 banks, bases 0,256,…,1792 bytes
              tail at +2048         scratch 2304 bytes
              store stride 128 bytes (was 96)
```

**The leaf ordering carries over unchanged.** Which leaf lands at
`(top,row,halfcol,lane)` is fixed by `.Lntt_one_bank` plus the 9×16 enumeration;
neither depends on component count or leaf degree — `component` only selects
which branch of a leaf a slot holds. The port copies `.Lntt_one_bank`
byte-identically, so the permutation is the same.

Consequence: **`base_tables.h` copies verbatim.** Verified — the same
`basemul_zetas` table is correct for 1152, because the reference `zetas[288]`
are bit-identical and both parameter sets use the same leaf→zeta rule
(`zetas[144 + k/2]`, sign by `k%2`).

## Correction to an earlier claim about pack

I previously wrote that 1152's degree-4 leaves make "this entire class of
complexity largely disappear", citing the stock lanes (864 needs
`poly_shuffle_asm`/`poly_shuffle2_asm`, 1152 does not; stock `pack.s` is 452 vs
150 normalized lines). **That evidence is about the stock layout, which has no
GT permutation at all, so it does not carry to the GT pack.** The measurement:

| | 864 | 1152 |
|---|---|---|
| natural-order starts of one GT vector's 8 leaves | `0, 48, 96, 144, 192, 240, 288, 336` | `0, 64, 128, 192, 256, 320, 384, 448` |
| gap | 48 | 64 |
| per leaf, stored | 6 bytes | **8 bytes** |
| per leaf, 12-bit packed | 4.5 bytes | **6 bytes** |

**The scatter is structurally identical** — same permutation, same 8-way spread,
only multiplied by the leaf degree. 1152 does not avoid the scatter.

What genuinely improves is **granularity**:

- 8 bytes per leaf is exactly one `d`-register store; 6 bytes is not, which is
  why 864 needs ST3 lane stores and TBL routing.
- 6 whole bytes per leaf when packed to 12 bits; 864's 4.5 bytes straddle byte
  boundaries, so its packing cannot be done per leaf at all.

So the advantage is real but narrower than I claimed: it is about store and pack
granularity, not about eliminating the routing problem. Expect the 1152 pack to
be simpler than 864's 7,751 lines, but not trivial — and size it from a real
design, not from this argument.

## What still needs verifying

The 1152 layout above is **predicted, not measured**. It follows from the
measured 864 layout plus the component-count change. When G3's eight-bank
forward exists, `probe864.py`'s method must be re-run against it: the derived
permutation must equal `perm864.txt`, and the layout formula must hold.

## Local-build caveat

The NTRU+864 package targets Linux/AArch64. `ntt_tail.S` uses its `C()` macro
and so defines only `_ntt_tail_asm` under `__APPLE__`, while `ntt.S` calls the
unprefixed name. `darwin_shim.S` adds that one alias so the probe can run here.
It is probe scaffolding and belongs nowhere near a release package.
