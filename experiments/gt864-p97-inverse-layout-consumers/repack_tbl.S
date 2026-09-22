/* Layout-free invntt16 output -> natural order, in one pass.
 *
 * The natural index is 27*(t+16h) + 3j + c.  The free layout puts j in the
 * lanes, c in the 128-halfword block, and h in the lane halves, so a group's
 * 24 main coefficients are one ZIP of each c-block followed by one ST3 --
 * ST3's interleave-by-three IS the 3j + c axis.  j = 8 rides along as a
 * single-lane ST3 at offset 24.
 *
 * x0 natural out (864 int16)   x1 free main (6 x 128 halfwords)
 * x2 free tail (3 c-blocks x 32 groups)
 */
#ifdef __APPLE__
#define repack_tbl_asm _repack_tbl_asm
#endif
.section __TEXT,__const
.p2align 4
repack_idx:
    .byte 0,1,16,17,32,33,2,3,18,19,34,35,4,5,20,21
    .byte 36,37,6,7,22,23,38,39,8,9,24,25,40,41,10,11
    .byte 26,27,42,43,12,13,28,29,44,45,14,15,30,31,46,47
.text
.global repack_tbl_asm
repack_tbl_asm:
    .macro TAILQ off
    ldr q24, [x2, #\off]            // c=0, h=0 groups
    ldr q25, [x2, #64+\off]         // c=1
    ldr q26, [x2, #128+\off]        // c=2
    ldr q27, [x2, #32+\off]         // c=0, h=1 groups
    ldr q28, [x2, #96+\off]
    ldr q29, [x2, #160+\off]
    .endm

    .macro GROUP t, lane
    ldr q0, [x1, #(16*\t)]
    ldr q1, [x1, #(256+16*\t)]
    ldr q2, [x1, #(512+16*\t)]
    ldr q3, [x1, #(768+16*\t)]
    ldr q4, [x1, #(1024+16*\t)]
    ldr q5, [x1, #(1280+16*\t)]
    zip1 v16.2d, v0.2d, v1.2d       // c=0, j=0..7, h=0
    zip1 v17.2d, v2.2d, v3.2d       // c=1
    zip1 v18.2d, v4.2d, v5.2d       // c=2
    add  x3, x0, #(54*\t)
    tbl  v6.16b, {v16.16b, v17.16b, v18.16b}, v13.16b
    tbl  v7.16b, {v16.16b, v17.16b, v18.16b}, v14.16b
    tbl  v8.16b, {v16.16b, v17.16b, v18.16b}, v15.16b
    str  q6, [x3]
    str  q7, [x3, #16]
    str  q8, [x3, #32]
    add  x5, x3, #48
    st3  {v24.h, v25.h, v26.h}[\lane], [x5]
    zip2 v19.2d, v0.2d, v1.2d       // the h=1 group, 16 groups on
    zip2 v20.2d, v2.2d, v3.2d
    zip2 v21.2d, v4.2d, v5.2d
    add  x4, x0, #(54*(\t+16))
    tbl  v9.16b,  {v19.16b, v20.16b, v21.16b}, v13.16b
    tbl  v10.16b, {v19.16b, v20.16b, v21.16b}, v14.16b
    tbl  v11.16b, {v19.16b, v20.16b, v21.16b}, v15.16b
    str  q9,  [x4]
    str  q10, [x4, #16]
    str  q11, [x4, #32]
    add  x6, x4, #48
    st3  {v27.h, v28.h, v29.h}[\lane], [x6]
    .endm

    adrp x7, repack_idx@PAGE
    add  x7, x7, repack_idx@PAGEOFF
    ldr  q13, [x7]
    ldr  q14, [x7, #16]
    ldr  q15, [x7, #32]
    TAILQ 0
    GROUP 0,0
    GROUP 1,1
    GROUP 2,2
    GROUP 3,3
    GROUP 4,4
    GROUP 5,5
    GROUP 6,6
    GROUP 7,7
    TAILQ 16
    GROUP 8,0
    GROUP 9,1
    GROUP 10,2
    GROUP 11,3
    GROUP 12,4
    GROUP 13,5
    GROUP 14,6
    GROUP 15,7
    ret
