/* NTRU+1152 Forward stage one: alpha/beta CRT split into eight banks.
 *
 * Requires every input coefficient in [-3,4]; this is not a general-input API.
 * The bound matters: the split multiplies by -722 with a bare MUL and no
 * reduction, and |-722 * 4| = 2888 fits int16.
 *
 * Ported from NTRU+864's ntt_top.S.  Structural changes only:
 *
 *   LD3 -> LD4          three cubic branches become four quartic branches
 *   6 banks -> 8        2 tops x 4 components; bases 0,256,...,1792
 *   +864 -> +1152       the second half is 576 coefficients above the first
 *   stride 54 -> 72     9 m-values x 4 branches x 2 bytes
 *   tail 48 -> 64       8 m-values x 4 branches x 2 bytes
 *
 * The s=8 tail is simpler here than at 864.  Four halfwords is exactly one
 * LDR d, so the three-part load becomes one instruction; and 2 tops x 4
 * branches fills all eight lanes, so MOVI plus six INS becomes two MOV.
 * NTRU+864 dup'd q and a third constant into v29/v31 and never used them;
 * those are dropped.
 *
 * x0: 1152-int16 output, eight 256-byte banks then a 256-byte tail region
 * x1: 1152-int16 natural-order input
 *
 * For m = s + 9*t the second LD4 is 576 coefficients above the first:
 *     low  = a[4*(s + 9*t) + branch]
 *     high = a[4*(s + 9*(t+16)) + branch]
 */
.text
.p2align 2

.global ntt_top_asm
.global _ntt_top_asm
ntt_top_asm:
_ntt_top_asm:
    mov x2, x1
    add x3, x1, #1152

    /* Eight contiguous 16-vector banks: (alpha,b0..b3), (beta,b0..b3). */
    mov x4, x0
    add x5, x0, #256
    add x6, x0, #512
    add x7, x0, #768
    add x8, x0, #1024
    add x9, x0, #1280
    add x10, x0, #1536
    add x11, x0, #1792
    add x12, x0, #2048

    /* Copied unchanged from the NTRU+864 level-zero split. */
    mov w13, #0xfd2e
    dup v30.8h, w13

    mov w14, #16
.Ltop_split_loop:
    /* lanes 0..7 are residues s=0..7; v0..v3 and v4..v7 are quartic branches. */
    ld4 {v0.8h, v1.8h, v2.8h, v3.8h}, [x2]
    ld4 {v4.8h, v5.8h, v6.8h, v7.8h}, [x3]

    /* t_b = alpha * high_b, bare MUL under the [-3,4] input contract. */
    mul v16.8h, v4.8h, v30.8h
    mul v17.8h, v5.8h, v30.8h
    mul v18.8h, v6.8h, v30.8h
    mul v19.8h, v7.8h, v30.8h

    /* beta output = low + high - t, with beta = 1 - alpha. */
    add v20.8h, v0.8h, v4.8h
    add v21.8h, v1.8h, v5.8h
    add v22.8h, v2.8h, v6.8h
    add v23.8h, v3.8h, v7.8h
    sub v20.8h, v20.8h, v16.8h
    sub v21.8h, v21.8h, v17.8h
    sub v22.8h, v22.8h, v18.8h
    sub v23.8h, v23.8h, v19.8h

    /* alpha output = low + t. */
    add v16.8h, v0.8h, v16.8h
    add v17.8h, v1.8h, v17.8h
    add v18.8h, v2.8h, v18.8h
    add v19.8h, v3.8h, v19.8h

    str q16, [x4], #16
    str q17, [x5], #16
    str q18, [x6], #16
    str q19, [x7], #16
    str q20, [x8], #16
    str q21, [x9], #16
    str q22, [x10], #16
    str q23, [x11], #16

    /* s=8: exactly four halfwords per half, so one LDR d each.  At t=15 this
     * reads bytes 1144..1151 of a 1152-int16 input, so it stays in bounds. */
    add x15, x2, #64
    add x16, x3, #64
    ldr d0, [x15]
    ldr d1, [x16]

    mul v2.8h, v1.8h, v30.8h
    add v4.8h, v0.8h, v1.8h
    sub v4.8h, v4.8h, v2.8h
    add v2.8h, v0.8h, v2.8h

    /* One vector holds all eight (top,branch) tails, with no padding lane:
     * lanes 0..3 are top 0 branches 0..3, lanes 4..7 are top 1 branches 0..3,
     * matching bank = top*4 + component. */
    mov v5.d[0], v2.d[0]
    mov v5.d[1], v4.d[0]
    str q5, [x12], #16

    /* 9 values of m times 4 interleaved branches = 72 bytes per t. */
    add x2, x2, #72
    add x3, x3, #72
    subs w14, w14, #1
    b.ne .Ltop_split_loop
    ret

#if defined(__ELF__)
.section .note.GNU-stack,"",%progbits
#endif
