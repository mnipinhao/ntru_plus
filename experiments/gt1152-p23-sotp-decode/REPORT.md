# P23 — `poly_sotp_decode`, two bits per coefficient

Branch `neon-1152`, parent `85c5f1e3`.  Pi 5 core 3, GCC 14.2.0.

P21 measured this at 1,343 cycles against the official's 508 and found the
cause: P13's NEON version does a horizontal `vaddvq_u16` **per output byte**,
144 of them, packing eight 0/1 lanes into a byte by multiplying by
`{1,2,...,128}` and reducing.

**484 cycles, 2.75x faster and below the official's 508.  `poly_sotp_decode`
went from +835 to -17, decaps from +0.90% to -0.53%, and the KEM from +0.00% to
-0.44%.**

## 1. The message needs no bit expansion at all

The reference computes, for output byte i and bit j,

```
t4  = (buf[144+i] >> j & 1) + a[8i+j]        as uint16
r  |= t4                                      ; failure if any t4 > 1
bit = (t4 ^ (buf[i] >> j)) & 1
```

so the message is simply

```
msg[i] = packLSB(a[8i..8i+7]) ^ buf[144+i] ^ buf[i]
```

The only hard part is packing eight coefficients' low bits into a byte, and the
official's `cbd.s` shows how to avoid paying for it separately.

## 2. Two-bit fields make the buf bytes usable as-is

Carry the coefficients as `a + 1` in two-bit fields, four to a byte.  Then a buf
byte lines up directly: its even bits are `b2 & 0x55` and its odd bits are
`(b2 >> 1) & 0x55`, each aligned with one of two field vectors.  No bit-plane
expansion, no `dup` from a scalar byte.

With `f = a + 1 + b2 = t4 + 1`, the failure test falls out of the same packing:

| f | t4 | f0 ^ f1 | valid |
|---:|---:|---:|---|
| 0 | -1 | 0 | no |
| 1 | 0 | 1 | **yes** |
| 2 | 1 | 1 | **yes** |
| 3 | 2 | 0 | no |

so bit 0 of `f ^ (f >> 1)` is exactly the validity of that field, and
`ok &= ve & vo` accumulates it across the whole polynomial.  The message bit is
`t4 & 1`, the complement of the field's bit 0.

## 3. Non-ternary coefficients are handled, not assumed

Two-bit fields would overflow on a coefficient outside {-1,0,1}, so the obvious
reading is that this needs a precondition.  It does not: the reference **fails**
on any such coefficient anyway, because `t4 = a + b2` read as uint16 exceeds 1
whichever way `b2` falls.  A saturating narrow (`vqmovn_s16`) preserves that
property, and a running `vmaxq_u8` over the field values reports it.  So the
behaviour is the reference's, not a narrowed contract.

## 4. The de-interleave, simulated rather than assumed

Three `uzp` levels over eight byte vectors give the eight planes
`q[k][l] = a[8l + plane(k)] + 1`.  The plane order is **0,2,1,3,4,6,5,7**, not
the bit-reversal one might guess.  Assuming the bit-reversal was the one defect
in this gate, and it survived the first differential because that test's only
accepted cases were the all-zero polynomial, where every field is valid whatever
the order.  Simulating `uzp1`/`uzp2` symbolically settled it in one step.

**The test was strengthened as a result.**  It now builds genuinely valid
encodings — pick the message bit `m`, set `a = m - b2` so `t4 = m` always — so
the accepted path is exercised with real message content.

## 5. Correctness

```
20,000 trials x 1152 coefficients, four modes:
  valid encodings (a = m - b2)                  5,000 accepted
  valid with one coefficient corrupted          rejected
  random ternary                                rejected
  random in [-3,3], out of range                rejected
mismatches against the reference (return code and all 144 message bytes): 0
```

Package gates on the Pi, all green: KAT sha256 `2ddfc810c4...64c3`, 64 round
trips with tampered rejection, 13,824 canonical cases, 11/11 ABI sentinel masks
zero, 288/288 baseinv, zeroization clean, 43-file manifest.

## 6. Measured

| | cycles |
|---|---:|
| P13, horizontal reduction | 1,332 |
| **P23, two-bit fields** | **484** |
| official | 508 |

| operation | official | GT | delta | was |
|---|---:|---:|---:|---:|
| keygen | 64,061 | 64,775 | +1.12% | +1.06% |
| **encaps** | 59,551 | **58,337** | **-2.04%** | -1.92% |
| **decaps** | 52,498 | **52,218** | **-0.53%** | +0.90% |
| **total** | **176,109** | **175,331** | **-0.44%** | +0.00% |

**Two of the three operations now beat the official and so does the total**,
with the hash still the generic sponge.

## 7. Next

P21's order continues with `poly_basemul_rinv` (+834, degree-4 intrinsics C,
never scheduled — M2-2).  After that, `baseinv` (+2,406) is keygen-only and is
what keeps keygen positive.

## Reproduce

```sh
gcc -O2 -march=native test.c sotp.c -o t && ./t
gcc -O3 -march=native -D_DEFAULT_SOURCE bench.c sotp.c old_sotp.c -o b && ./b
```
