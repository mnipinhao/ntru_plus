/* P36 probes: issue-limited floors for the two inverse transforms' exact
 * multiply multisets, all chains independent.
 *
 *   GT        packed_i9 x16 (19,19,19) + invntt16_asm x8 (51,49,51)
 *             + invntt16_tail x1 (50,49,50) + crepmod3 x36 (4,0,4)
 *           = 906 mls + 745 mul + 906 sqrdmulh = 2557
 *   official  _looptop_6543 x18 (20,16,20) + _looptop_210 x8 (69,63,69)
 *             + poly_crepmod3 x36 (4,0,4)
 *           = 1056 mls + 792 mul + 1056 sqrdmulh = 2904
 *
 * Both entries save d8-d15: P34's lesson, learned the hard way.
 */
.text
.p2align 2

.macro SAVE_D
    stp d8,  d9,  [sp, #-64]!
    stp d10, d11, [sp, #16]
    stp d12, d13, [sp, #32]
    stp d14, d15, [sp, #48]
.endm
.macro RESTORE_D
    ldp d10, d11, [sp, #16]
    ldp d12, d13, [sp, #32]
    ldp d14, d15, [sp, #48]
    ldp d8,  d9,  [sp], #64
.endm

/* six independent destinations per mnemonic, so nothing waits on anything */
.macro SIX op
    \op v16.8h, v1.8h, v2.8h
    \op v17.8h, v3.8h, v4.8h
    \op v18.8h, v5.8h, v6.8h
    \op v19.8h, v7.8h, v1.8h
    \op v20.8h, v2.8h, v3.8h
    \op v21.8h, v4.8h, v5.8h
.endm

/* GT: 906 = 151x6, 745 = 124x6 + 1, 906 = 151x6 */
.global floor_inv_gt_asm
floor_inv_gt_asm:
    SAVE_D
    .rept 151
        SIX mls
    .endr
    .rept 124
        SIX mul
    .endr
    mul v22.8h, v1.8h, v2.8h
    .rept 151
        SIX sqrdmulh
    .endr
    RESTORE_D
    ret

/* official: 1056 = 176x6, 792 = 132x6, 1056 = 176x6 */
.global floor_inv_off_asm
floor_inv_off_asm:
    SAVE_D
    .rept 176
        SIX mls
    .endr
    .rept 132
        SIX mul
    .endr
    .rept 176
        SIX sqrdmulh
    .endr
    RESTORE_D
    ret

#if defined(__ELF__)
.section .note.GNU-stack,"",%progbits
#endif
