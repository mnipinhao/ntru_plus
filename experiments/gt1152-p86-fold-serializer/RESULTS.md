# P86 — NTRU+1152's serializer, folded the way the official one folds

Roadmap item 3.  1152's packer and unpacker were C intrinsics and cost +109 ns
of packing and +79 of unpacking against Official in decapsulation.  This closes
most of that without writing any assembly, and without touching the transform.

## What was wrong

The old path transposed first and then encoded each lane on its own: widen the
even coefficients to 32 bits, multiply-accumulate the odd ones in shifted by
twelve, and pull the twelve bytes out with `tbl`.  Three instructions a lane,
twenty-four a pair, on top of a twenty-four-instruction transpose.

Official never does that.  It keeps the coefficients component-major -- lane j
of vector i is coefficient i of block j -- and folds four of them into three
halfwords with shift-insert alone:

```
h0 = c0 | c1 << 12      sli  h0, c1, #12
h1 = c1 >> 4  | c2 << 8  ushr h1, c1, #4 ; sli h1, c2, #8
h2 = c2 >> 8  | c3 << 4  ushr h2, c2, #8 ; sli h2, c3, #4
```

Ten instructions for the whole pair, no table.

**GT already has that arrangement -- before its transpose.**  `load_pair` orders
the rows so a transposed lane reads out as four even coefficients then four odd
ones, which means that before the transpose, vector i holds coefficient i of
every block.  The four consecutive coefficients of a block are in `v[0]`,
`v[4]`, `v[1]`, `v[5]` and the next four in `v[2]`, `v[6]`, `v[3]`, `v[7]`.  So
the fold applies directly and the transpose moves to *after* the fold, where it
gathers six halfword streams instead of eight coefficient streams.

The reduction follows Official too: a rounding multiply-high and a
multiply-subtract to land in (-q, q), then a sign mask and a second
multiply-subtract to make it canonical.  Four instructions a vector against the
old five.

The decode is the fold run backwards -- `ushr`, `sli`, `and` -- which retires
the `unpack_idx` table and the per-lane shift vector.

## Per kernel, M2 Pro, gated harness, both sides built the same way

|  | before | after | |
|---|---:|---:|---|
| `tobytes_full` | 129.2 | **98.0** | **-31.3** |
| `tobytes_small` | 92.9 | **65.4** | **-27.5** |
| `tobytes_compare` | 166.7 | 159.3 | -7.4 |
| `frombytes` | 79.8 | **70.9** | -8.9 |

Official's `poly_tobytes`, for scale, is 78.2 ns.

`tobytes_compare` barely moves because it is dominated by the dependent lane
loads of the expected bytes, not by the encoding -- consistent with P84's
finding that it is a net cost at 1152.  It is now worth revisiting: against
`tobytes_full` at 98.0 plus a 21 ns constant-time `verify`, the fused compare is
40 ns behind rather than 16.

## At the KEM level

| | keygen | encaps | decaps |
|---|---:|---:|---:|
| M2 Pro, default alignment | **-81** | **-62** | **-56** |
| M2 Pro, `-falign-functions=64` | -57 | -63 | -53 |
| **Cortex-A76**, `taskset -c 3` | **-105** | **-58** | **-75** |

Both machines improve, so the promotion criterion holds.  A76's clock sat at
2400 MHz with 41 of 41 rounds accepted.

Against Official + CE at the SUPERCOP revision on M2, NTRU+1152 goes from
-1.2% / -4.5% / -2.3% to **-1.9% / -5.5% / -3.3%**.

## A measurement trap worth recording

The first KEM comparison said keygen had *regressed* by 22 ns.  It had not: the
"before" binary had been built earlier in the session, and rebuilding the same
source in the same session as the "after" binary moved keygen by 66 ns on its
own.  Profiling showed `pack/unpack` down 62 ns exactly as predicted while
Keccak -- untouched, byte-identical, and at the same alignment mod 64 -- appeared
165 ns slower.  That is I-cache set and branch-predictor aliasing following the
shift in code addresses.

**Both sides of any KEM-level comparison must be built in the same session with
the same flags**, and a delta smaller than about 70 ns on this part should be
treated as layout noise unless it survives a rebuild.

## Verification

- 300 random vectors: `tobytes_full`, `tobytes_small`, `tobytes_compare` (both
  agreeing and both detecting a flipped bit) and `frombytes` (values and the
  out-of-range flag) all bit-identical to the previous implementation.
- `make check` on both machines: canonical boundary 13,824 cases, ABI masks all
  zero including the four serializer entries, 288/288 baseinv rejections,
  zeroization 33 calls / 34,000 bytes / nothing left, KAT matching
  `kat/expected`, deterministic SUPERCOP export.
- SUPERCOP leaf regenerated; `check_supercop_leaves.py` reports all current.
