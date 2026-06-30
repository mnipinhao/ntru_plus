# Forward NTT Production Contract Audit

Date: 2026-06-30

Scope: documentation and target selection only.  No Slothy run was performed,
no `.opt.s` candidate was generated, and production defaults were not changed.

## Production Entrypoint

The production Forward NTT entrypoint is:

```text
poly_ntt / _poly_ntt
gt_block_major_poly_ntt / _gt_block_major_poly_ntt
```

Current production source wiring is Makefile-driven, not inferred from file
names:

| build path | production NTT setting | source files |
| --- | --- | --- |
| `Additional_Implementation/aarch64/NTRU+768/Makefile` | `GT_NTT_ASM ?= $(GT_NTT_ASM_PHASE123_N1)` | `asm/my_ntt_phase123_n1.s`, `asm/slothy/my_32ntt.opt.s` |
| `aarch64-bench/Makefile` | `GT_PRODUCTION_NTT_ASM ?= $(NTRUPLUS)/asm/my_ntt_phase123_n1.s` and `GT_PRODUCTION_NTT32_ASM ?= $(NTRUPLUS)/asm/slothy/my_32ntt.opt.s` | same production pair |

`asm/my_ntt_phase123_n1.s` is a thin production wrapper that includes
`asm/my_ntt.s`.  The wrapper in `asm/my_ntt.s` emits the public symbols above,
includes the scheduled Phase123 body from `asm/slothy/my_ntt_phase123.n1.opt.s`,
and calls `_ntt32_8way` from `asm/slothy/my_32ntt.opt.s` three times.

The three `_ntt32_8way` calls use row offsets:

```text
row0 scatter base = dst + 0
row1 scatter base = dst + 256
row2 scatter base = dst + 512
```

This is the active production default.  The direct-tuple and BPQ variants are
selected only by separate candidate wrappers/macros and are not production
defaults.

## KEM Callers

Current `kem.c` Forward NTT call sites:

| API path | call site | role | direct consumer |
| --- | --- | --- | --- |
| keygen `genf_derand` | `poly_ntt(f, f)` | transform secret `f` | `KEYPAIR_BASEINV(finv, f)` and `poly_tobytes(sk, f)` |
| keygen `geng_derand` | `poly_ntt(g, g)` | transform secret/public arithmetic operand `g` | `KEYPAIR_BASEINV(ginv, g)` |
| keygen public arithmetic | transformed `f/g/finv/ginv` | NTT-domain multiplication | `KEYPAIR_BASEMUL(&h, g, finv)`, `KEYPAIR_BASEMUL(&hinv, f, ginv)`, `poly_tobytes(pk, &h)` |
| encap randomness path | `poly_ntt(&r, &r)` | transform sampled `r` | `poly_tobytes(buf2, &r)`, `hash_g`, `gt_encap_basemul_add_tobytes_contract(ct, &h, &r, &m)` |
| encap message path | `poly_ntt(&m, &m)` | transform SOTP-encoded message | `gt_encap_basemul_add_tobytes_contract` |
| decap message verify path | `poly_ntt(&m2, &m1)` | transform recovered message | `poly_sub(&c, &c, &m2)` before verify basemul |
| decap re-encryption path | `poly_ntt(&r1, &r1)` | transform regenerated `r1` | `poly_tobytes(buf2, &r1)` and byte comparison |

Forward NTT therefore affects keygen, encap, and decap.  It is not one huge
single block in any API, but it is reused enough that a real production-window
win can matter across the KEM.

## Input Contract

Input is a natural-order `poly` with 768 signed 16-bit coefficients.  The caller
supplies ordinary polynomial-domain data from CBD/triple/SOTP/crepmod3 paths.
The Forward NTT wrapper may be in-place or out-of-place through the normal
`poly_ntt(dst, src)` ABI.

The contract to preserve for Slothy candidates:

- Natural coefficient order at input.
- Same modular value as the C reference NTT.
- Same representative/range contract expected by downstream GT arithmetic and
  serialization tests.
- Constant-time behavior; specialization may depend only on compile-time row or
  block constants.

## Output Layout Contract

Production output is GT block-major row-bitrev layout.  It is not tuple,
rowpack, BPQ, or TMVP evalpack.

`asm/slothy/my_32ntt.opt.s` completes each NTT32 row and scatters reduced output
directly to the final `poly_ntt` destination.  The final layout is:

```text
branch in {0,1}
physical block j in 0..95
quartic coefficient lane in 0..3
memory index = branch * 384 + 4 * j + lane
```

The physical block `j` is already row-bitrev Good-Thomas order.  The
`gt_rowbitrev_lambda[branch][j]` table in `ntt.c` is arranged for this physical
order, so consumers do not perform a separate output reorder.

Consumer contract:

- `poly_baseinv` and keygen batch base inverse read block-major row-bitrev NTT
  blocks.
- `poly_basemul`, `poly_basemul_rminus1`,
  `poly_basemul_scaled_r_input`, and `poly_basemul_add` read block-major
  row-bitrev operands and the matching `gt_rowbitrev_lambda` physical order.
- `poly_tobytes` serializes the current physical representation for public key,
  ciphertext, and verify buffers.  Changing Forward NTT output layout changes
  bytes unless every consumer and packing path is changed together.
- Decap `poly_sub(&c, &c, &m2)` assumes `c` from ciphertext unpacking and `m2`
  from Forward NTT use the exact same production NTT-domain layout.

## PMU Context

Latest target-selection context:

| component | cycles/call | API share |
| --- | ---: | ---: |
| `encap_ntt_r` | 2704.884 | 7.1% encap |
| `encap_ntt_m` | 2704.136 | 7.1% encap |
| `decap_ntt_m1` | 2710.132 | 8.1% decap |
| `decap_ntt_r1` | 2705.003 | 8.1% decap |

Forward NTT is a repeated local target.  A Forward NTT Slothy campaign is only
worth running against production-layout windows with PMU repeatability, not
against historical source-order or alternative-layout experiments.

## Active And Dead Routes

| route | files / flags | status | reason |
| --- | --- | --- | --- |
| production block-major | `asm/my_ntt_phase123_n1.s`, `asm/my_ntt.s`, `asm/slothy/my_ntt_phase123.n1.opt.s`, `asm/slothy/my_32ntt.opt.s` | active production default | emits `poly_ntt` / `gt_block_major_poly_ntt`; output is GT block-major row-bitrev |
| rowspec / shadow-base | `asm/my_ntt_shadow_base*.s`, `asm/slothy/my_32ntt.shadow_base*.s`, `gt_test/test_gt_ntt_shadow_base*.c` | experimental / stopped | benchmark-only route; previous rowspec/source-order scheduling did not provide promotion evidence |
| direct tuple / Candidate A | `asm/my_ntt_candidate_a_direct_tuple.s`, `MY_NTT_DIRECT_TUPLE`, `asm/slothy/ntt32_8way.to_tuple.n1.opt.s` | experimental / not production | writes tuple layout for TMVP experiments; not the production output contract |
| BPQ / Candidate B | `asm/my_ntt_candidate_b_bpq.s`, `MY_NTT_BRANCH_PAIR_Q`, `asm/slothy/ntt32_8way.to_bpq.n1.opt.s` | experimental / not production | BPQ branch-pair layout candidate; not production |
| rowpack | `asm/slothy/ntt32_8way.rowpack_v*.s`, rowpack docs/tests | experimental / not production | alternative SoA/rowpack layout; does not match production consumers |
| oldstore / ldrtrn | basemul oldstore and ldrtrn wrapper files | dead for Forward NTT | basemul load/store experiments, not the Forward NTT production path |
| source-order local windows | symbolic/canonical slices detached from production scheduling | rejected as promotion route | small source-order local Slothy windows can pass model/correctness and still regress on Pi5 PMU |

## Slothy Readiness

Status: `ready_for_window_manifest`, not ready for an immediate Slothy run.

The production output layout is clear: GT block-major row-bitrev.  That removes
the previous ambiguity around tuple/rowpack/BPQ naming.  However, the recent
InvNTT and basemul campaigns show that a small source-order local window is not
enough.  Before running Slothy, Forward NTT needs a production-only window
manifest with live-in/live-out, memory write, row offset, and final-store
contracts.

Candidate windows to document in that manifest:

| candidate | source anchor | readiness | notes |
| --- | --- | --- | --- |
| Phase123 iteration windows | markers in `asm/slothy/my_ntt_phase123.n1.opt.s` | audit first | production-scheduled already; avoid detached source-order Phase123 windows |
| NTT32 stage12 grouped stripes | `_ntt32_stage12_stripe*` markers in `asm/slothy/my_32ntt.opt.s` | needs grouping | individual stripes may be too small for normal Slothy policy |
| NTT32 stage345 block windows | `_ntt32_stage345_block*` markers in `asm/slothy/my_32ntt.opt.s` | likely first serious area | output-layout and scatter-store sensitive; document exact store map before running |
| final reduction/store subwindow | inside stage345 blocks | needs explicit contract | preserve block-major row-bitrev output; do not silently switch to tuple/rowpack/BPQ |

## Blockers And Next Action

Blockers before any Forward NTT Slothy campaign:

1. Write a production-only Forward NTT window manifest.
2. Pin the block-major row-bitrev store map and consumer contract in the
   manifest.
3. Choose windows from production-scheduled sources, not old source-order
   symbolic slices.
4. Define benchmark-only integration that compares production
   `gt_block_major_poly_ntt` against the candidate and the KEM component
   profile.
5. Require correctness, Pi5 PMU, and repeat/non-regression before recording a
   current best.

Recommended target-tracker state:

```yaml
forward_ntt_production_windows:
  status: ready_for_window_manifest
  reason: production block-major row-bitrev output contract is now clear; run
    no Slothy campaign until a production-only manifest and PMU plan exist
```
