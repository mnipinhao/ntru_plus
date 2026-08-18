# Complete F32X3 inverse assembly report

The default-off complete symbols are:

- `gt_d4aos_f32x3_yang_invntt_avx2_asm` (Y1), 11,799 bytes.
- `gt_d4aos_f32x3_yang_compact_invntt_avx2_asm` (Y2), 4,413 bytes.

Both implement native F32X3 -> five-layer NTT32 -> compact DFT3 -> immediate Barrett ->
direct fused CRT terminal -> canonical natural coefficients. They share the DFT3 and
terminal macros and differ only in the frozen producer. The supported out==input alias
uses the single 1,536-byte semantic state.

Correctness: all existing L0/L1/L2/L3/L4 checkpoints pass; complete Y1/Y2 pass zero,
768 physical basis states, 768 q-representative states, 10,000 deterministic native
states, 1,000 Forward/Basemul products, alias, range and natural-order checks under
ASan/UBSan.

Release audit: no calls, no YMM spill, no DFT3-result store/reload, no old 4x8 transpose,
and no coefficient scalar loop. Dynamic traffic is 48 native input YMM loads, 96
transform-state loads, 96 transform-state stores, 48 DFT3 row loads, zero DFT3-result
stores, and exactly 192 output qword stores. The one semantic state is 1,536 bytes.

Selected static instruction inventory (loop bodies counted once):

| Instruction | Y1 | Y2 |
| --- | ---: | ---: |
| `vpmullw` | 205 | 77 |
| `vpmulhw` | 212 | 84 |
| `vpmulhrsw` | 96 | 32 |
| `vpaddw` | 246 | 86 |
| `vpsubw` | 356 | 132 |
| `vpsraw` | 6 | 6 |
| `vpermq` | 192 | 64 |
| `vperm2i128` | 3 | 3 |
| `vpblendd` | 96 | 32 |
| `vextracti128` / `vpextrq` / `vmovq` | 3 / 6 / 6 | 3 / 6 / 6 |

Post-repair source SHA-256 is
`1cb163c78eb902a1dc3b35431433e0147653063eb9bde64b932038030e482a6f` and object
SHA-256 is `1946448b162c81e71f8df63b65ad5094423e283ea434484578f6b472e1436548`.
The object and objdump are preserved as `build/d4_aos_f32x3_complete.direct_crt.release.*`.
