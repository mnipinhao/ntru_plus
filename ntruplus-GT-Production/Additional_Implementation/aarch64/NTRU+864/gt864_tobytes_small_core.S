/* Exact scheduled instructions; comments omitted. See TOBYTES-INTEGRATION.md. */
#ifdef __APPLE__
#define byte_pair_small _byte_pair_small
#endif
.text
.global byte_pair_small
byte_pair_small:
        byte_pair_small_slothy_start:
        ldr q11, [x1, #384]
        ldr q9, [x1, #336]
        ldr q13, [x1]
        ext v2.16B, v9.16B, v9.16B, #14
        ldr q9, [x1, #288]
        trn1 v14.8H, v11.8H, v2.8H
        trn2 v11.8H, v11.8H, v2.8H
        ext v21.16B, v9.16B, v9.16B, #12
        ldr q9, [x1, #240]
        ext v18.16B, v9.16B, v9.16B, #10
        ldr q9, [x1, #192]
        trn1 v2.8H, v21.8H, v18.8H
        trn2 v18.8H, v21.8H, v18.8H
        ext v6.16B, v9.16B, v9.16B, #8
        ldr q9, [x1, #144]
        ext v31.16B, v9.16B, v9.16B, #6
        ldr q9, [x1, #96]
        trn2 v21.8H, v6.8H, v31.8H
        trn1 v22.8H, v6.8H, v31.8H
        trn1 v6.4S, v14.4S, v2.4S
        trn2 v14.4S, v14.4S, v2.4S
        ext v24.16B, v9.16B, v9.16B, #4
        ldr q9, [x1, #48]
        ext v9.16B, v9.16B, v9.16B, #2
        trn1 v31.8H, v24.8H, v9.8H
        trn2 v9.8H, v24.8H, v9.8H
        trn1 v24.4S, v11.4S, v18.4S
        trn2 v11.4S, v11.4S, v18.4S
        trn1 v18.4S, v21.4S, v9.4S
        trn2 v9.4S, v21.4S, v9.4S
        trn1 v1.2D, v11.2D, v9.2D
        trn2 v10.2D, v11.2D, v9.2D
        ldr q9, [x2, #336]
        trn1 v2.4S, v22.4S, v31.4S
        ldr q11, [x2, #384]
        trn2 v25.2D, v24.2D, v18.2D
        trn2 v31.4S, v22.4S, v31.4S
        ldr q7, [x2]
        trn2 v3.2D, v6.2D, v2.2D
        trn1 v17.2D, v6.2D, v2.2D
        ext v2.16B, v9.16B, v9.16B, #14
        ldr q9, [x2, #192]
        trn1 v15.2D, v24.2D, v18.2D
        trn1 v23.2D, v14.2D, v31.2D
        trn2 v0.2D, v14.2D, v31.2D
        trn1 v14.8H, v11.8H, v2.8H
        mov w16, #3457
        ext v6.16B, v9.16B, v9.16B, #8
        ldr q9, [x2, #96]
        trn2 v11.8H, v11.8H, v2.8H
        ext v24.16B, v9.16B, v9.16B, #4
        ldr q9, [x2, #144]
        ext v31.16B, v9.16B, v9.16B, #6
        ldr q9, [x2, #288]
        trn1 v22.8H, v6.8H, v31.8H
        ext v21.16B, v9.16B, v9.16B, #12
        ldr q9, [x2, #240]
        ext v18.16B, v9.16B, v9.16B, #10
        ldr q9, [x2, #48]
        trn1 v2.8H, v21.8H, v18.8H
        trn2 v18.8H, v21.8H, v18.8H
        ext v9.16B, v9.16B, v9.16B, #2
        trn2 v21.8H, v6.8H, v31.8H
        trn1 v6.4S, v14.4S, v2.4S
        trn1 v31.8H, v24.8H, v9.8H
        trn2 v14.4S, v14.4S, v2.4S
        trn2 v9.8H, v24.8H, v9.8H
        trn1 v2.4S, v22.4S, v31.4S
        trn1 v24.4S, v11.4S, v18.4S
        trn2 v11.4S, v11.4S, v18.4S
        trn1 v18.4S, v21.4S, v9.4S
        trn2 v9.4S, v21.4S, v9.4S
        trn1 v12.2D, v6.2D, v2.2D
        trn1 v26.2D, v24.2D, v18.2D
        trn2 v27.2D, v6.2D, v2.2D
        trn2 v4.2D, v24.2D, v18.2D
        trn1 v6.2D, v11.2D, v9.2D
        ldr q18, [x4, #0]
        trn2 v24.2D, v11.2D, v9.2D
        orr v9.16B, v17.16B, v17.16B
        trn2 v31.4S, v22.4S, v31.4S
        ins v9.h[0], v13.h[0]
        trn2 v21.2D, v14.2D, v31.2D
        trn1 v22.2D, v14.2D, v31.2D
        dup v14.8H, w16
        tbl v31.16B, {v9.16B}, v18.16B
        sshr v9.8H, v31.8H, #15
        and v9.16B, v9.16B, v14.16B
        add v2.8H, v31.8H, v9.8H
        orr v9.16B, v12.16B, v12.16B
        ins v9.h[0], v7.h[0]
        add x16, x0, #0
        ldr q11, [x4, #16]
        tbl v31.16B, {v9.16B}, v18.16B
        xtn v18.8B, v2.8H
        sshr v9.8H, v31.8H, #15
        and v9.16B, v9.16B, v14.16B
        add v31.8H, v31.8H, v9.8H
        ushr v9.8H, v2.8H, #8
        sli v9.8H, v31.8H, #4
        xtn v19.8B, v9.8H
        ushr v9.8H, v31.8H, #4
        xtn v20.8B, v9.8H
        st3 {v18.8B, v19.8B, v20.8B}, [x16]
        ldr q18, [x3, #0]
        and v31.16B, v17.16B, v18.16B
        bic v9.16B, v15.16B, v18.16B
        orr v9.16B, v31.16B, v9.16B
        ins v9.h[1], v13.h[1]
        tbl v31.16B, {v9.16B}, v11.16B
        sshr v9.8H, v31.8H, #15
        and v9.16B, v9.16B, v14.16B
        add v2.8H, v31.8H, v9.8H
        bic v9.16B, v26.16B, v18.16B
        and v31.16B, v12.16B, v18.16B
        orr v9.16B, v31.16B, v9.16B
        ins v9.h[1], v7.h[1]
        tbl v31.16B, {v9.16B}, v11.16B
        ldr q11, [x4, #32]
        sshr v9.8H, v31.8H, #15
        and v9.16B, v9.16B, v14.16B
        xtn v18.8B, v2.8H
        add x14, x0, #72
        add x12, x0, #144
        add v31.8H, v31.8H, v9.8H
        ushr v9.8H, v2.8H, #8
        sli v9.8H, v31.8H, #4
        xtn v19.8B, v9.8H
        ushr v9.8H, v31.8H, #4
        xtn v20.8B, v9.8H
        st3 {v18.8B, v19.8B, v20.8B}, [x14]
        ldr q18, [x3, #16]
        and v31.16B, v15.16B, v18.16B
        bic v9.16B, v23.16B, v18.16B
        orr v9.16B, v31.16B, v9.16B
        ins v9.h[2], v13.h[2]
        tbl v31.16B, {v9.16B}, v11.16B
        sshr v9.8H, v31.8H, #15
        and v9.16B, v9.16B, v14.16B
        add v2.8H, v31.8H, v9.8H
        bic v9.16B, v22.16B, v18.16B
        and v31.16B, v26.16B, v18.16B
        orr v9.16B, v31.16B, v9.16B
        ins v9.h[2], v7.h[2]
        xtn v18.8B, v2.8H
        tbl v31.16B, {v9.16B}, v11.16B
        ldr q11, [x4, #48]
        sshr v9.8H, v31.8H, #15
        and v9.16B, v9.16B, v14.16B
        add v31.8H, v31.8H, v9.8H
        ushr v9.8H, v2.8H, #8
        sli v9.8H, v31.8H, #4
        xtn v19.8B, v9.8H
        ushr v9.8H, v31.8H, #4
        xtn v20.8B, v9.8H
        st3 {v18.8B, v19.8B, v20.8B}, [x12]
        ldr q18, [x3, #32]
        and v31.16B, v23.16B, v18.16B
        bic v9.16B, v1.16B, v18.16B
        orr v9.16B, v31.16B, v9.16B
        ins v9.h[3], v13.h[3]
        tbl v31.16B, {v9.16B}, v11.16B
        sshr v9.8H, v31.8H, #15
        and v9.16B, v9.16B, v14.16B
        add x17, x0, #24
        add v2.8H, v31.8H, v9.8H
        bic v9.16B, v6.16B, v18.16B
        and v31.16B, v22.16B, v18.16B
        xtn v18.8B, v2.8H
        orr v9.16B, v31.16B, v9.16B
        ins v9.h[3], v7.h[3]
        tbl v31.16B, {v9.16B}, v11.16B
        ldr q11, [x4, #64]
        sshr v9.8H, v31.8H, #15
        and v9.16B, v9.16B, v14.16B
        add v31.8H, v31.8H, v9.8H
        ushr v9.8H, v2.8H, #8
        sli v9.8H, v31.8H, #4
        xtn v19.8B, v9.8H
        ushr v9.8H, v31.8H, #4
        xtn v20.8B, v9.8H
        add x7, x0, #96
        st3 {v18.8B, v19.8B, v20.8B}, [x17]
        ldr q18, [x3, #48]
        and v31.16B, v1.16B, v18.16B
        bic v9.16B, v3.16B, v18.16B
        orr v9.16B, v31.16B, v9.16B
        ins v9.h[4], v13.h[4]
        tbl v31.16B, {v9.16B}, v11.16B
        sshr v9.8H, v31.8H, #15
        and v9.16B, v9.16B, v14.16B
        add v2.8H, v31.8H, v9.8H
        and v31.16B, v6.16B, v18.16B
        bic v9.16B, v27.16B, v18.16B
        orr v9.16B, v31.16B, v9.16B
        xtn v18.8B, v2.8H
        add x15, x0, #168
        ins v9.h[4], v7.h[4]
        tbl v31.16B, {v9.16B}, v11.16B
        ldr q11, [x4, #80]
        sshr v9.8H, v31.8H, #15
        and v9.16B, v9.16B, v14.16B
        add v31.8H, v31.8H, v9.8H
        ushr v9.8H, v2.8H, #8
        sli v9.8H, v31.8H, #4
        xtn v19.8B, v9.8H
        ushr v9.8H, v31.8H, #4
        xtn v20.8B, v9.8H
        st3 {v18.8B, v19.8B, v20.8B}, [x7]
        ldr q18, [x3, #64]
        bic v9.16B, v25.16B, v18.16B
        and v31.16B, v3.16B, v18.16B
        orr v9.16B, v31.16B, v9.16B
        ins v9.h[5], v13.h[5]
        tbl v31.16B, {v9.16B}, v11.16B
        sshr v9.8H, v31.8H, #15
        and v9.16B, v9.16B, v14.16B
        add v2.8H, v31.8H, v9.8H
        and v31.16B, v27.16B, v18.16B
        bic v9.16B, v4.16B, v18.16B
        orr v9.16B, v31.16B, v9.16B
        ins v9.h[5], v7.h[5]
        tbl v31.16B, {v9.16B}, v11.16B
        sshr v9.8H, v31.8H, #15
        and v9.16B, v9.16B, v14.16B
        ldr q11, [x4, #96]
        add x6, x0, #48
        xtn v18.8B, v2.8H
        add v31.8H, v31.8H, v9.8H
        ushr v9.8H, v2.8H, #8
        sli v9.8H, v31.8H, #4
        xtn v19.8B, v9.8H
        ushr v9.8H, v31.8H, #4
        xtn v20.8B, v9.8H
        st3 {v18.8B, v19.8B, v20.8B}, [x15]
        ldr q18, [x3, #80]
        bic v9.16B, v0.16B, v18.16B
        and v31.16B, v25.16B, v18.16B
        orr v9.16B, v31.16B, v9.16B
        ins v9.h[6], v13.h[6]
        tbl v31.16B, {v9.16B}, v11.16B
        sshr v9.8H, v31.8H, #15
        and v9.16B, v9.16B, v14.16B
        add v2.8H, v31.8H, v9.8H
        bic v9.16B, v21.16B, v18.16B
        and v31.16B, v4.16B, v18.16B
        xtn v18.8B, v2.8H
        orr v9.16B, v31.16B, v9.16B
        ins v9.h[6], v7.h[6]
        tbl v31.16B, {v9.16B}, v11.16B
        sshr v9.8H, v31.8H, #15
        and v9.16B, v9.16B, v14.16B
        add v31.8H, v31.8H, v9.8H
        ushr v9.8H, v2.8H, #8
        sli v9.8H, v31.8H, #4
        add x9, x0, #120
        xtn v19.8B, v9.8H
        ushr v9.8H, v31.8H, #4
        xtn v20.8B, v9.8H
        orr v9.16B, v0.16B, v0.16B
        st3 {v18.8B, v19.8B, v20.8B}, [x6]
        ldr q18, [x4, #112]
        ins v9.h[7], v13.h[7]
        tbl v31.16B, {v9.16B}, v18.16B
        sshr v9.8H, v31.8H, #15
        and v9.16B, v9.16B, v14.16B
        add v2.8H, v31.8H, v9.8H
        orr v9.16B, v21.16B, v21.16B
        ins v9.h[7], v7.h[7]
        tbl v31.16B, {v9.16B}, v18.16B
        xtn v18.8B, v2.8H
        add x13, x0, #192
        sshr v9.8H, v31.8H, #15
        and v9.16B, v9.16B, v14.16B
        add v31.8H, v31.8H, v9.8H
        ushr v9.8H, v2.8H, #8
        sli v9.8H, v31.8H, #4
        xtn v19.8B, v9.8H
        ushr v9.8H, v31.8H, #4
        xtn v20.8B, v9.8H
        orr v9.16B, v10.16B, v10.16B
        st3 {v18.8B, v19.8B, v20.8B}, [x9]
        ldr q18, [x4, #128]
        tbl v31.16B, {v9.16B}, v18.16B
        sshr v9.8H, v31.8H, #15
        and v9.16B, v9.16B, v14.16B
        add v2.8H, v31.8H, v9.8H
        orr v9.16B, v24.16B, v24.16B
        tbl v31.16B, {v9.16B}, v18.16B
        xtn v18.8B, v2.8H
        sshr v9.8H, v31.8H, #15
        and v9.16B, v9.16B, v14.16B
        add v31.8H, v31.8H, v9.8H
        ushr v9.8H, v2.8H, #8
        sli v9.8H, v31.8H, #4
        xtn v19.8B, v9.8H
        ushr v9.8H, v31.8H, #4
        xtn v20.8B, v9.8H
        st3 {v18.8B, v19.8B, v20.8B}, [x13]
        byte_pair_small_slothy_end:
    ret
