# GT1152-P01 — ring profile and declared oracle

First gate of the NTRU+1152 Good-Thomas campaign. Pure Python; no assembly, no
build, no hardware. Its purpose is to make every structural claim the port
rests on re-runnable, and to establish the oracle that every later gate is
checked against.

```sh
make check          # proof.py + test_kat.py
python3 test_kat.py --count 3   # quick subset
```

## Contents

| file | role |
| --- | --- |
| `ring-profile.yml` | Frozen ring/representation/range intake for NTRU+1152 |
| `ntruplus1152.py` | **Declared oracle.** Pure-Python NTRU+1152 reference |
| `nistkat.py` | AES-256 + CTR_DRBG, so the KAT transcript needs no C toolchain |
| `proof.py` | Structural proof → `proof-report.json` |
| `test_kat.py` | KAT reproduction → `kat-report.json` |

`ntruplus1152.py` parses its zeta table from
`Reference_Implementation/NTRU+1152/ntt.c` rather than embedding a copy, so it
cannot silently drift from the implementation it checks. C integer semantics
(int16_t wrap, arithmetic shift) are reproduced exactly, because `barrett_reduce`
and `crepmod3` depend on them.

## Results

**KAT: 100/100 cases reproduced byte-for-byte** (pk, sk, ct, ss, and the
decapsulation status), against
`ntruplus-ntt-Optimized/KAT/NTRU+1152/PQCkemKAT_3488.rsp`
(sha256 `2ddfc810c4…64c3`). Runtime ~5.6 s.

Supporting checks run during development:

- `ntt` → `invntt` round trip is the identity on ternary inputs.
- `invntt(poly_basemul(ntt(a), ntt(b)))` agrees with an independent schoolbook
  multiply in `Z_q[x]/(x^1152 − x^576 + 1)`.
- Negative control: perturbing a single zeta by 1 breaks `ct`, `ss` and the
  decapsulation status, so the comparison is not vacuous.
- `nistkat.py` reproduces the FIPS-197 C.3 AES-256 vector.

**Structural proof: 10/10 checks.**

| check | result |
| --- | --- |
| `field/alpha_beta_roots` | `y²−y+1 mod 3457` has roots 723, 2735; sum ≡ 1, matching `ntt_top.S`'s `beta = 1-alpha` |
| `field/alpha_order` | `ord(α) = ord(β) = 6`; `q−1 = 3456 = 2⁷·27` |
| `transform/ord_z_is_864_for_both` | `ord(z) = 864` for both parameter sets |
| `transform/leaf_root_count` | `z¹⁴⁴−α` and `z¹⁴⁴−β` each split into 144 linear factors → 288 leaves |
| `transform/gt_factors_coprime` | `144 = 9×16`, `gcd(9,16) = 1` |
| `tables/reference_zetas_identical` | `NTRU+864/ntt.c` and `NTRU+1152/ntt.c` `zetas[288]` agree on all 288 values |
| `tables/stock_zetas_mul_identical` | stock `base.s` `zetas_mul` agree on all 609 integers |
| `leaves/same_zeta_window_and_count` | both index `zetas[144+i]` with a ± pair; 864 in blocks of 6 (2×degree-3), 1152 in blocks of 8 (2×degree-4); both yield 288 leaves |
| `tables/ntt9_twiddles_are_z_derived` | every non-zero value in `ntt9.S`'s four twiddle tables is z-derived |
| `oracle/zetas_match_reference` | the oracle parses zetas from source |

### The `ord(z) = 864` trap

| n | `ord(X) = 6·(n/2)` | leaf degree | z | `ord(z)` |
|---|---:|---:|---|---:|
| 864 | 2592 | 3 | X³ | **864** |
| 1152 | 3456 | 4 | X⁴ | **864** |

The 864 in the twiddle orders is `144 × ord(α) = 144 × 6`, **not** the parameter
`n`. A generator that searches for an order-`n` root will fail outright at
n = 1152 (no element of order 1152 satisfies `c¹⁴⁴ = α`). Nothing needs
rescaling; the tables are copied.

### Scope of the `ntt9.S` table audit

`tables/ntt9_twiddles_are_z_derived` proves the tables' *contents* are functions
of `(q, z¹⁴⁴−α)` alone: every non-zero value is either a twiddle whose
multiplicative order divides 864, or the exact `round(t·2¹⁵/q)` Barrett–Shoup
constant of such a twiddle.

It does **not** reverse-engineer the 617-instruction `.Lntt_one_bank` body to
reconstruct the table *ordering*. That is deliberate — the port copies
`.Lntt_one_bank` byte-identically, so ordering is fixed by the algorithm rather
than by `n`, and the question does not arise. The tables mix two packing styles
(whole-row twiddle/Shoup pairs in rows 1–12 of `.Lntt16_top0`, lane-interleaved
pairs in rows 13–21), which is why the audit is layout-agnostic.

## What this gate does not establish

- **No degree-4 range bound.** Every NTRU+864 bound is proved for degree-3
  accumulators and does not transfer. G2 owns this.
- **No GT-domain layout.** The oracle works in the reference coefficient order.
  The GT byte layout and the wire permutation are G3.
- **No performance claim of any kind.** This gate never ran on hardware.
