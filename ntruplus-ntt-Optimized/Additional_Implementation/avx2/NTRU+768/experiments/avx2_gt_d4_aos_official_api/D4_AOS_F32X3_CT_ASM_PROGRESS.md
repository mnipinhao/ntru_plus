# F32X3 CT merged assembly progress

| Checkpoint | State | Evidence |
| --- | --- | --- |
| stage0 L0 | CORRECT | `gt_d4aos_f32x3_invntt32_stage0_asm`; 768 basis + 10,000 random states |
| merged L0-L2 | DISASSEMBLY_VERIFIED | `gt_d4aos_f32x3_invntt32_ct_merged_l0_l2_asm`; byte-exact L0/L1/L2 checkpoints, 768 basis, boundaries, and 10,000 random states under ASan/UBSan |
| merged L3-L4 | DISASSEMBLY_VERIFIED | `gt_d4aos_f32x3_invntt32_ct_merged_l3_l4_asm`; exact L3/L4 checkpoints |
| complete L0-L4 | DISASSEMBLY_VERIFIED | `gt_d4aos_f32x3_invntt32_ct_merged_asm`; 768 basis and 10,000 random states |
| Y1 Yang L0-L4 | DISASSEMBLY_VERIFIED | 48 Pass-A loads; median 456 TSC; exact equality |
| Y2 compact Yang | DISASSEMBLY_VERIFIED | looped rows; median 460 TSC; exact equality |
| compact inverse DFT3 probe | DISASSEMBLY_VERIFIED | 768/10,000/1,000 exact; paired delta 78-92 TSC |
| complete Y1 inverse | CORRECT_REJECTED_PERFORMANCE | 11,799 bytes; 874-886 TSC; no spill/materialization |
| complete Y2 inverse | CORRECT_REJECTED_PERFORMANCE | 4,413 bytes; 868-880 TSC; no spill/materialization |

## Merged L0-L2 record

- Experiment ID: `AVX2-GT-D4-AOS-F32X3-CT-MERGED-L0-L2-001`
- Generated-table digest: `03ae270c0656c0e64e74da3538546d3239cf34d8d4fd1343ecb0f968637a9963`
- Release contract: aligned, non-overlapping native input and post-L2 output; canonical R^0 lanes.
- Tile shape: four data YMMs for fixed `(row,j3,j4)` and all `(j1,j2)` values.
- Register allocation: ymm0-ymm3 data; ymm4 factor; ymm5 factor-qinv; ymm6-ymm10
  Montgomery/canonical temporaries; ymm12 q; ymm13 q-1; ymm14 zero; ymm11/ymm15 free.
- Release state traffic: 96 native-state YMM loads (bit-reversal pair formation), 48 final
  post-L2 YMM stores, and no L0/L1 semantic stores.
- Butterfly inventory: 48 L0, 24 L1, 24 L2; 48 Montgomery products.
- Release instruction inventory: 48 `vpmullw`, 96 `vpmulhw`, 336 `vpaddw`,
  384 `vpsubw`, 192 `vpermq`, zero `vpshufb`, zero `vperm2i128`.
- Public-table loads: 72 factor/qinv loads plus q and q-1.
- Symbol size: 12,274 bytes (`0x2ff2`); stack bytes: zero; calls: zero.
- Release source SHA-256: `df98453e0358c606e414d5110481aab17a91153c568ed43061077e0f6df033ed`.
- Release object SHA-256: `678e7537f677423458b3c686e6ee6874e7e3e1ff42f89d05b59a67f9496c6abb`.
- Release binary SHA-256: `48fa880411e841382fab9de0a59383a3684a13d32fea36c29f55939225d62f8b`.
- Preserved audit: `build/d4_aos_f32x3_invntt_avx2_asm.release.objdump` and
  `build/d4_aos_f32x3_ct_l0_l2.release.symbol.objdump`.

## Five-layer record

- L3/L4 generated digest: `323cd674bf9815f19c6980a6d358dd16b73bb47f96f06e5094d042d812291119`.
- Complete symbol size: 19,643 bytes; L3/L4-only size: 7,391 bytes.
- Complete instruction inventory: 96 `vpmullw`, 192 `vpmulhw`, 528 `vpaddw`,
  624 `vpsubw`, 192 `vpermq`, zero `vpshufb`, and zero `vperm2i128`.
- Complete semantic traffic: Pass A stores 48 post-L2 YMMs; Pass B loads those 48
  YMMs and stores 48 post-L4 YMMs. The output object is the single semantic state.
- Calls, stack bytes and YMM spills: zero.

## Complete terminal record

- Terminal digest: `9a609525c63981688f489497aeae59c9ceb29f832aa962322285b7cb0f6abbac`.
- Complete correctness: 768 basis, 768 q representatives, 10,000 random states and
  1,000 Forward/Basemul products; alias/range/natural order and ASan/UBSan pass.
- DFT3 materialization: none. Output: exactly 192 dynamic qword stores.
- One bounded repair reduced Y1/Y2 from about 1,084/1,082 to 876/868 representative
  TSC, but Y2 remains in the specified insufficient-return band.

Exact next checkpoint: `CLOSE_D4AOS_F32X3_TERMINAL_001_NO_PROMOTION`; retain the
experiment record and return optimization work to the current GT SoA champion.
