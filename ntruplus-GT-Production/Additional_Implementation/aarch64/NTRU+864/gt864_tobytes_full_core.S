/* Exact scheduled instructions; comments omitted. See TOBYTES-INTEGRATION.md. */
#ifdef __APPLE__
#define byte_pair_block _byte_pair_block
#endif
.text
.global byte_pair_block
byte_pair_block:
        byte_pair_block_slothy_start:
        ldr q6, [x1, #384]
        ldr q2, [x1, #336]
        ldr q29, [x1]
        ext v20.16B, v2.16B, v2.16B, #14
        ldr q2, [x1, #288]
        trn1 v9.8H, v6.8H, v20.8H
        trn2 v6.8H, v6.8H, v20.8H
        ext v26.16B, v2.16B, v2.16B, #12
        ldr q2, [x1, #240]
        ext v25.16B, v2.16B, v2.16B, #10
        ldr q2, [x1, #192]
        trn1 v20.8H, v26.8H, v25.8H
        trn2 v25.8H, v26.8H, v25.8H
        ext v28.16B, v2.16B, v2.16B, #8
        ldr q2, [x1, #144]
        ext v18.16B, v2.16B, v2.16B, #6
        ldr q2, [x1, #96]
        ext v19.16B, v2.16B, v2.16B, #4
        trn2 v26.8H, v28.8H, v18.8H
        ldr q2, [x1, #48]
        ldr q31, [x2]
        trn1 v21.8H, v28.8H, v18.8H
        trn1 v28.4S, v9.4S, v20.4S
        trn2 v9.4S, v9.4S, v20.4S
        ext v2.16B, v2.16B, v2.16B, #2
        trn1 v18.8H, v19.8H, v2.8H
        trn2 v2.8H, v19.8H, v2.8H
        trn1 v19.4S, v6.4S, v25.4S
        trn2 v6.4S, v6.4S, v25.4S
        trn1 v25.4S, v26.4S, v2.4S
        trn2 v2.4S, v26.4S, v2.4S
        trn1 v22.2D, v6.2D, v2.2D
        trn2 v0.2D, v6.2D, v2.2D
        ldr q2, [x2, #144]
        trn1 v20.4S, v21.4S, v18.4S
        trn2 v18.4S, v21.4S, v18.4S
        ldr q6, [x2, #384]
        trn2 v4.2D, v19.2D, v25.2D
        trn1 v17.2D, v19.2D, v25.2D
        trn1 v27.2D, v9.2D, v18.2D
        trn2 v15.2D, v9.2D, v18.2D
        ext v18.16B, v2.16B, v2.16B, #6
        ldr q2, [x2, #96]
        trn1 v24.2D, v28.2D, v20.2D
        trn2 v13.2D, v28.2D, v20.2D
        ext v19.16B, v2.16B, v2.16B, #4
        ldr q2, [x2, #240]
        ext v25.16B, v2.16B, v2.16B, #10
        ldr q2, [x2, #192]
        ext v28.16B, v2.16B, v2.16B, #8
        ldr q2, [x2, #288]
        ext v26.16B, v2.16B, v2.16B, #12
        mov w11, #3457
        ldr q2, [x2, #336]
        trn1 v21.8H, v28.8H, v18.8H
        mov w8, #9
        ext v20.16B, v2.16B, v2.16B, #14
        ldr q2, [x2, #48]
        trn1 v9.8H, v6.8H, v20.8H
        trn2 v6.8H, v6.8H, v20.8H
        trn1 v20.8H, v26.8H, v25.8H
        trn2 v25.8H, v26.8H, v25.8H
        trn2 v26.8H, v28.8H, v18.8H
        ext v2.16B, v2.16B, v2.16B, #2
        trn1 v28.4S, v9.4S, v20.4S
        trn2 v9.4S, v9.4S, v20.4S
        trn1 v18.8H, v19.8H, v2.8H
        trn2 v2.8H, v19.8H, v2.8H
        add x16, x0, #0
        trn1 v19.4S, v6.4S, v25.4S
        trn2 v6.4S, v6.4S, v25.4S
        trn1 v20.4S, v21.4S, v18.4S
        trn1 v25.4S, v26.4S, v2.4S
        trn2 v2.4S, v26.4S, v2.4S
        trn2 v18.4S, v21.4S, v18.4S
        trn2 v3.2D, v19.2D, v25.2D
        trn1 v21.2D, v6.2D, v2.2D
        trn1 v16.2D, v19.2D, v25.2D
        ldr q25, [x4, #0]
        trn2 v26.2D, v6.2D, v2.2D
        orr v2.16B, v24.16B, v24.16B
        trn1 v12.2D, v28.2D, v20.2D
        trn2 v14.2D, v9.2D, v18.2D
        ldr q6, [x4, #16]
        ins v2.h[0], v29.h[0]
        trn1 v10.2D, v9.2D, v18.2D
        dup v9.8H, w8
        trn2 v30.2D, v28.2D, v20.2D
        tbl v18.16B, {v2.16B}, v25.16B
        sqrdmulh v2.8H, v18.8H, v9.8H
        dup v28.8H, w11
        mls v18.8H, v2.8H, v28.8H
        sshr v2.8H, v18.8H, #15
        and v2.16B, v2.16B, v28.16B
        add v20.8H, v18.8H, v2.8H
        orr v2.16B, v12.16B, v12.16B
        ins v2.h[0], v31.h[0]
        tbl v18.16B, {v2.16B}, v25.16B
        sqrdmulh v2.8H, v18.8H, v9.8H
        mls v18.8H, v2.8H, v28.8H
        sshr v2.8H, v18.8H, #15
        and v2.16B, v2.16B, v28.16B
        add v25.8H, v18.8H, v2.8H
        ushr v2.8H, v20.8H, #8
        xtn v18.8B, v20.8H
        sli v2.8H, v25.8H, #4
        xtn v19.8B, v2.8H
        ushr v2.8H, v25.8H, #4
        ldr q25, [x3, #0]
        xtn v20.8B, v2.8H
        st3 {v18.8B, v19.8B, v20.8B}, [x16]
        and v18.16B, v24.16B, v25.16B
        bic v2.16B, v17.16B, v25.16B
        orr v2.16B, v18.16B, v2.16B
        ins v2.h[1], v29.h[1]
        tbl v18.16B, {v2.16B}, v6.16B
        sqrdmulh v2.8H, v18.8H, v9.8H
        mls v18.8H, v2.8H, v28.8H
        add x17, x0, #72
        sshr v2.8H, v18.8H, #15
        and v2.16B, v2.16B, v28.16B
        add v20.8H, v18.8H, v2.8H
        bic v2.16B, v16.16B, v25.16B
        and v18.16B, v12.16B, v25.16B
        orr v2.16B, v18.16B, v2.16B
        ins v2.h[1], v31.h[1]
        tbl v18.16B, {v2.16B}, v6.16B
        sqrdmulh v2.8H, v18.8H, v9.8H
        mls v18.8H, v2.8H, v28.8H
        sshr v2.8H, v18.8H, #15
        and v2.16B, v2.16B, v28.16B
        add v25.8H, v18.8H, v2.8H
        ushr v2.8H, v20.8H, #8
        sli v2.8H, v25.8H, #4
        xtn v19.8B, v2.8H
        ushr v2.8H, v25.8H, #4
        ldr q25, [x3, #16]
        xtn v18.8B, v20.8H
        ldr q6, [x4, #32]
        add x10, x0, #144
        xtn v20.8B, v2.8H
        st3 {v18.8B, v19.8B, v20.8B}, [x17]
        bic v2.16B, v27.16B, v25.16B
        and v18.16B, v17.16B, v25.16B
        orr v2.16B, v18.16B, v2.16B
        ins v2.h[2], v29.h[2]
        tbl v18.16B, {v2.16B}, v6.16B
        sqrdmulh v2.8H, v18.8H, v9.8H
        mls v18.8H, v2.8H, v28.8H
        sshr v2.8H, v18.8H, #15
        and v2.16B, v2.16B, v28.16B
        add v20.8H, v18.8H, v2.8H
        and v18.16B, v16.16B, v25.16B
        bic v2.16B, v10.16B, v25.16B
        orr v2.16B, v18.16B, v2.16B
        ins v2.h[2], v31.h[2]
        tbl v18.16B, {v2.16B}, v6.16B
        ldr q6, [x4, #48]
        sqrdmulh v2.8H, v18.8H, v9.8H
        mls v18.8H, v2.8H, v28.8H
        sshr v2.8H, v18.8H, #15
        and v2.16B, v2.16B, v28.16B
        add v25.8H, v18.8H, v2.8H
        ushr v2.8H, v20.8H, #8
        xtn v18.8B, v20.8H
        sli v2.8H, v25.8H, #4
        xtn v19.8B, v2.8H
        ushr v2.8H, v25.8H, #4
        xtn v20.8B, v2.8H
        add x6, x0, #24
        ldr q25, [x3, #32]
        st3 {v18.8B, v19.8B, v20.8B}, [x10]
        bic v2.16B, v22.16B, v25.16B
        and v18.16B, v27.16B, v25.16B
        orr v2.16B, v18.16B, v2.16B
        ins v2.h[3], v29.h[3]
        tbl v18.16B, {v2.16B}, v6.16B
        sqrdmulh v2.8H, v18.8H, v9.8H
        mls v18.8H, v2.8H, v28.8H
        sshr v2.8H, v18.8H, #15
        and v2.16B, v2.16B, v28.16B
        add v20.8H, v18.8H, v2.8H
        and v18.16B, v10.16B, v25.16B
        bic v2.16B, v21.16B, v25.16B
        orr v2.16B, v18.16B, v2.16B
        ins v2.h[3], v31.h[3]
        tbl v18.16B, {v2.16B}, v6.16B
        ldr q6, [x4, #64]
        sqrdmulh v2.8H, v18.8H, v9.8H
        mls v18.8H, v2.8H, v28.8H
        sshr v2.8H, v18.8H, #15
        and v2.16B, v2.16B, v28.16B
        add v25.8H, v18.8H, v2.8H
        ushr v2.8H, v20.8H, #8
        xtn v18.8B, v20.8H
        sli v2.8H, v25.8H, #4
        xtn v19.8B, v2.8H
        ushr v2.8H, v25.8H, #4
        ldr q25, [x3, #48]
        xtn v20.8B, v2.8H
        st3 {v18.8B, v19.8B, v20.8B}, [x6]
        bic v2.16B, v13.16B, v25.16B
        and v18.16B, v22.16B, v25.16B
        add x14, x0, #96
        orr v2.16B, v18.16B, v2.16B
        ins v2.h[4], v29.h[4]
        tbl v18.16B, {v2.16B}, v6.16B
        sqrdmulh v2.8H, v18.8H, v9.8H
        mls v18.8H, v2.8H, v28.8H
        sshr v2.8H, v18.8H, #15
        and v2.16B, v2.16B, v28.16B
        add v20.8H, v18.8H, v2.8H
        and v18.16B, v21.16B, v25.16B
        bic v2.16B, v30.16B, v25.16B
        orr v2.16B, v18.16B, v2.16B
        ins v2.h[4], v31.h[4]
        tbl v18.16B, {v2.16B}, v6.16B
        ldr q6, [x4, #80]
        sqrdmulh v2.8H, v18.8H, v9.8H
        mls v18.8H, v2.8H, v28.8H
        add x13, x0, #168
        sshr v2.8H, v18.8H, #15
        and v2.16B, v2.16B, v28.16B
        add v25.8H, v18.8H, v2.8H
        ushr v2.8H, v20.8H, #8
        xtn v18.8B, v20.8H
        sli v2.8H, v25.8H, #4
        xtn v19.8B, v2.8H
        ushr v2.8H, v25.8H, #4
        ldr q25, [x3, #64]
        xtn v20.8B, v2.8H
        st3 {v18.8B, v19.8B, v20.8B}, [x14]
        bic v2.16B, v4.16B, v25.16B
        and v18.16B, v13.16B, v25.16B
        orr v2.16B, v18.16B, v2.16B
        ins v2.h[5], v29.h[5]
        tbl v18.16B, {v2.16B}, v6.16B
        sqrdmulh v2.8H, v18.8H, v9.8H
        mls v18.8H, v2.8H, v28.8H
        sshr v2.8H, v18.8H, #15
        and v2.16B, v2.16B, v28.16B
        add v20.8H, v18.8H, v2.8H
        and v18.16B, v30.16B, v25.16B
        bic v2.16B, v3.16B, v25.16B
        orr v2.16B, v18.16B, v2.16B
        ins v2.h[5], v31.h[5]
        tbl v18.16B, {v2.16B}, v6.16B
        ldr q6, [x4, #96]
        sqrdmulh v2.8H, v18.8H, v9.8H
        mls v18.8H, v2.8H, v28.8H
        sshr v2.8H, v18.8H, #15
        and v2.16B, v2.16B, v28.16B
        add v25.8H, v18.8H, v2.8H
        add x12, x0, #48
        ushr v2.8H, v20.8H, #8
        xtn v18.8B, v20.8H
        sli v2.8H, v25.8H, #4
        xtn v19.8B, v2.8H
        ushr v2.8H, v25.8H, #4
        ldr q25, [x3, #80]
        xtn v20.8B, v2.8H
        st3 {v18.8B, v19.8B, v20.8B}, [x13]
        and v18.16B, v4.16B, v25.16B
        bic v2.16B, v15.16B, v25.16B
        orr v2.16B, v18.16B, v2.16B
        ins v2.h[6], v29.h[6]
        tbl v18.16B, {v2.16B}, v6.16B
        sqrdmulh v2.8H, v18.8H, v9.8H
        mls v18.8H, v2.8H, v28.8H
        sshr v2.8H, v18.8H, #15
        and v2.16B, v2.16B, v28.16B
        add v20.8H, v18.8H, v2.8H
        bic v2.16B, v14.16B, v25.16B
        and v18.16B, v3.16B, v25.16B
        orr v2.16B, v18.16B, v2.16B
        ins v2.h[6], v31.h[6]
        tbl v18.16B, {v2.16B}, v6.16B
        sqrdmulh v2.8H, v18.8H, v9.8H
        mls v18.8H, v2.8H, v28.8H
        sshr v2.8H, v18.8H, #15
        and v2.16B, v2.16B, v28.16B
        add v25.8H, v18.8H, v2.8H
        ushr v2.8H, v20.8H, #8
        sli v2.8H, v25.8H, #4
        xtn v19.8B, v2.8H
        ushr v2.8H, v25.8H, #4
        xtn v18.8B, v20.8H
        ldr q25, [x4, #112]
        add x15, x0, #120
        xtn v20.8B, v2.8H
        orr v2.16B, v15.16B, v15.16B
        st3 {v18.8B, v19.8B, v20.8B}, [x12]
        ins v2.h[7], v29.h[7]
        tbl v18.16B, {v2.16B}, v25.16B
        sqrdmulh v2.8H, v18.8H, v9.8H
        mls v18.8H, v2.8H, v28.8H
        sshr v2.8H, v18.8H, #15
        and v2.16B, v2.16B, v28.16B
        add v20.8H, v18.8H, v2.8H
        orr v2.16B, v14.16B, v14.16B
        ins v2.h[7], v31.h[7]
        tbl v18.16B, {v2.16B}, v25.16B
        sqrdmulh v2.8H, v18.8H, v9.8H
        mls v18.8H, v2.8H, v28.8H
        add x7, x0, #192
        sshr v2.8H, v18.8H, #15
        and v2.16B, v2.16B, v28.16B
        add v25.8H, v18.8H, v2.8H
        ushr v2.8H, v20.8H, #8
        xtn v18.8B, v20.8H
        sli v2.8H, v25.8H, #4
        xtn v19.8B, v2.8H
        ushr v2.8H, v25.8H, #4
        ldr q25, [x4, #128]
        xtn v20.8B, v2.8H
        orr v2.16B, v0.16B, v0.16B
        st3 {v18.8B, v19.8B, v20.8B}, [x15]
        tbl v18.16B, {v2.16B}, v25.16B
        sqrdmulh v2.8H, v18.8H, v9.8H
        mls v18.8H, v2.8H, v28.8H
        sshr v2.8H, v18.8H, #15
        and v2.16B, v2.16B, v28.16B
        add v20.8H, v18.8H, v2.8H
        orr v2.16B, v26.16B, v26.16B
        tbl v18.16B, {v2.16B}, v25.16B
        sqrdmulh v2.8H, v18.8H, v9.8H
        mls v18.8H, v2.8H, v28.8H
        sshr v2.8H, v18.8H, #15
        and v2.16B, v2.16B, v28.16B
        add v25.8H, v18.8H, v2.8H
        ushr v2.8H, v20.8H, #8
        xtn v18.8B, v20.8H
        sli v2.8H, v25.8H, #4
        xtn v19.8B, v2.8H
        ushr v2.8H, v25.8H, #4
        xtn v20.8B, v2.8H
        st3 {v18.8B, v19.8B, v20.8B}, [x7]
        byte_pair_block_slothy_end:
    ret
