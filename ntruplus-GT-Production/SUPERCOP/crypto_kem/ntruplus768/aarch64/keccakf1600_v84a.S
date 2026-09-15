/*
 * Copyright (c) The mlkem-native project authors
 * Copyright (c) 2021-2022 Arm Limited
 * Copyright (c) 2022 Matthias Kannwischer
 * SPDX-License-Identifier: Apache-2.0 OR ISC OR MIT
 */

/* References
 * ==========
 *
 * - [HYBRID]
 *   Hybrid scalar/vector implementations of Keccak and SPHINCS+ on AArch64
 *   Becker, Kannwischer
 *   https://eprint.iacr.org/2022/1243
 */

/*yaml
  Name: ntruplus_keccak_f1600_x1_v84a_aarch64
  Description: AArch64 ARMv8.4-A implementation of Keccak-f[1600] permutation for single state
  Signature: void ntruplus_keccak_f1600_x1_v84a_aarch64(uint64_t state[25], const uint64_t rc[24])
  ABI:
    Architecture: aarch64
    CallingConvention: AAPCS64
    Features: [NEON, SHA3]
    x0:
      type: buffer
      size_bytes: 200
      permissions: read/write
      c_parameter: uint64_t state[25]
      description: Keccak state (25 x uint64_t)
    x1:
      type: buffer
      size_bytes: 192
      permissions: read-only
      c_parameter: const uint64_t rc[24]
      description: Round constants (24 x uint64_t)
  Stack:
    bytes: 64
    description: register preservation
*/

//
// Author: Hanno Becker <hanno.becker@arm.com>
// Author: Matthias Kannwischer <matthias@kannwischer.eu>
//
// This implementation is essentially from the paper @[HYBRID].
// The only difference is interleaving/deinterleaving of Keccak state
// during load and store, so that the caller need not do this.
//

#if defined(__ARM_FEATURE_SHA3)

/*
 * Imported from mlkem-native revision
 * 438f0da19dc3d5299bb2e318d1067f9a298f1bcf.
 * Generated upstream source SHA-256:
 * 8f7841f3c130549ccc64af236e8b8d6f811cba1cdafd83a8b12424476973d3da
 * The upstream round body is kept instruction-for-instruction in the macro.
 * NTRU+ adapts symbols/sections and adds the fixed-size hash_g sponge around a
 * second expansion of that body. The fused integration is not claimed to be
 * covered by the upstream formal-verification artifact.
 */
.macro NTRUPLUS_KECCAK_V84A_PERMUTE
        mov x2, #0x18               // =24

Lntruplus_keccak_f1600_x1_v84a_loop_\@:
        eor3 v30.16b, v0.16b, v5.16b, v10.16b
        eor3 v29.16b, v1.16b, v6.16b, v11.16b
        eor3 v28.16b, v2.16b, v7.16b, v12.16b
        eor3 v27.16b, v3.16b, v8.16b, v13.16b
        eor3 v26.16b, v4.16b, v9.16b, v14.16b
        eor3 v30.16b, v30.16b, v15.16b, v20.16b
        eor3 v29.16b, v29.16b, v16.16b, v21.16b
        eor3 v28.16b, v28.16b, v17.16b, v22.16b
        eor3 v27.16b, v27.16b, v18.16b, v23.16b
        eor3 v26.16b, v26.16b, v19.16b, v24.16b
        rax1 v25.2d, v30.2d, v28.2d
        rax1 v28.2d, v28.2d, v26.2d
        rax1 v26.2d, v26.2d, v29.2d
        rax1 v29.2d, v29.2d, v27.2d
        rax1 v27.2d, v27.2d, v30.2d
        eor v30.16b, v0.16b, v26.16b
        xar v0.2d, v2.2d, v29.2d, #0x2
        xar v2.2d, v12.2d, v29.2d, #0x15
        xar v12.2d, v13.2d, v28.2d, #0x27
        xar v13.2d, v19.2d, v27.2d, #0x38
        xar v19.2d, v23.2d, v28.2d, #0x8
        xar v23.2d, v15.2d, v26.2d, #0x17
        xar v15.2d, v1.2d, v25.2d, #0x3f
        xar v1.2d, v8.2d, v28.2d, #0x9
        xar v8.2d, v16.2d, v25.2d, #0x13
        xar v16.2d, v7.2d, v29.2d, #0x3a
        xar v7.2d, v10.2d, v26.2d, #0x3d
        xar v10.2d, v3.2d, v28.2d, #0x24
        xar v3.2d, v18.2d, v28.2d, #0x2b
        xar v18.2d, v17.2d, v29.2d, #0x31
        xar v17.2d, v11.2d, v25.2d, #0x36
        xar v11.2d, v9.2d, v27.2d, #0x2c
        xar v9.2d, v22.2d, v29.2d, #0x3
        xar v22.2d, v14.2d, v27.2d, #0x19
        xar v14.2d, v20.2d, v26.2d, #0x2e
        xar v20.2d, v4.2d, v27.2d, #0x25
        xar v4.2d, v24.2d, v27.2d, #0x32
        xar v24.2d, v21.2d, v25.2d, #0x3e
        xar v21.2d, v5.2d, v26.2d, #0x1c
        xar v27.2d, v6.2d, v25.2d, #0x14
        ld1r { v31.2d }, [x1], #8
        bcax v5.16b, v10.16b, v7.16b, v11.16b
        bcax v6.16b, v11.16b, v8.16b, v7.16b
        bcax v7.16b, v7.16b, v9.16b, v8.16b
        bcax v8.16b, v8.16b, v10.16b, v9.16b
        bcax v9.16b, v9.16b, v11.16b, v10.16b
        bcax v10.16b, v15.16b, v12.16b, v16.16b
        bcax v11.16b, v16.16b, v13.16b, v12.16b
        bcax v12.16b, v12.16b, v14.16b, v13.16b
        bcax v13.16b, v13.16b, v15.16b, v14.16b
        bcax v14.16b, v14.16b, v16.16b, v15.16b
        bcax v15.16b, v20.16b, v17.16b, v21.16b
        bcax v16.16b, v21.16b, v18.16b, v17.16b
        bcax v17.16b, v17.16b, v19.16b, v18.16b
        bcax v18.16b, v18.16b, v20.16b, v19.16b
        bcax v19.16b, v19.16b, v21.16b, v20.16b
        bcax v20.16b, v0.16b, v22.16b, v1.16b
        bcax v21.16b, v1.16b, v23.16b, v22.16b
        bcax v22.16b, v22.16b, v24.16b, v23.16b
        bcax v23.16b, v23.16b, v0.16b, v24.16b
        bcax v24.16b, v24.16b, v1.16b, v0.16b
        bcax v0.16b, v30.16b, v2.16b, v27.16b
        bcax v1.16b, v27.16b, v3.16b, v2.16b
        bcax v2.16b, v2.16b, v4.16b, v3.16b
        bcax v3.16b, v3.16b, v30.16b, v4.16b
        bcax v4.16b, v4.16b, v27.16b, v30.16b
        eor v0.16b, v0.16b, v31.16b
        sub x2, x2, #0x1
        cbnz x2, Lntruplus_keccak_f1600_x1_v84a_loop_\@
.endm

#ifdef __APPLE__
.text
#else
.section .text.module_keccakf1600_v84a_body,"ax",%progbits
#endif
.balign 4
.global ntruplus_keccak_f1600_x1_v84a_aarch64
.global _ntruplus_keccak_f1600_x1_v84a_aarch64
#ifndef __APPLE__
.type ntruplus_keccak_f1600_x1_v84a_aarch64, %function
#endif
ntruplus_keccak_f1600_x1_v84a_aarch64:
_ntruplus_keccak_f1600_x1_v84a_aarch64:

        .cfi_startproc
        sub sp, sp, #0x40
        .cfi_adjust_cfa_offset 0x40
        stp d8, d9, [sp]
        .cfi_rel_offset d8, 0x0
        .cfi_rel_offset d9, 0x8
        stp d10, d11, [sp, #0x10]
        .cfi_rel_offset d10, 0x10
        .cfi_rel_offset d11, 0x18
        stp d12, d13, [sp, #0x20]
        .cfi_rel_offset d12, 0x20
        .cfi_rel_offset d13, 0x28
        stp d14, d15, [sp, #0x30]
        .cfi_rel_offset d14, 0x30
        .cfi_rel_offset d15, 0x38
        ldp d0, d1, [x0]
        ldp d2, d3, [x0, #0x10]
        ldp d4, d5, [x0, #0x20]
        ldp d6, d7, [x0, #0x30]
        ldp d8, d9, [x0, #0x40]
        ldp d10, d11, [x0, #0x50]
        ldp d12, d13, [x0, #0x60]
        ldp d14, d15, [x0, #0x70]
        ldp d16, d17, [x0, #0x80]
        ldp d18, d19, [x0, #0x90]
        ldp d20, d21, [x0, #0xa0]
        ldp d22, d23, [x0, #0xb0]
        ldr d24, [x0, #0xc0]
        NTRUPLUS_KECCAK_V84A_PERMUTE
        stp d0, d1, [x0]
        stp d2, d3, [x0, #0x10]
        stp d4, d5, [x0, #0x20]
        stp d6, d7, [x0, #0x30]
        stp d8, d9, [x0, #0x40]
        stp d10, d11, [x0, #0x50]
        stp d12, d13, [x0, #0x60]
        stp d14, d15, [x0, #0x70]
        stp d16, d17, [x0, #0x80]
        stp d18, d19, [x0, #0x90]
        stp d20, d21, [x0, #0xa0]
        stp d22, d23, [x0, #0xb0]
        str d24, [x0, #0xc0]
        ldp d8, d9, [sp]
        .cfi_restore d8
        .cfi_restore d9
        ldp d10, d11, [sp, #0x10]
        .cfi_restore d10
        .cfi_restore d11
        ldp d12, d13, [sp, #0x20]
        .cfi_restore d12
        .cfi_restore d13
        ldp d14, d15, [sp, #0x30]
        .cfi_restore d14
        .cfi_restore d15
        add sp, sp, #0x40
        .cfi_adjust_cfa_offset -0x40
        ret
        .cfi_endproc

#ifndef __APPLE__
.size ntruplus_keccak_f1600_x1_v84a_aarch64, .-ntruplus_keccak_f1600_x1_v84a_aarch64
#endif

/* Internal live-state permutation. Callers preserve d8-d15. */
Lntruplus_keccak_f1600_x1_v84a_live:
        NTRUPLUS_KECCAK_V84A_PERMUTE
        ret

/* Fixed hash_g: x0=out[192], x1=msg[1152], x2=rc[24].
 * Input and output may alias. All input is absorbed before the first store.
 */
#ifdef __APPLE__
.text
#else
.section .text.module_hash_g_fused_v84a_body,"ax",%progbits
#endif
.balign 4
.global ntruplus_hash_g_fused_v84a_aarch64
.global _ntruplus_hash_g_fused_v84a_aarch64
#ifndef __APPLE__
.type ntruplus_hash_g_fused_v84a_aarch64, %function
#endif
ntruplus_hash_g_fused_v84a_aarch64:
_ntruplus_hash_g_fused_v84a_aarch64:
        .cfi_startproc
        sub sp, sp, #0x50
        .cfi_adjust_cfa_offset 0x50
        stp d8, d9, [sp]
        .cfi_rel_offset d8, 0x0
        .cfi_rel_offset d9, 0x8
        stp d10, d11, [sp, #0x10]
        .cfi_rel_offset d10, 0x10
        .cfi_rel_offset d11, 0x18
        stp d12, d13, [sp, #0x20]
        .cfi_rel_offset d12, 0x20
        .cfi_rel_offset d13, 0x28
        stp d14, d15, [sp, #0x30]
        .cfi_rel_offset d14, 0x30
        .cfi_rel_offset d15, 0x38
        str x30, [sp, #0x40]
        .cfi_rel_offset x30, 0x40
        mov x3, x0
        mov x4, x1
        mov x5, x2

        ldr x6, [x4]
        lsl x6, x6, #8
        orr x6, x6, #1
        fmov d0, x6
        ldur d1, [x4, #7]
        ldur d2, [x4, #15]
        ldur d3, [x4, #23]
        ldur d4, [x4, #31]
        ldur d5, [x4, #39]
        ldur d6, [x4, #47]
        ldur d7, [x4, #55]
        ldur d8, [x4, #63]
        ldur d9, [x4, #71]
        ldur d10, [x4, #79]
        ldur d11, [x4, #87]
        ldur d12, [x4, #95]
        ldur d13, [x4, #103]
        ldur d14, [x4, #111]
        ldur d15, [x4, #119]
        ldur d16, [x4, #127]
        movi v17.2d, #0
        movi v18.2d, #0
        movi v19.2d, #0
        movi v20.2d, #0
        movi v21.2d, #0
        movi v22.2d, #0
        movi v23.2d, #0
        movi v24.2d, #0
        mov x1, x5
        bl Lntruplus_keccak_f1600_x1_v84a_live

        add x4, x4, #135
        mov x7, #7
Lntruplus_hash_g_v84a_full:
        ldr d25, [x4, #0]
        eor v0.8b, v0.8b, v25.8b
        ldr d25, [x4, #8]
        eor v1.8b, v1.8b, v25.8b
        ldr d25, [x4, #16]
        eor v2.8b, v2.8b, v25.8b
        ldr d25, [x4, #24]
        eor v3.8b, v3.8b, v25.8b
        ldr d25, [x4, #32]
        eor v4.8b, v4.8b, v25.8b
        ldr d25, [x4, #40]
        eor v5.8b, v5.8b, v25.8b
        ldr d25, [x4, #48]
        eor v6.8b, v6.8b, v25.8b
        ldr d25, [x4, #56]
        eor v7.8b, v7.8b, v25.8b
        ldr d25, [x4, #64]
        eor v8.8b, v8.8b, v25.8b
        ldr d25, [x4, #72]
        eor v9.8b, v9.8b, v25.8b
        ldr d25, [x4, #80]
        eor v10.8b, v10.8b, v25.8b
        ldr d25, [x4, #88]
        eor v11.8b, v11.8b, v25.8b
        ldr d25, [x4, #96]
        eor v12.8b, v12.8b, v25.8b
        ldr d25, [x4, #104]
        eor v13.8b, v13.8b, v25.8b
        ldr d25, [x4, #112]
        eor v14.8b, v14.8b, v25.8b
        ldr d25, [x4, #120]
        eor v15.8b, v15.8b, v25.8b
        ldr d25, [x4, #128]
        eor v16.8b, v16.8b, v25.8b
        add x4, x4, #136
        mov x1, x5
        bl Lntruplus_keccak_f1600_x1_v84a_live
        subs x7, x7, #1
        b.ne Lntruplus_hash_g_v84a_full

        ldr d25, [x4, #0]
        eor v0.8b, v0.8b, v25.8b
        ldr d25, [x4, #8]
        eor v1.8b, v1.8b, v25.8b
        ldr d25, [x4, #16]
        eor v2.8b, v2.8b, v25.8b
        ldr d25, [x4, #24]
        eor v3.8b, v3.8b, v25.8b
        ldr d25, [x4, #32]
        eor v4.8b, v4.8b, v25.8b
        ldr d25, [x4, #40]
        eor v5.8b, v5.8b, v25.8b
        ldr d25, [x4, #48]
        eor v6.8b, v6.8b, v25.8b
        ldr d25, [x4, #56]
        eor v7.8b, v7.8b, v25.8b
        ldrb w6, [x4, #64]
        orr x6, x6, #0x1f00
        fmov d25, x6
        eor v8.8b, v8.8b, v25.8b
        mov x6, #0x8000000000000000
        fmov d25, x6
        eor v16.8b, v16.8b, v25.8b
        mov x1, x5
        bl Lntruplus_keccak_f1600_x1_v84a_live

        stp d0, d1, [x3, #0]
        stp d2, d3, [x3, #16]
        stp d4, d5, [x3, #32]
        stp d6, d7, [x3, #48]
        stp d8, d9, [x3, #64]
        stp d10, d11, [x3, #80]
        stp d12, d13, [x3, #96]
        stp d14, d15, [x3, #112]
        str d16, [x3, #128]
        mov x1, x5
        bl Lntruplus_keccak_f1600_x1_v84a_live
        stp d0, d1, [x3, #136]
        stp d2, d3, [x3, #152]
        stp d4, d5, [x3, #168]
        str d6, [x3, #184]

        movi v0.16b, #0
        movi v1.16b, #0
        movi v2.16b, #0
        movi v3.16b, #0
        movi v4.16b, #0
        movi v5.16b, #0
        movi v6.16b, #0
        movi v7.16b, #0
        movi v8.16b, #0
        movi v9.16b, #0
        movi v10.16b, #0
        movi v11.16b, #0
        movi v12.16b, #0
        movi v13.16b, #0
        movi v14.16b, #0
        movi v15.16b, #0
        movi v16.16b, #0
        movi v17.16b, #0
        movi v18.16b, #0
        movi v19.16b, #0
        movi v20.16b, #0
        movi v21.16b, #0
        movi v22.16b, #0
        movi v23.16b, #0
        movi v24.16b, #0
        movi v25.16b, #0
        movi v26.16b, #0
        movi v27.16b, #0
        movi v28.16b, #0
        movi v29.16b, #0
        movi v30.16b, #0
        movi v31.16b, #0
        ldr x30, [sp, #0x40]
        .cfi_restore x30
        ldp d8, d9, [sp]
        .cfi_restore d8
        .cfi_restore d9
        ldp d10, d11, [sp, #0x10]
        .cfi_restore d10
        .cfi_restore d11
        ldp d12, d13, [sp, #0x20]
        .cfi_restore d12
        .cfi_restore d13
        ldp d14, d15, [sp, #0x30]
        .cfi_restore d14
        .cfi_restore d15
        add sp, sp, #0x50
        .cfi_adjust_cfa_offset -0x50
        ret
        .cfi_endproc
#ifndef __APPLE__
.size ntruplus_hash_g_fused_v84a_aarch64, .-ntruplus_hash_g_fused_v84a_aarch64
#endif

#endif /* __ARM_FEATURE_SHA3 */


#if defined(__ELF__)
.section .note.GNU-stack,"",%progbits
#endif
