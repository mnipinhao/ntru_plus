#ifdef __APPLE__
#define p60_residual _p60_residual
#endif
.text
.p2align 4
.global p60_residual
p60_residual:
p60_residual_slothy_start:
        ldr q20, [x4, #1024]
        ldr q21, [x4, #1040]
        ldr q22, [x4, #1056]
        ldr q23, [x4, #1072]
        // (top 0, t 0) -> natural byte 0
        ldr q0, [x1, #0]
        ldr q4, [x1, #256]
        ldr q2, [x1, #1024]
        cmgt v16.8h, v0.8h, v20.8h
        cmgt v17.8h, v21.8h, v0.8h
        add v0.8h, v0.8h, v16.8h
        sub v0.8h, v0.8h, v17.8h
        sqrdmulh v16.8h, v0.8h, v22.8h
        mls v0.8h, v16.8h, v23.8h
        cmgt v16.8h, v4.8h, v20.8h
        cmgt v17.8h, v21.8h, v4.8h
        add v4.8h, v4.8h, v16.8h
        sub v4.8h, v4.8h, v17.8h
        sqrdmulh v16.8h, v4.8h, v22.8h
        mls v4.8h, v16.8h, v23.8h
        ext v1.16b, v0.16b, v0.16b, #8
        ext v5.16b, v4.16b, v4.16b, #8
        ext v6.16b, v2.16b, v2.16b, #8
        add x3, x0, #0
        st3 {v0.4h, v1.4h, v2.4h}, [x3]
        add x3, x0, #24
        st3 {v4.4h, v5.4h, v6.4h}, [x3]
        // (top 1, t 0) -> natural byte 864
        ldr q0, [x1, #512]
        ldr q4, [x1, #768]
        ldr q2, [x1, #1280]
        cmgt v16.8h, v0.8h, v20.8h
        cmgt v17.8h, v21.8h, v0.8h
        add v0.8h, v0.8h, v16.8h
        sub v0.8h, v0.8h, v17.8h
        sqrdmulh v16.8h, v0.8h, v22.8h
        mls v0.8h, v16.8h, v23.8h
        cmgt v16.8h, v4.8h, v20.8h
        cmgt v17.8h, v21.8h, v4.8h
        add v4.8h, v4.8h, v16.8h
        sub v4.8h, v4.8h, v17.8h
        sqrdmulh v16.8h, v4.8h, v22.8h
        mls v4.8h, v16.8h, v23.8h
        ext v1.16b, v0.16b, v0.16b, #8
        ext v5.16b, v4.16b, v4.16b, #8
        ext v6.16b, v2.16b, v2.16b, #8
        add x3, x0, #864
        st3 {v0.4h, v1.4h, v2.4h}, [x3]
        add x3, x0, #888
        st3 {v4.4h, v5.4h, v6.4h}, [x3]
        // (top 0, t 1) -> natural byte 54
        ldr q0, [x1, #16]
        ldr q4, [x1, #272]
        ldr q2, [x1, #1040]
        cmgt v16.8h, v0.8h, v20.8h
        cmgt v17.8h, v21.8h, v0.8h
        add v0.8h, v0.8h, v16.8h
        sub v0.8h, v0.8h, v17.8h
        sqrdmulh v16.8h, v0.8h, v22.8h
        mls v0.8h, v16.8h, v23.8h
        cmgt v16.8h, v4.8h, v20.8h
        cmgt v17.8h, v21.8h, v4.8h
        add v4.8h, v4.8h, v16.8h
        sub v4.8h, v4.8h, v17.8h
        sqrdmulh v16.8h, v4.8h, v22.8h
        mls v4.8h, v16.8h, v23.8h
        ext v1.16b, v0.16b, v0.16b, #8
        ext v5.16b, v4.16b, v4.16b, #8
        ext v6.16b, v2.16b, v2.16b, #8
        add x3, x0, #54
        st3 {v0.4h, v1.4h, v2.4h}, [x3]
        add x3, x0, #78
        st3 {v4.4h, v5.4h, v6.4h}, [x3]
        // (top 0, t 2) -> natural byte 108
        ldr q0, [x1, #32]
        ldr q4, [x1, #288]
        ldr q2, [x1, #1056]
        cmgt v16.8h, v0.8h, v20.8h
        cmgt v17.8h, v21.8h, v0.8h
        add v0.8h, v0.8h, v16.8h
        sub v0.8h, v0.8h, v17.8h
        sqrdmulh v16.8h, v0.8h, v22.8h
        mls v0.8h, v16.8h, v23.8h
        cmgt v16.8h, v4.8h, v20.8h
        cmgt v17.8h, v21.8h, v4.8h
        add v4.8h, v4.8h, v16.8h
        sub v4.8h, v4.8h, v17.8h
        sqrdmulh v16.8h, v4.8h, v22.8h
        mls v4.8h, v16.8h, v23.8h
        ext v1.16b, v0.16b, v0.16b, #8
        ext v5.16b, v4.16b, v4.16b, #8
        ext v6.16b, v2.16b, v2.16b, #8
        add x3, x0, #108
        st3 {v0.4h, v1.4h, v2.4h}, [x3]
        add x3, x0, #132
        st3 {v4.4h, v5.4h, v6.4h}, [x3]
        // (top 1, t 1) -> natural byte 918
        ldr q0, [x1, #528]
        ldr q4, [x1, #784]
        ldr q2, [x1, #1296]
        cmgt v16.8h, v0.8h, v20.8h
        cmgt v17.8h, v21.8h, v0.8h
        add v0.8h, v0.8h, v16.8h
        sub v0.8h, v0.8h, v17.8h
        sqrdmulh v16.8h, v0.8h, v22.8h
        mls v0.8h, v16.8h, v23.8h
        cmgt v16.8h, v4.8h, v20.8h
        cmgt v17.8h, v21.8h, v4.8h
        add v4.8h, v4.8h, v16.8h
        sub v4.8h, v4.8h, v17.8h
        sqrdmulh v16.8h, v4.8h, v22.8h
        mls v4.8h, v16.8h, v23.8h
        ext v1.16b, v0.16b, v0.16b, #8
        ext v5.16b, v4.16b, v4.16b, #8
        ext v6.16b, v2.16b, v2.16b, #8
        add x3, x0, #918
        st3 {v0.4h, v1.4h, v2.4h}, [x3]
        add x3, x0, #942
        st3 {v4.4h, v5.4h, v6.4h}, [x3]
        // (top 1, t 2) -> natural byte 972
        ldr q0, [x1, #544]
        ldr q4, [x1, #800]
        ldr q2, [x1, #1312]
        cmgt v16.8h, v0.8h, v20.8h
        cmgt v17.8h, v21.8h, v0.8h
        add v0.8h, v0.8h, v16.8h
        sub v0.8h, v0.8h, v17.8h
        sqrdmulh v16.8h, v0.8h, v22.8h
        mls v0.8h, v16.8h, v23.8h
        cmgt v16.8h, v4.8h, v20.8h
        cmgt v17.8h, v21.8h, v4.8h
        add v4.8h, v4.8h, v16.8h
        sub v4.8h, v4.8h, v17.8h
        sqrdmulh v16.8h, v4.8h, v22.8h
        mls v4.8h, v16.8h, v23.8h
        ext v1.16b, v0.16b, v0.16b, #8
        ext v5.16b, v4.16b, v4.16b, #8
        ext v6.16b, v2.16b, v2.16b, #8
        add x3, x0, #972
        st3 {v0.4h, v1.4h, v2.4h}, [x3]
        add x3, x0, #996
        st3 {v4.4h, v5.4h, v6.4h}, [x3]
        // (top 0, t 3) -> natural byte 162
        ldr q0, [x1, #48]
        ldr q4, [x1, #304]
        ldr q2, [x1, #1072]
        cmgt v16.8h, v0.8h, v20.8h
        cmgt v17.8h, v21.8h, v0.8h
        add v0.8h, v0.8h, v16.8h
        sub v0.8h, v0.8h, v17.8h
        sqrdmulh v16.8h, v0.8h, v22.8h
        mls v0.8h, v16.8h, v23.8h
        cmgt v16.8h, v4.8h, v20.8h
        cmgt v17.8h, v21.8h, v4.8h
        add v4.8h, v4.8h, v16.8h
        sub v4.8h, v4.8h, v17.8h
        sqrdmulh v16.8h, v4.8h, v22.8h
        mls v4.8h, v16.8h, v23.8h
        ext v1.16b, v0.16b, v0.16b, #8
        ext v5.16b, v4.16b, v4.16b, #8
        ext v6.16b, v2.16b, v2.16b, #8
        add x3, x0, #162
        st3 {v0.4h, v1.4h, v2.4h}, [x3]
        add x3, x0, #186
        st3 {v4.4h, v5.4h, v6.4h}, [x3]
        // (top 1, t 3) -> natural byte 1026
        ldr q0, [x1, #560]
        ldr q4, [x1, #816]
        ldr q2, [x1, #1328]
        cmgt v16.8h, v0.8h, v20.8h
        cmgt v17.8h, v21.8h, v0.8h
        add v0.8h, v0.8h, v16.8h
        sub v0.8h, v0.8h, v17.8h
        sqrdmulh v16.8h, v0.8h, v22.8h
        mls v0.8h, v16.8h, v23.8h
        cmgt v16.8h, v4.8h, v20.8h
        cmgt v17.8h, v21.8h, v4.8h
        add v4.8h, v4.8h, v16.8h
        sub v4.8h, v4.8h, v17.8h
        sqrdmulh v16.8h, v4.8h, v22.8h
        mls v4.8h, v16.8h, v23.8h
        ext v1.16b, v0.16b, v0.16b, #8
        ext v5.16b, v4.16b, v4.16b, #8
        ext v6.16b, v2.16b, v2.16b, #8
        add x3, x0, #1026
        st3 {v0.4h, v1.4h, v2.4h}, [x3]
        add x3, x0, #1050
        st3 {v4.4h, v5.4h, v6.4h}, [x3]
        // (top 0, t 4) -> natural byte 216
        ldr q0, [x1, #64]
        ldr q4, [x1, #320]
        ldr q2, [x1, #1088]
        cmgt v16.8h, v0.8h, v20.8h
        cmgt v17.8h, v21.8h, v0.8h
        add v0.8h, v0.8h, v16.8h
        sub v0.8h, v0.8h, v17.8h
        sqrdmulh v16.8h, v0.8h, v22.8h
        mls v0.8h, v16.8h, v23.8h
        cmgt v16.8h, v4.8h, v20.8h
        cmgt v17.8h, v21.8h, v4.8h
        add v4.8h, v4.8h, v16.8h
        sub v4.8h, v4.8h, v17.8h
        sqrdmulh v16.8h, v4.8h, v22.8h
        mls v4.8h, v16.8h, v23.8h
        ext v1.16b, v0.16b, v0.16b, #8
        ext v5.16b, v4.16b, v4.16b, #8
        ext v6.16b, v2.16b, v2.16b, #8
        add x3, x0, #216
        st3 {v0.4h, v1.4h, v2.4h}, [x3]
        add x3, x0, #240
        st3 {v4.4h, v5.4h, v6.4h}, [x3]
        // (top 1, t 8) -> natural byte 1296
        ldr q0, [x1, #640]
        ldr q4, [x1, #896]
        ldr q2, [x1, #1408]
        cmgt v16.8h, v0.8h, v20.8h
        cmgt v17.8h, v21.8h, v0.8h
        add v0.8h, v0.8h, v16.8h
        sub v0.8h, v0.8h, v17.8h
        sqrdmulh v16.8h, v0.8h, v22.8h
        mls v0.8h, v16.8h, v23.8h
        cmgt v16.8h, v4.8h, v20.8h
        cmgt v17.8h, v21.8h, v4.8h
        add v4.8h, v4.8h, v16.8h
        sub v4.8h, v4.8h, v17.8h
        sqrdmulh v16.8h, v4.8h, v22.8h
        mls v4.8h, v16.8h, v23.8h
        ext v1.16b, v0.16b, v0.16b, #8
        ext v5.16b, v4.16b, v4.16b, #8
        ext v6.16b, v2.16b, v2.16b, #8
        add x3, x0, #1296
        st3 {v0.4h, v1.4h, v2.4h}, [x3]
        add x3, x0, #1320
        st3 {v4.4h, v5.4h, v6.4h}, [x3]
p60_residual_slothy_end:
        ret
#if defined(__ELF__)
.section .note.GNU-stack,"",%progbits
#endif
