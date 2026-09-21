# P87 — why NTRU+864's serializer is expensive, and the shape that would fix it

P86 took NTRU+1152's packer from 129.2 to 98.0 ns by folding four coefficients
into three halfwords with shift-insert instead of transposing first and pulling
each lane out with `tbl`.  The same trick does not transfer to 864 unchanged.
This is why, and what does transfer.

All of it comes from the permutation measured directly -- feed a polynomial
whose value is its index through the packer, decode the 12-bit fields, and the
GT-slot-to-wire map falls out exactly.  `extract_perm.c` and the two tables are
beside this file.

## The one structural fact that separates them

| | vectors per 12-byte block | lanes per 12-byte block | same-lane run |
|---|---|---|---|
| **1152** | 8 | **1** (144 of 144) | **8** wire positions |
| **864** | 8 | **2** (108 of 108) | **6** wire positions |

At 1152 a single 8x8 transpose delivers a whole 12-byte block: the eight
coefficients it needs sit at one lane of eight vectors.  At 864 they sit at
*two* lanes -- six at lane L and two at lane L+4 -- so no transpose produces a
block, and the packer has to route them.  That is the whole reason
`pack_small.S` spends 200 `trn`, 108 `uzp` and 54 `tbl` on 432 coefficients
where 1152 now spends 24 `trn` per 64.

The deeper structure, for the record:

* a same-lane run is exactly **6 wire positions = 9 bytes**, everywhere;
* 12 consecutive wire positions come from **12 distinct vectors at a lane pair
  (L, L+4)**, six at each;
* there are **18 such 12-vector sets**, each serving exactly **4** super-blocks,
  at lane pairs (0,4), (1,5), (2,6), (3,7), with the vector order fixed;
* every vector belongs to exactly two sets.

## The scheme that does not work: a 12-period fold

The obvious port of P86 is to fold twelve coefficients into nine halfwords and
store eighteen bytes.  Six `ext` rotate the second six vectors by four lanes so
all twelve are lane-aligned, and one fold then serves four super-blocks.

It does not pay.  A 12-vector group only ever uses lanes 0-3 of its first six
vectors and 4-7 of its last six: **half of every load is discarded**, because
the other half belongs to the group's partner set.  Counting instructions per
coefficient, with a separate reduction pass to avoid reducing everything twice,
it lands near 2.1 against the current 2.3 -- a 9% paper saving for a complete
rewrite.  Not worth it.

## The scheme that does work: a 6-coefficient, 9-byte unit

Take **six vectors** rather than twelve.  Lane j of those six is a valid
6-coefficient run for every j, so eight runs come out of 48 loaded coefficients
with **nothing discarded**.

Six coefficients are 72 bits, which is four and a half halfwords -- the reason
this looked impossible.  Fold them into **five** halfwords instead and store
nine bytes, leaving the top byte of the fifth undisturbed:

```
h0 = c0 | c1 << 12          sli  h0, c1, #12
h1 = c1 >> 4  | c2 << 8     ushr h1, c1, #4  ; sli h1, c2, #8
h2 = c2 >> 8  | c3 << 4     ushr h2, c2, #8  ; sli h2, c3, #4
h3 = c4 | c5 << 12          sli  h3, c5, #12
h4 = c5 >> 4                ushr h4, c5, #4      (only the low byte is used)
```

Seven instructions for the whole six, no table.  Then gather the five streams
so lane j is run j -- a partial transpose, five streams rather than eight --
and store `str d` plus one byte.

Per 48 coefficients: 6 loads, 24 reduce, 7 fold, about 18 gather, 16 store --
call it **1.48 instructions per coefficient against the current 2.3**, a 36%
cut, and `tbl` disappears in favour of `sli` and `trn`.  Scaling P86's result
the same way puts `tobytes_full` near **79 ns against today's 123.5**, which is
Official's 78.

## Notes for whoever implements it

* **The one-byte tail can be avoided.** Runs at one lane advance nine bytes per
  group, so storing ten bytes (`str d` + `str h`) overlaps one byte into the
  next group, which the next group rewrites.  Process groups in increasing
  order within a lane and only the final group needs the narrow store.  This is
  reachable at 864 in a way it was not at 1152, where the overlapping blocks
  belonged to eight different pairs.
* **The reduction should follow Official's**, as P86's did: a rounding
  multiply-high and a multiply-subtract, then a sign mask and a second
  multiply-subtract.  Four instructions a vector rather than five.
* **The decode is the same fold backwards** -- `ushr`, `sli`, `and` -- and 864's
  unpack is only +24 ns against Official today, so it is the smaller half.
* `pack_small.S` currently carries **59 `mov` and 58 `add`** of pure register
  and address overhead out of about 1,000 instructions.  A generated,
  fully-unrolled emitter with immediate offsets should not need them.
* Do it in C intrinsics first.  P86 got 1152 from 129.2 to 98.0 without a line
  of assembly, and the risk profile is not comparable.

## What this is worth

864's decapsulation spends 242 ns packing against Official's 156, and 259
unpacking against 235.  The packer is the half that moves.  Two calls in
decapsulation, two in key generation, one in encapsulation, so at roughly
-35 ns a call this is about -70 ns on decapsulation and key generation and
-35 on encapsulation -- against arithmetic deficits, after P84's correction, of
+124, +53 and -5 ns.

---

# Implemented, 2026-09-21

The six-coefficient scheme landed.  `pack_full.S` and `pack_small.S` are gone --
564 KB of assembly replaced by about a hundred lines of C intrinsics in
`pack.c`, driven by a generated `pack6.h`.

## Per kernel, M2 Pro, gated harness

|  | assembly | P87 C | |
|---|---:|---:|---|
| `tobytes_full` | 123.7 | **97.2** | **-26.5** |
| `tobytes_small` | 114.1 | **69.7** | **-44.4** |
| `tobytes_compare` | 133.0 | 161.8 | *+28.8, not adopted* |

Official's `poly_tobytes` is 78.7 for scale.

The fused compare does not survive the move.  Its cost is the nine-byte fetch of
the expected run: an eight-byte load plus a lane insert goes through a
general-purpose register, and replacing it with a masked sixteen-byte load was
worse still (161.6).  The assembly `pack_compare.S` is kept.

## At the KEM level

| | keygen | encaps | decaps |
|---|---:|---:|---:|
| **M2 Pro** | **-109** | **-66** | **-37** |
| **Cortex-A76**, `taskset -c 3` | **-359 (-2.3%)** | **-239 (-1.6%)** | **-143 (-1.0%)** |

**A76 gains more than M2, in both absolute and relative terms.**  That was not
expected: the campaign's standing explanation is that delivery work hides in the
shadow of A76's single multiply pipe.  It does not hide here, because the packer
was never multiply-bound -- it was bound on `tbl` and `uzp`, and removing them
helps a machine with one permute pipe more than one with several.

## The compare is now the thing to fix

| | ns |
|---|---:|
| assembly `tobytes_compare` | 133.0 |
| **P87 `tobytes_full` + constant-time `verify`** | **114.0** |
| assembly `tobytes_full` + `verify` | 140.8 |

Packing into a buffer and verifying now beats the fused compare by 19 ns,
where against the old packer it lost by 7.5.  It needs 1296 bytes that decap
does not currently have spare, though `buf3` is `POLYBYTES + SYMBYTES` and its
tail is dead after `poly_cbd1` consumes it.  That is roadmap item 4, and it is
the same conclusion 1152 reached from the other direction.

## Verification

400 random vectors across `tobytes_full` (arbitrary signed int16),
`tobytes_small` and `tobytes_compare`, including a flipped bit that both
implementations must catch, all bit-identical to the assembly.  `make check`
passes on both machines: 10,368 canonical-boundary cases, ABI masks all zero,
zeroization 21 calls / 24,028 bytes / nothing left, KAT matching
`kat/expected`, deterministic export.  SUPERCOP leaf regenerated.
