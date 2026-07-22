# Canonical unpack next-wave results

Historical experiment baseline: U0 was production and U1 was default-off when
this experiment ran. U1 is enabled globally in `gt_production_default` as of
2026-07-18 after KEM, KAT, cross-vector, guard, ABI, and paired PMU promotion
gates passed.

## What changed

Both variants implement the same public, little-endian contract:

```text
two 48-byte canonical loads
  -> transpose packed fields
  -> unpack and mask 64 12-bit coefficients
  -> 8x8 canonical-to-GT transpose
  -> 16 fixed eight-byte GT block stores
```

U1 exposes that complete chain to one symbolic register allocation and schedule.
The final transpose writes its four high-half outputs directly with `trn2`; U0
uses `trn2` into temporaries followed by four `mov` instructions.  Arithmetic,
masking, offsets, permutation, store sizes, and the two `umov/str` lane-store
contracts are unchanged.

## Static and Slothy result

| Variant | Instructions/chunk | Full function instructions | N1 expected cycles | N1 bound |
|---|---:|---:|---:|---:|
| U0 production source | 94 | 1141 | not rescheduled here | - |
| U1 whole DAG | 90 | 1093 | 59 | 59 |

The full-function count includes one prologue/epilogue and 12 chunks.  U1
therefore removes 48 static/dynamic instructions from one full unpack.  Slothy
reported `OPTIMAL`, no spills, and internal self-check `OK`.  The model is
Neoverse N1 and is not a Pi 5 cycle measurement.

The requested remote host currently has a Python runtime mismatch: its system
interpreter is CPython 3.15 while the existing NumPy/OR-Tools venv is CPython
3.14.  The solve was therefore run with the existing local Slothy checkout and
the same N1 target model.  The remote host still passed final AArch64
cross-assembly and Linux PMU C syntax checks.

## Correctness and ABI

The chunk and full candidates pass:

- all 256 uniform input-byte values;
- 4,000 deterministic random 1,152-byte inputs;
- exact comparison with `poly_frombytes_gt_canonical`;
- chunk untouched-coefficient checks;
- before/after guard bytes;
- `x19-x28` and AAPCS64 low-half `d8-d15` sentinels.

Observed results:

```text
canonical_unpack_chunk_u0_mismatches=0
canonical_unpack_chunk_u0_untouched_mismatches=0
canonical_unpack_chunk_u0_guard_mismatches=0
canonical_unpack_chunk_u0_abi_mask=0x0
canonical_unpack_chunk_u1_mismatches=0
canonical_unpack_chunk_u1_untouched_mismatches=0
canonical_unpack_chunk_u1_guard_mismatches=0
canonical_unpack_chunk_u1_abi_mask=0x0
canonical_unpack_full_u1_mismatches=0
canonical_unpack_full_u1_guard_mismatches=0
canonical_unpack_full_u1_abi_mask=0x0
```

Commands:

```sh
make -B test_gt_canonical_unpack_chunk_candidate
make -B test_gt_canonical_unpack_full_candidate
```

The generated chunk object is 844 text bytes for U0+U1.  The generated full U1
object is 4,400 text bytes under the Linux AArch64 cross-assembler.  Final
linked binary text and symbol alignment are deferred to the Pi 5 PMU run.

## Pi 5 decision

Raspberry Pi 5 Cortex-A76, core 3, `NTESTS=61`, `NITERATIONS=20000`:

| Scope | Variant | Cycles p50 | Instructions p50 | Paired delta | Wins |
|---|---|---:|---:|---:|---:|
| chunk | U0 | 52 | 124 | - | - |
| chunk | U1 | 53 | 120 | +1 | 0/61 |
| full unpack | production | 537 | 1158 | - | - |
| full unpack | U1 | 498 | 1110 | -39 | 61/61 |

The chunk result alone is misleading: U1 pays one extra cycle there, but its
whole-function schedule removes 39 cycles across all 12 chunks. The full KEM
same-binary result confirms that this survives real call contexts. With U1 and
production pack, encapsulation improves by 43.0 cycles and decapsulation by
101.6 cycles; both win 61/61 paired samples. Keypair is the zero-call control
and has identical retired instructions.

U1 was therefore selected and has since been promoted as the production
canonical-unpack implementation.

```sh
cd /home/pi/ntruplus/ntruplus-ntt-Optimized/aarch64-bench
make -B bench_gt_canonical_unpack_chunk_pmu
make -B bench_gt_canonical_unpack_full_pmu
```

Raw output is under
`aarch64-bench/results/serialization_candidates_2026-07-18/`.

## Post-F2 revalidation (2026-07-20)

Correctness, guards, and ABI sentinels still pass on the current production
tree. The chunk remains 52 cycles for U0 versus 53 for U1, while the complete
12-chunk function is 538 versus 498 cycles. U1 wins all 61 full-function pairs
by 39-40 cycles. Same-binary KEM PMU measures about 44 cycles saved in
encapsulation and 66 in decapsulation, so the global U1 production decision is
unchanged.
