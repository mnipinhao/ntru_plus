# GT Production Serialization And Endpoint Audit

Date: 2026-07-24

## Conclusion

Serialization is the best next code-size target, but the useful change is
more specific than "merge duplicate endpoints."

The release contains three large canonical serializers:

| Linked region | Text bytes | Share of 80,673-byte text | KEM use |
| --- | ---: | ---: | --- |
| generic `poly_tobytes` | 5,440 | 6.74% | encap x2, decap x1 |
| generic `poly_frombytes` | 4,400 | 5.45% | encap x1, decap x2 |
| keygen CQ `tobytes` | 5,168 | 6.41% | keygen x3 |
| QSoA pack and unpack | 472 | 0.59% | decap verify |
| **serialization total** | **15,480** | **19.19%** | |

The underscore-prefixed symbols are address aliases, not duplicate bodies.
The public KEM wrappers are also too small to matter. The first proven
duplication target is an exact internal `pack64` register contract shared by
the generic, keygen, and QSoA pack paths.

## Exact Pack Duplication

All three pack paths reach the same physical input contract:

```text
v0       = q
v9-v12   = first four coefficient vectors
v26-v29  = second four coefficient vectors
x0       = canonical output pointer
```

They then execute the same 60 instructions, including the two 48-byte stores:

```text
conditional lift to [0,q)
-> 12-bit field packing
-> byte transpose
-> 96-byte canonical store
```

The instruction sequence is operand-for-operand identical:

```text
generic poly_tobytes:      12 static copies
keygen CQ tobytes:          12 static copies
QSoA tobytes loop:           1 static copy
```

This is not an opcode-shape guess. The source audit finds 12 exact copies at
the expected chunk boundaries in each unrolled serializer.

## Shared Helper Candidate

The first candidate should extract only this 60-instruction body:

```text
layout-specific frontend
-> internal ABI pack64_from_qregs
-> next chunk
```

Static estimate:

```text
current pack-family instructions:   2,612
shared-helper estimate:             1,198
instruction reduction:             1,414
byte reduction before alignment:    5,656
```

The estimate includes one `bl` at every replaced static site and one shared
60-instruction body plus `ret`. Saving/restoring LR and alignment can move the
exact result by tens of bytes, not kilobytes. The expected reduction is about
5.6 KiB, or 7% of the current release `.text`.

The dynamic cost is two instructions per 64 coefficients:

```text
fall-through core    -> 60 instructions
BL + core + RET      -> 62 instructions
```

Therefore one serializer call adds about 24 retired instructions across its
12 chunks, before any LR-preservation overhead. The larger risk is the new
call boundary preventing cross-boundary scheduling, not the retired count.
The helper must use a documented private ABI and preserve the wrapper's return
address. AAPCS aliases alone are not sufficient evidence.

## Why Not Merge Whole Endpoints

The endpoint frontends are semantically different:

```text
generic pack:
  GT block-major row-bitrev gather + transpose

keygen pack:
  CQ gather + table lookup + unzip

QSoA pack:
  contiguous eight-vector load
```

Only the final register-shaped `pack64` core is identical. Forcing all three
through a common memory layout would add a scratch write/read boundary and
would discard the reason the keygen-specific endpoint exists.

The unpack side has no comparable exact body. The current generic unpack is a
4.4 KiB fully unrolled canonical-to-GT scatter, while QSoA unpack is a compact
200-byte loop with a different destination contract. Their longest common
opcode-shaped run is seven instructions, but operand-for-operand comparison
leaves only one instruction. A shared whole endpoint is not justified by
duplication evidence.

## Existing Performance Evidence

The large serializers are speed-selected implementations:

| Component | GT cycles | KPQC cycles | GT overhead |
| --- | ---: | ---: | ---: |
| generic canonical pack | 613 | 459 | +154 |
| generic canonical unpack | 487 | 328 | +159 |

The internal-layout diagnostics are faster than KPQC; the fixed canonical
permutation is the overhead. Existing scheduling work already selected:

- pack P1 only for keygen, because global P1 regressed encap/decap context;
- unpack U1 globally, saving about 39 cycles per standalone call;
- compact decap verification, saving 9,088 text bytes at about 112 full-decap
  cycles versus the speed profile.

This means a compact serializer cannot be promoted from text size alone. It
must be measured in each caller context.

## Candidate Order

1. **C1: shared `pack64_from_qregs` private helper**

   Highest-confidence size candidate. Expected text reduction is about
   5.6 KiB. Keep generic, keygen CQ, and QSoA frontends unchanged.

2. **C2: looped generic unpack**

   Separate compactness experiment, not duplicate elimination. Preserve U1
   as the speed baseline. Target at least 2 KiB reduction and no more than
   0.5% warm full-KEM regression.

3. **C3: encap product-to-bytes endpoint**

   Consider only after C1 defines a reusable pack register contract.
   `poly_basemul_add` already produces a byte-equivalent representation, but
   the release still writes a polynomial and calls `poly_tobytes`. Direct
   fusion may save data traffic, but duplicating pack arithmetic would increase
   text again.

4. **Do not merge decap verification first**

   Its QSoA serialization is already compact, and the complete actual verify
   product-to-bytes path is slightly faster than KPQC. The 2,880-byte
   pointwise kernel is arithmetic, not duplicate serialization.

## Required C1 Gates

```text
exact 60-instruction semantic core preserved
private vector/GPR clobber contract documented
LR and AAPCS64 preservation pass
canonical pack differential pass
keygen CQ pack differential pass
QSoA pack differential pass
KAT and 100 KEM round trips pass
same-binary paired keygen/encap/decap PMU
warm regression <= 0.5%
mixed/cold instruction-cache evidence
linked text reduction >= 2 KiB
```

The first implementation should remain development-only. The release folder
must receive only a candidate that passes these gates.

## C1 Measurement Result

The first wave was completed on Pi 5. The best shape is a split candidate:

```text
generic pack = existing compact scheduled shared core
CQ keygen pack = current frontend + shared exact pack64 core
```

Combined result:

```text
linked text:       80,673 -> 74,273 bytes
generic pack:      -14 paired cycles
CQ keygen pack:    -20 paired cycles
full keygen:       about -115 cycles
full encapsulation about -25 cycles
full decapsulation flat
mixed KEM:         about -124 cycles
KAT/ABI:           pass
```

The detailed result is stored in:

```text
ntruplus-ntt-Optimized/aarch64-bench/results/
  gt_production_icache_size_2026-07-24/serialization-c1-result.md
```

## Reproduction

Source duplication:

```sh
python3 \
  ntruplus-ntt-Optimized/Additional_Implementation/aarch64/NTRU+768/experiments/gt_production_icache_size/analyze_serialization_duplication.py \
  --release-root ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+768
```

Linked sizes were read from the externally built Pi 5 ELF:

```text
/tmp/ntruplus-gt-release-20260724-v2-build/test_kem
```

The machine-readable linked inventory is
`serialization_endpoint_inventory.json`.
