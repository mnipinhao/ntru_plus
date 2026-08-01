// Production compact shared-core canonical pack.
.text

.p2align 4
.global poly_tobytes_gt_canonical
.global _poly_tobytes_gt_canonical
#ifndef __APPLE__
.type poly_tobytes_gt_canonical, %function
#endif
poly_tobytes_gt_canonical:
_poly_tobytes_gt_canonical:
    sub sp, sp, #80
    stp d8, d9, [sp, #0]
    stp d10, d11, [sp, #16]
    stp d12, d13, [sp, #32]
    stp d14, d15, [sp, #48]
    str x30, [sp, #64]
    adr x2, .Lcanonical_pack_compact_q
    ldr q0, [x2]
    // canonical blocks 0..15
    ldr d1, [x1, #312]
    ldr d9, [x1, #288]
    mov v1.d[1], v9.d[0]
    ldr d2, [x1, #360]
    ldr d9, [x1, #336]
    mov v2.d[1], v9.d[0]
    ldr d3, [x1, #264]
    ldr d9, [x1, #240]
    mov v3.d[1], v9.d[0]
    ldr d4, [x1, #192]
    ldr d9, [x1, #216]
    mov v4.d[1], v9.d[0]
    ldr d5, [x1, #72]
    ldr d9, [x1, #48]
    mov v5.d[1], v9.d[0]
    ldr d6, [x1, #0]
    ldr d9, [x1, #24]
    mov v6.d[1], v9.d[0]
    ldr d7, [x1, #168]
    ldr d9, [x1, #144]
    mov v7.d[1], v9.d[0]
    ldr d8, [x1, #96]
    ldr d9, [x1, #120]
    mov v8.d[1], v9.d[0]
    bl .Lcanonical_pack_compact_core
    // canonical blocks 16..31
    ldr d1, [x1, #696]
    ldr d9, [x1, #672]
    mov v1.d[1], v9.d[0]
    ldr d2, [x1, #744]
    ldr d9, [x1, #720]
    mov v2.d[1], v9.d[0]
    ldr d3, [x1, #648]
    ldr d9, [x1, #624]
    mov v3.d[1], v9.d[0]
    ldr d4, [x1, #576]
    ldr d9, [x1, #600]
    mov v4.d[1], v9.d[0]
    ldr d5, [x1, #456]
    ldr d9, [x1, #432]
    mov v5.d[1], v9.d[0]
    ldr d6, [x1, #384]
    ldr d9, [x1, #408]
    mov v6.d[1], v9.d[0]
    ldr d7, [x1, #552]
    ldr d9, [x1, #528]
    mov v7.d[1], v9.d[0]
    ldr d8, [x1, #480]
    ldr d9, [x1, #504]
    mov v8.d[1], v9.d[0]
    bl .Lcanonical_pack_compact_core
    // canonical blocks 32..47
    ldr d1, [x1, #128]
    ldr d9, [x1, #152]
    mov v1.d[1], v9.d[0]
    ldr d2, [x1, #176]
    ldr d9, [x1, #200]
    mov v2.d[1], v9.d[0]
    ldr d3, [x1, #224]
    ldr d9, [x1, #248]
    mov v3.d[1], v9.d[0]
    ldr d4, [x1, #272]
    ldr d9, [x1, #296]
    mov v4.d[1], v9.d[0]
    ldr d5, [x1, #320]
    ldr d9, [x1, #344]
    mov v5.d[1], v9.d[0]
    ldr d6, [x1, #368]
    ldr d9, [x1, #392]
    mov v6.d[1], v9.d[0]
    ldr d7, [x1, #416]
    ldr d9, [x1, #440]
    mov v7.d[1], v9.d[0]
    ldr d8, [x1, #464]
    ldr d9, [x1, #488]
    mov v8.d[1], v9.d[0]
    bl .Lcanonical_pack_compact_core
    // canonical blocks 48..63
    ldr d1, [x1, #704]
    ldr d9, [x1, #728]
    mov v1.d[1], v9.d[0]
    ldr d2, [x1, #752]
    ldr d9, [x1, #8]
    mov v2.d[1], v9.d[0]
    ldr d3, [x1, #32]
    ldr d9, [x1, #56]
    mov v3.d[1], v9.d[0]
    ldr d4, [x1, #80]
    ldr d9, [x1, #104]
    mov v4.d[1], v9.d[0]
    ldr d5, [x1, #608]
    ldr d9, [x1, #632]
    mov v5.d[1], v9.d[0]
    ldr d6, [x1, #656]
    ldr d9, [x1, #680]
    mov v6.d[1], v9.d[0]
    ldr d7, [x1, #560]
    ldr d9, [x1, #584]
    mov v7.d[1], v9.d[0]
    ldr d8, [x1, #536]
    ldr d9, [x1, #512]
    mov v8.d[1], v9.d[0]
    bl .Lcanonical_pack_compact_core
    // canonical blocks 64..79
    ldr d1, [x1, #400]
    ldr d9, [x1, #424]
    mov v1.d[1], v9.d[0]
    ldr d2, [x1, #376]
    ldr d9, [x1, #352]
    mov v2.d[1], v9.d[0]
    ldr d3, [x1, #280]
    ldr d9, [x1, #256]
    mov v3.d[1], v9.d[0]
    ldr d4, [x1, #328]
    ldr d9, [x1, #304]
    mov v4.d[1], v9.d[0]
    ldr d5, [x1, #592]
    ldr d9, [x1, #616]
    mov v5.d[1], v9.d[0]
    ldr d6, [x1, #568]
    ldr d9, [x1, #544]
    mov v6.d[1], v9.d[0]
    ldr d7, [x1, #472]
    ldr d9, [x1, #448]
    mov v7.d[1], v9.d[0]
    ldr d8, [x1, #520]
    ldr d9, [x1, #496]
    mov v8.d[1], v9.d[0]
    bl .Lcanonical_pack_compact_core
    // canonical blocks 80..95
    ldr d1, [x1, #16]
    ldr d9, [x1, #40]
    mov v1.d[1], v9.d[0]
    ldr d2, [x1, #760]
    ldr d9, [x1, #736]
    mov v2.d[1], v9.d[0]
    ldr d3, [x1, #664]
    ldr d9, [x1, #640]
    mov v3.d[1], v9.d[0]
    ldr d4, [x1, #712]
    ldr d9, [x1, #688]
    mov v4.d[1], v9.d[0]
    ldr d5, [x1, #208]
    ldr d9, [x1, #232]
    mov v5.d[1], v9.d[0]
    ldr d6, [x1, #184]
    ldr d9, [x1, #160]
    mov v6.d[1], v9.d[0]
    ldr d7, [x1, #88]
    ldr d9, [x1, #64]
    mov v7.d[1], v9.d[0]
    ldr d8, [x1, #136]
    ldr d9, [x1, #112]
    mov v8.d[1], v9.d[0]
    bl .Lcanonical_pack_compact_core
    // canonical blocks 96..111
    ldr d1, [x1, #1136]
    ldr d9, [x1, #1160]
    mov v1.d[1], v9.d[0]
    ldr d2, [x1, #1112]
    ldr d9, [x1, #1088]
    mov v2.d[1], v9.d[0]
    ldr d3, [x1, #1232]
    ldr d9, [x1, #1256]
    mov v3.d[1], v9.d[0]
    ldr d4, [x1, #1208]
    ldr d9, [x1, #1184]
    mov v4.d[1], v9.d[0]
    ldr d5, [x1, #1040]
    ldr d9, [x1, #1064]
    mov v5.d[1], v9.d[0]
    ldr d6, [x1, #1016]
    ldr d9, [x1, #992]
    mov v6.d[1], v9.d[0]
    ldr d7, [x1, #920]
    ldr d9, [x1, #896]
    mov v7.d[1], v9.d[0]
    ldr d8, [x1, #968]
    ldr d9, [x1, #944]
    mov v8.d[1], v9.d[0]
    bl .Lcanonical_pack_compact_core
    // canonical blocks 112..127
    ldr d1, [x1, #1424]
    ldr d9, [x1, #1448]
    mov v1.d[1], v9.d[0]
    ldr d2, [x1, #1400]
    ldr d9, [x1, #1376]
    mov v2.d[1], v9.d[0]
    ldr d3, [x1, #1304]
    ldr d9, [x1, #1280]
    mov v3.d[1], v9.d[0]
    ldr d4, [x1, #1352]
    ldr d9, [x1, #1328]
    mov v4.d[1], v9.d[0]
    ldr d5, [x1, #848]
    ldr d9, [x1, #872]
    mov v5.d[1], v9.d[0]
    ldr d6, [x1, #824]
    ldr d9, [x1, #800]
    mov v6.d[1], v9.d[0]
    ldr d7, [x1, #1496]
    ldr d9, [x1, #1472]
    mov v7.d[1], v9.d[0]
    ldr d8, [x1, #776]
    ldr d9, [x1, #1520]
    mov v8.d[1], v9.d[0]
    bl .Lcanonical_pack_compact_core
    // canonical blocks 128..143
    ldr d1, [x1, #1336]
    ldr d9, [x1, #1312]
    mov v1.d[1], v9.d[0]
    ldr d2, [x1, #1384]
    ldr d9, [x1, #1360]
    mov v2.d[1], v9.d[0]
    ldr d3, [x1, #1288]
    ldr d9, [x1, #1264]
    mov v3.d[1], v9.d[0]
    ldr d4, [x1, #1216]
    ldr d9, [x1, #1240]
    mov v4.d[1], v9.d[0]
    ldr d5, [x1, #1096]
    ldr d9, [x1, #1072]
    mov v5.d[1], v9.d[0]
    ldr d6, [x1, #1024]
    ldr d9, [x1, #1048]
    mov v6.d[1], v9.d[0]
    ldr d7, [x1, #1192]
    ldr d9, [x1, #1168]
    mov v7.d[1], v9.d[0]
    ldr d8, [x1, #1120]
    ldr d9, [x1, #1144]
    mov v8.d[1], v9.d[0]
    bl .Lcanonical_pack_compact_core
    // canonical blocks 144..159
    ldr d1, [x1, #952]
    ldr d9, [x1, #928]
    mov v1.d[1], v9.d[0]
    ldr d2, [x1, #1000]
    ldr d9, [x1, #976]
    mov v2.d[1], v9.d[0]
    ldr d3, [x1, #904]
    ldr d9, [x1, #880]
    mov v3.d[1], v9.d[0]
    ldr d4, [x1, #832]
    ldr d9, [x1, #856]
    mov v4.d[1], v9.d[0]
    ldr d5, [x1, #1480]
    ldr d9, [x1, #1456]
    mov v5.d[1], v9.d[0]
    ldr d6, [x1, #1408]
    ldr d9, [x1, #1432]
    mov v6.d[1], v9.d[0]
    ldr d7, [x1, #808]
    ldr d9, [x1, #784]
    mov v7.d[1], v9.d[0]
    ldr d8, [x1, #1504]
    ldr d9, [x1, #1528]
    mov v8.d[1], v9.d[0]
    bl .Lcanonical_pack_compact_core
    // canonical blocks 160..175
    ldr d1, [x1, #1152]
    ldr d9, [x1, #1176]
    mov v1.d[1], v9.d[0]
    ldr d2, [x1, #1200]
    ldr d9, [x1, #1224]
    mov v2.d[1], v9.d[0]
    ldr d3, [x1, #1248]
    ldr d9, [x1, #1272]
    mov v3.d[1], v9.d[0]
    ldr d4, [x1, #1296]
    ldr d9, [x1, #1320]
    mov v4.d[1], v9.d[0]
    ldr d5, [x1, #1344]
    ldr d9, [x1, #1368]
    mov v5.d[1], v9.d[0]
    ldr d6, [x1, #1392]
    ldr d9, [x1, #1416]
    mov v6.d[1], v9.d[0]
    ldr d7, [x1, #1440]
    ldr d9, [x1, #1464]
    mov v7.d[1], v9.d[0]
    ldr d8, [x1, #1488]
    ldr d9, [x1, #1512]
    mov v8.d[1], v9.d[0]
    bl .Lcanonical_pack_compact_core
    // canonical blocks 176..191
    ldr d1, [x1, #960]
    ldr d9, [x1, #984]
    mov v1.d[1], v9.d[0]
    ldr d2, [x1, #1008]
    ldr d9, [x1, #1032]
    mov v2.d[1], v9.d[0]
    ldr d3, [x1, #1056]
    ldr d9, [x1, #1080]
    mov v3.d[1], v9.d[0]
    ldr d4, [x1, #1104]
    ldr d9, [x1, #1128]
    mov v4.d[1], v9.d[0]
    ldr d5, [x1, #864]
    ldr d9, [x1, #888]
    mov v5.d[1], v9.d[0]
    ldr d6, [x1, #912]
    ldr d9, [x1, #936]
    mov v6.d[1], v9.d[0]
    ldr d7, [x1, #816]
    ldr d9, [x1, #840]
    mov v7.d[1], v9.d[0]
    ldr d8, [x1, #792]
    ldr d9, [x1, #768]
    mov v8.d[1], v9.d[0]
    bl .Lcanonical_pack_compact_core
    ldr x30, [sp, #64]
    ldp d8, d9, [sp, #0]
    ldp d10, d11, [sp, #16]
    ldp d12, d13, [sp, #32]
    ldp d14, d15, [sp, #48]
    add sp, sp, #80
    ret

.p2align 4
.Lcanonical_pack_compact_core:
    sshr v31.8H, v6.8H, #15
    sshr v19.8H, v5.8H, #15
    and v23.16B, v31.16B, v0.16B
    sshr v31.8H, v7.8H, #15
    sshr v26.8H, v8.8H, #15
    and v25.16B, v19.16B, v0.16B
    add v14.8H, v6.8H, v23.8H
    and v27.16B, v31.16B, v0.16B
    add v23.8H, v5.8H, v25.8H
    sshr v13.8H, v1.8H, #15
    and v25.16B, v26.16B, v0.16B
    add v18.8H, v7.8H, v27.8H
    sshr v27.8H, v2.8H, #15
    trn1 v29.8H, v23.8H, v14.8H
    add v15.8H, v8.8H, v25.8H
    sshr v9.8H, v3.8H, #15
    and v12.16B, v27.16B, v0.16B
    and v22.16B, v13.16B, v0.16B
    and v31.16B, v9.16B, v0.16B
    sshr v24.8H, v4.8H, #15
    trn2 v25.8H, v18.8H, v15.8H
    trn1 v11.8H, v18.8H, v15.8H
    and v9.16B, v24.16B, v0.16B
    add v21.8H, v1.8H, v22.8H
    add v10.8H, v2.8H, v12.8H
    trn2 v22.8H, v23.8H, v14.8H
    add v27.8H, v4.8H, v9.8H
    add v30.8H, v3.8H, v31.8H
    trn1 v26.8H, v21.8H, v10.8H
    trn2 v20.8H, v21.8H, v10.8H
    trn2 v14.8H, v30.8H, v27.8H
    trn1 v15.8H, v30.8H, v27.8H
    trn2 v10.4S, v29.4S, v11.4S
    trn1 v31.4S, v22.4S, v25.4S
    trn1 v12.4S, v20.4S, v14.4S
    trn2 v16.4S, v26.4S, v15.4S
    trn1 v26.4S, v26.4S, v15.4S
    trn2 v23.4S, v22.4S, v25.4S
    trn2 v28.2D, v16.2D, v10.2D
    trn1 v18.2D, v12.2D, v31.2D
    trn1 v21.2D, v16.2D, v10.2D
    trn2 v19.4S, v20.4S, v14.4S
    trn1 v11.4S, v29.4S, v11.4S
    shl v13.8H, v18.8H, #12
    trn1 v14.2D, v19.2D, v23.2D
    shl v27.8H, v21.8H, #8
    trn1 v9.2D, v26.2D, v11.2D
    ushr v10.8H, v18.8H, #4
    trn2 v31.2D, v12.2D, v31.2D
    ushr v17.8H, v21.8H, #8
    eor v13.16B, v9.16B, v13.16B
    ushr v20.8H, v28.8H, #8
    trn2 v24.2D, v26.2D, v11.2D
    shl v30.8H, v31.8H, #12
    ushr v25.8H, v31.8H, #4
    trn2 v31.2D, v19.2D, v23.2D
    shl v15.8H, v28.8H, #8
    eor v11.16B, v24.16B, v30.16B
    eor v16.16B, v10.16B, v27.16B
    shl v18.8H, v31.8H, #4
    eor v29.16B, v25.16B, v15.16B
    shl v23.8H, v14.8H, #4
    eor v21.16B, v20.16B, v18.16B
    trn1 v19.8H, v13.8H, v16.8H
    eor v20.16B, v17.16B, v23.16B
    trn2 v31.8H, v13.8H, v16.8H
    trn2 v23.8H, v29.8H, v21.8H
    trn1 v27.8H, v29.8H, v21.8H
    trn1 v13.8H, v20.8H, v11.8H
    trn2 v21.8H, v20.8H, v11.8H
    trn2 v14.4S, v27.4S, v31.4S
    trn1 v12.4S, v27.4S, v31.4S
    trn2 v30.4S, v19.4S, v13.4S
    trn1 v15.4S, v21.4S, v23.4S
    trn2 v11.4S, v21.4S, v23.4S
    trn1 v9.4S, v19.4S, v13.4S
    trn1 v25.2D, v15.2D, v30.2D
    trn1 v24.2D, v9.2D, v12.2D
    trn1 v26.2D, v14.2D, v11.2D
    trn2 v21.2D, v14.2D, v11.2D
    st1 {v24.8H, v25.8H, v26.8H}, [x0], #48
    trn2 v20.2D, v15.2D, v30.2D
    trn2 v19.2D, v9.2D, v12.2D
    st1 {v19.8H, v20.8H, v21.8H}, [x0], #48
    ret

.p2align 4
.Lcanonical_pack_compact_q:
    .hword 3457, 3457, 3457, 3457
    .hword 3457, 3457, 3457, 3457
#ifndef __APPLE__
.size poly_tobytes_gt_canonical, .-poly_tobytes_gt_canonical
#endif

#ifndef GT_PRODUCTION_USE_CANONICAL_UNPACK_U1
.global poly_frombytes_gt_canonical
.global _poly_frombytes_gt_canonical
.p2align 2
poly_frombytes_gt_canonical:
_poly_frombytes_gt_canonical:
    sub sp, sp, #64
    stp d8, d9, [sp, #0]
    stp d10, d11, [sp, #16]
    stp d12, d13, [sp, #32]
    stp d14, d15, [sp, #48]
    adr x2, canonical_pack_const_mask_0fff
    ldr q0, [x2]
    // canonical blocks 0..15
    ld1 {v18.8H, v19.8H, v20.8H}, [x1], #48
    ld1 {v26.8H, v27.8H, v28.8H}, [x1], #48
    trn1 v31.2D, v18.2D, v26.2D
    trn2 v14.2D, v18.2D, v26.2D
    trn2 v2.2D, v19.2D, v27.2D
    trn1 v17.2D, v20.2D, v28.2D
    trn1 v27.2D, v19.2D, v27.2D
    trn2 v30.2D, v20.2D, v28.2D
    trn2 v15.4S, v14.4S, v17.4S
    trn1 v29.4S, v31.4S, v2.4S
    trn2 v23.4S, v31.4S, v2.4S
    trn1 v21.4S, v27.4S, v30.4S
    trn2 v13.8H, v29.8H, v15.8H
    trn1 v16.8H, v29.8H, v15.8H
    trn1 v18.4S, v14.4S, v17.4S
    trn1 v25.8H, v23.8H, v21.8H
    trn2 v2.4S, v27.4S, v30.4S
    ushr v5.8H, v13.8H, #8
    shl v20.8H, v25.8H, #8
    and v24.16B, v16.16B, v0.16B
    shl v19.8H, v13.8H, #4
    trn1 v4.8H, v18.8H, v2.8H
    ushr v10.8H, v16.8H, #12
    eor v29.16B, v5.16B, v20.16B
    trn2 v15.8H, v18.8H, v2.8H
    ushr v5.8H, v25.8H, #4
    eor v19.16B, v10.16B, v19.16B
    and v26.16B, v29.16B, v0.16B
    and v27.16B, v5.16B, v0.16B
    shl v22.8H, v4.8H, #4
    and v25.16B, v19.16B, v0.16B
    shl v5.8H, v15.8H, #8
    trn2 v29.8H, v23.8H, v21.8H
    ushr v13.8H, v15.8H, #4
    ushr v6.8H, v4.8H, #8
    ushr v28.8H, v29.8H, #12
    eor v6.16B, v6.16B, v5.16B
    eor v30.16B, v28.16B, v22.16B
    and v14.16B, v29.16B, v0.16B
    and v16.16B, v6.16B, v0.16B
    and v17.16B, v13.16B, v0.16B
    and v15.16B, v30.16B, v0.16B
    trn1 v1.8h, v24.8h, v25.8h
    trn2 v2.8h, v24.8h, v25.8h
    trn1 v3.8h, v26.8h, v27.8h
    trn2 v4.8h, v26.8h, v27.8h
    trn1 v5.8h, v14.8h, v15.8h
    trn2 v6.8h, v14.8h, v15.8h
    trn1 v7.8h, v16.8h, v17.8h
    trn2 v8.8h, v16.8h, v17.8h
    trn1 v24.4s, v1.4s, v3.4s
    trn2 v26.4s, v1.4s, v3.4s
    trn1 v25.4s, v2.4s, v4.4s
    trn2 v27.4s, v2.4s, v4.4s
    trn1 v14.4s, v5.4s, v7.4s
    trn2 v16.4s, v5.4s, v7.4s
    trn1 v15.4s, v6.4s, v8.4s
    trn2 v17.4s, v6.4s, v8.4s
    trn2 v1.2d, v24.2d, v14.2d
    trn1 v24.2d, v24.2d, v14.2d
    mov v14.16b, v1.16b
    trn2 v2.2d, v25.2d, v15.2d
    trn1 v25.2d, v25.2d, v15.2d
    mov v15.16b, v2.16b
    trn2 v3.2d, v26.2d, v16.2d
    trn1 v26.2d, v26.2d, v16.2d
    mov v16.16b, v3.16b
    trn2 v4.2d, v27.2d, v17.2d
    trn1 v27.2d, v27.2d, v17.2d
    mov v17.16b, v4.16b
    str d24, [x0, #312]
    umov x9, v24.d[1]
    str x9, [x0, #288]
    str d25, [x0, #360]
    umov x9, v25.d[1]
    str x9, [x0, #336]
    str d26, [x0, #264]
    umov x9, v26.d[1]
    str x9, [x0, #240]
    str d27, [x0, #192]
    umov x9, v27.d[1]
    str x9, [x0, #216]
    str d14, [x0, #72]
    umov x9, v14.d[1]
    str x9, [x0, #48]
    str d15, [x0, #0]
    umov x9, v15.d[1]
    str x9, [x0, #24]
    str d16, [x0, #168]
    umov x9, v16.d[1]
    str x9, [x0, #144]
    str d17, [x0, #96]
    umov x9, v17.d[1]
    str x9, [x0, #120]
    // canonical blocks 16..31
    ld1 {v18.8H, v19.8H, v20.8H}, [x1], #48
    ld1 {v26.8H, v27.8H, v28.8H}, [x1], #48
    trn1 v31.2D, v18.2D, v26.2D
    trn2 v14.2D, v18.2D, v26.2D
    trn2 v2.2D, v19.2D, v27.2D
    trn1 v17.2D, v20.2D, v28.2D
    trn1 v27.2D, v19.2D, v27.2D
    trn2 v30.2D, v20.2D, v28.2D
    trn2 v15.4S, v14.4S, v17.4S
    trn1 v29.4S, v31.4S, v2.4S
    trn2 v23.4S, v31.4S, v2.4S
    trn1 v21.4S, v27.4S, v30.4S
    trn2 v13.8H, v29.8H, v15.8H
    trn1 v16.8H, v29.8H, v15.8H
    trn1 v18.4S, v14.4S, v17.4S
    trn1 v25.8H, v23.8H, v21.8H
    trn2 v2.4S, v27.4S, v30.4S
    ushr v5.8H, v13.8H, #8
    shl v20.8H, v25.8H, #8
    and v24.16B, v16.16B, v0.16B
    shl v19.8H, v13.8H, #4
    trn1 v4.8H, v18.8H, v2.8H
    ushr v10.8H, v16.8H, #12
    eor v29.16B, v5.16B, v20.16B
    trn2 v15.8H, v18.8H, v2.8H
    ushr v5.8H, v25.8H, #4
    eor v19.16B, v10.16B, v19.16B
    and v26.16B, v29.16B, v0.16B
    and v27.16B, v5.16B, v0.16B
    shl v22.8H, v4.8H, #4
    and v25.16B, v19.16B, v0.16B
    shl v5.8H, v15.8H, #8
    trn2 v29.8H, v23.8H, v21.8H
    ushr v13.8H, v15.8H, #4
    ushr v6.8H, v4.8H, #8
    ushr v28.8H, v29.8H, #12
    eor v6.16B, v6.16B, v5.16B
    eor v30.16B, v28.16B, v22.16B
    and v14.16B, v29.16B, v0.16B
    and v16.16B, v6.16B, v0.16B
    and v17.16B, v13.16B, v0.16B
    and v15.16B, v30.16B, v0.16B
    trn1 v1.8h, v24.8h, v25.8h
    trn2 v2.8h, v24.8h, v25.8h
    trn1 v3.8h, v26.8h, v27.8h
    trn2 v4.8h, v26.8h, v27.8h
    trn1 v5.8h, v14.8h, v15.8h
    trn2 v6.8h, v14.8h, v15.8h
    trn1 v7.8h, v16.8h, v17.8h
    trn2 v8.8h, v16.8h, v17.8h
    trn1 v24.4s, v1.4s, v3.4s
    trn2 v26.4s, v1.4s, v3.4s
    trn1 v25.4s, v2.4s, v4.4s
    trn2 v27.4s, v2.4s, v4.4s
    trn1 v14.4s, v5.4s, v7.4s
    trn2 v16.4s, v5.4s, v7.4s
    trn1 v15.4s, v6.4s, v8.4s
    trn2 v17.4s, v6.4s, v8.4s
    trn2 v1.2d, v24.2d, v14.2d
    trn1 v24.2d, v24.2d, v14.2d
    mov v14.16b, v1.16b
    trn2 v2.2d, v25.2d, v15.2d
    trn1 v25.2d, v25.2d, v15.2d
    mov v15.16b, v2.16b
    trn2 v3.2d, v26.2d, v16.2d
    trn1 v26.2d, v26.2d, v16.2d
    mov v16.16b, v3.16b
    trn2 v4.2d, v27.2d, v17.2d
    trn1 v27.2d, v27.2d, v17.2d
    mov v17.16b, v4.16b
    str d24, [x0, #696]
    umov x9, v24.d[1]
    str x9, [x0, #672]
    str d25, [x0, #744]
    umov x9, v25.d[1]
    str x9, [x0, #720]
    str d26, [x0, #648]
    umov x9, v26.d[1]
    str x9, [x0, #624]
    str d27, [x0, #576]
    umov x9, v27.d[1]
    str x9, [x0, #600]
    str d14, [x0, #456]
    umov x9, v14.d[1]
    str x9, [x0, #432]
    str d15, [x0, #384]
    umov x9, v15.d[1]
    str x9, [x0, #408]
    str d16, [x0, #552]
    umov x9, v16.d[1]
    str x9, [x0, #528]
    str d17, [x0, #480]
    umov x9, v17.d[1]
    str x9, [x0, #504]
    // canonical blocks 32..47
    ld1 {v18.8H, v19.8H, v20.8H}, [x1], #48
    ld1 {v26.8H, v27.8H, v28.8H}, [x1], #48
    trn1 v31.2D, v18.2D, v26.2D
    trn2 v14.2D, v18.2D, v26.2D
    trn2 v2.2D, v19.2D, v27.2D
    trn1 v17.2D, v20.2D, v28.2D
    trn1 v27.2D, v19.2D, v27.2D
    trn2 v30.2D, v20.2D, v28.2D
    trn2 v15.4S, v14.4S, v17.4S
    trn1 v29.4S, v31.4S, v2.4S
    trn2 v23.4S, v31.4S, v2.4S
    trn1 v21.4S, v27.4S, v30.4S
    trn2 v13.8H, v29.8H, v15.8H
    trn1 v16.8H, v29.8H, v15.8H
    trn1 v18.4S, v14.4S, v17.4S
    trn1 v25.8H, v23.8H, v21.8H
    trn2 v2.4S, v27.4S, v30.4S
    ushr v5.8H, v13.8H, #8
    shl v20.8H, v25.8H, #8
    and v24.16B, v16.16B, v0.16B
    shl v19.8H, v13.8H, #4
    trn1 v4.8H, v18.8H, v2.8H
    ushr v10.8H, v16.8H, #12
    eor v29.16B, v5.16B, v20.16B
    trn2 v15.8H, v18.8H, v2.8H
    ushr v5.8H, v25.8H, #4
    eor v19.16B, v10.16B, v19.16B
    and v26.16B, v29.16B, v0.16B
    and v27.16B, v5.16B, v0.16B
    shl v22.8H, v4.8H, #4
    and v25.16B, v19.16B, v0.16B
    shl v5.8H, v15.8H, #8
    trn2 v29.8H, v23.8H, v21.8H
    ushr v13.8H, v15.8H, #4
    ushr v6.8H, v4.8H, #8
    ushr v28.8H, v29.8H, #12
    eor v6.16B, v6.16B, v5.16B
    eor v30.16B, v28.16B, v22.16B
    and v14.16B, v29.16B, v0.16B
    and v16.16B, v6.16B, v0.16B
    and v17.16B, v13.16B, v0.16B
    and v15.16B, v30.16B, v0.16B
    trn1 v1.8h, v24.8h, v25.8h
    trn2 v2.8h, v24.8h, v25.8h
    trn1 v3.8h, v26.8h, v27.8h
    trn2 v4.8h, v26.8h, v27.8h
    trn1 v5.8h, v14.8h, v15.8h
    trn2 v6.8h, v14.8h, v15.8h
    trn1 v7.8h, v16.8h, v17.8h
    trn2 v8.8h, v16.8h, v17.8h
    trn1 v24.4s, v1.4s, v3.4s
    trn2 v26.4s, v1.4s, v3.4s
    trn1 v25.4s, v2.4s, v4.4s
    trn2 v27.4s, v2.4s, v4.4s
    trn1 v14.4s, v5.4s, v7.4s
    trn2 v16.4s, v5.4s, v7.4s
    trn1 v15.4s, v6.4s, v8.4s
    trn2 v17.4s, v6.4s, v8.4s
    trn2 v1.2d, v24.2d, v14.2d
    trn1 v24.2d, v24.2d, v14.2d
    mov v14.16b, v1.16b
    trn2 v2.2d, v25.2d, v15.2d
    trn1 v25.2d, v25.2d, v15.2d
    mov v15.16b, v2.16b
    trn2 v3.2d, v26.2d, v16.2d
    trn1 v26.2d, v26.2d, v16.2d
    mov v16.16b, v3.16b
    trn2 v4.2d, v27.2d, v17.2d
    trn1 v27.2d, v27.2d, v17.2d
    mov v17.16b, v4.16b
    str d24, [x0, #128]
    umov x9, v24.d[1]
    str x9, [x0, #152]
    str d25, [x0, #176]
    umov x9, v25.d[1]
    str x9, [x0, #200]
    str d26, [x0, #224]
    umov x9, v26.d[1]
    str x9, [x0, #248]
    str d27, [x0, #272]
    umov x9, v27.d[1]
    str x9, [x0, #296]
    str d14, [x0, #320]
    umov x9, v14.d[1]
    str x9, [x0, #344]
    str d15, [x0, #368]
    umov x9, v15.d[1]
    str x9, [x0, #392]
    str d16, [x0, #416]
    umov x9, v16.d[1]
    str x9, [x0, #440]
    str d17, [x0, #464]
    umov x9, v17.d[1]
    str x9, [x0, #488]
    // canonical blocks 48..63
    ld1 {v18.8H, v19.8H, v20.8H}, [x1], #48
    ld1 {v26.8H, v27.8H, v28.8H}, [x1], #48
    trn1 v31.2D, v18.2D, v26.2D
    trn2 v14.2D, v18.2D, v26.2D
    trn2 v2.2D, v19.2D, v27.2D
    trn1 v17.2D, v20.2D, v28.2D
    trn1 v27.2D, v19.2D, v27.2D
    trn2 v30.2D, v20.2D, v28.2D
    trn2 v15.4S, v14.4S, v17.4S
    trn1 v29.4S, v31.4S, v2.4S
    trn2 v23.4S, v31.4S, v2.4S
    trn1 v21.4S, v27.4S, v30.4S
    trn2 v13.8H, v29.8H, v15.8H
    trn1 v16.8H, v29.8H, v15.8H
    trn1 v18.4S, v14.4S, v17.4S
    trn1 v25.8H, v23.8H, v21.8H
    trn2 v2.4S, v27.4S, v30.4S
    ushr v5.8H, v13.8H, #8
    shl v20.8H, v25.8H, #8
    and v24.16B, v16.16B, v0.16B
    shl v19.8H, v13.8H, #4
    trn1 v4.8H, v18.8H, v2.8H
    ushr v10.8H, v16.8H, #12
    eor v29.16B, v5.16B, v20.16B
    trn2 v15.8H, v18.8H, v2.8H
    ushr v5.8H, v25.8H, #4
    eor v19.16B, v10.16B, v19.16B
    and v26.16B, v29.16B, v0.16B
    and v27.16B, v5.16B, v0.16B
    shl v22.8H, v4.8H, #4
    and v25.16B, v19.16B, v0.16B
    shl v5.8H, v15.8H, #8
    trn2 v29.8H, v23.8H, v21.8H
    ushr v13.8H, v15.8H, #4
    ushr v6.8H, v4.8H, #8
    ushr v28.8H, v29.8H, #12
    eor v6.16B, v6.16B, v5.16B
    eor v30.16B, v28.16B, v22.16B
    and v14.16B, v29.16B, v0.16B
    and v16.16B, v6.16B, v0.16B
    and v17.16B, v13.16B, v0.16B
    and v15.16B, v30.16B, v0.16B
    trn1 v1.8h, v24.8h, v25.8h
    trn2 v2.8h, v24.8h, v25.8h
    trn1 v3.8h, v26.8h, v27.8h
    trn2 v4.8h, v26.8h, v27.8h
    trn1 v5.8h, v14.8h, v15.8h
    trn2 v6.8h, v14.8h, v15.8h
    trn1 v7.8h, v16.8h, v17.8h
    trn2 v8.8h, v16.8h, v17.8h
    trn1 v24.4s, v1.4s, v3.4s
    trn2 v26.4s, v1.4s, v3.4s
    trn1 v25.4s, v2.4s, v4.4s
    trn2 v27.4s, v2.4s, v4.4s
    trn1 v14.4s, v5.4s, v7.4s
    trn2 v16.4s, v5.4s, v7.4s
    trn1 v15.4s, v6.4s, v8.4s
    trn2 v17.4s, v6.4s, v8.4s
    trn2 v1.2d, v24.2d, v14.2d
    trn1 v24.2d, v24.2d, v14.2d
    mov v14.16b, v1.16b
    trn2 v2.2d, v25.2d, v15.2d
    trn1 v25.2d, v25.2d, v15.2d
    mov v15.16b, v2.16b
    trn2 v3.2d, v26.2d, v16.2d
    trn1 v26.2d, v26.2d, v16.2d
    mov v16.16b, v3.16b
    trn2 v4.2d, v27.2d, v17.2d
    trn1 v27.2d, v27.2d, v17.2d
    mov v17.16b, v4.16b
    str d24, [x0, #704]
    umov x9, v24.d[1]
    str x9, [x0, #728]
    str d25, [x0, #752]
    umov x9, v25.d[1]
    str x9, [x0, #8]
    str d26, [x0, #32]
    umov x9, v26.d[1]
    str x9, [x0, #56]
    str d27, [x0, #80]
    umov x9, v27.d[1]
    str x9, [x0, #104]
    str d14, [x0, #608]
    umov x9, v14.d[1]
    str x9, [x0, #632]
    str d15, [x0, #656]
    umov x9, v15.d[1]
    str x9, [x0, #680]
    str d16, [x0, #560]
    umov x9, v16.d[1]
    str x9, [x0, #584]
    str d17, [x0, #536]
    umov x9, v17.d[1]
    str x9, [x0, #512]
    // canonical blocks 64..79
    ld1 {v18.8H, v19.8H, v20.8H}, [x1], #48
    ld1 {v26.8H, v27.8H, v28.8H}, [x1], #48
    trn1 v31.2D, v18.2D, v26.2D
    trn2 v14.2D, v18.2D, v26.2D
    trn2 v2.2D, v19.2D, v27.2D
    trn1 v17.2D, v20.2D, v28.2D
    trn1 v27.2D, v19.2D, v27.2D
    trn2 v30.2D, v20.2D, v28.2D
    trn2 v15.4S, v14.4S, v17.4S
    trn1 v29.4S, v31.4S, v2.4S
    trn2 v23.4S, v31.4S, v2.4S
    trn1 v21.4S, v27.4S, v30.4S
    trn2 v13.8H, v29.8H, v15.8H
    trn1 v16.8H, v29.8H, v15.8H
    trn1 v18.4S, v14.4S, v17.4S
    trn1 v25.8H, v23.8H, v21.8H
    trn2 v2.4S, v27.4S, v30.4S
    ushr v5.8H, v13.8H, #8
    shl v20.8H, v25.8H, #8
    and v24.16B, v16.16B, v0.16B
    shl v19.8H, v13.8H, #4
    trn1 v4.8H, v18.8H, v2.8H
    ushr v10.8H, v16.8H, #12
    eor v29.16B, v5.16B, v20.16B
    trn2 v15.8H, v18.8H, v2.8H
    ushr v5.8H, v25.8H, #4
    eor v19.16B, v10.16B, v19.16B
    and v26.16B, v29.16B, v0.16B
    and v27.16B, v5.16B, v0.16B
    shl v22.8H, v4.8H, #4
    and v25.16B, v19.16B, v0.16B
    shl v5.8H, v15.8H, #8
    trn2 v29.8H, v23.8H, v21.8H
    ushr v13.8H, v15.8H, #4
    ushr v6.8H, v4.8H, #8
    ushr v28.8H, v29.8H, #12
    eor v6.16B, v6.16B, v5.16B
    eor v30.16B, v28.16B, v22.16B
    and v14.16B, v29.16B, v0.16B
    and v16.16B, v6.16B, v0.16B
    and v17.16B, v13.16B, v0.16B
    and v15.16B, v30.16B, v0.16B
    trn1 v1.8h, v24.8h, v25.8h
    trn2 v2.8h, v24.8h, v25.8h
    trn1 v3.8h, v26.8h, v27.8h
    trn2 v4.8h, v26.8h, v27.8h
    trn1 v5.8h, v14.8h, v15.8h
    trn2 v6.8h, v14.8h, v15.8h
    trn1 v7.8h, v16.8h, v17.8h
    trn2 v8.8h, v16.8h, v17.8h
    trn1 v24.4s, v1.4s, v3.4s
    trn2 v26.4s, v1.4s, v3.4s
    trn1 v25.4s, v2.4s, v4.4s
    trn2 v27.4s, v2.4s, v4.4s
    trn1 v14.4s, v5.4s, v7.4s
    trn2 v16.4s, v5.4s, v7.4s
    trn1 v15.4s, v6.4s, v8.4s
    trn2 v17.4s, v6.4s, v8.4s
    trn2 v1.2d, v24.2d, v14.2d
    trn1 v24.2d, v24.2d, v14.2d
    mov v14.16b, v1.16b
    trn2 v2.2d, v25.2d, v15.2d
    trn1 v25.2d, v25.2d, v15.2d
    mov v15.16b, v2.16b
    trn2 v3.2d, v26.2d, v16.2d
    trn1 v26.2d, v26.2d, v16.2d
    mov v16.16b, v3.16b
    trn2 v4.2d, v27.2d, v17.2d
    trn1 v27.2d, v27.2d, v17.2d
    mov v17.16b, v4.16b
    str d24, [x0, #400]
    umov x9, v24.d[1]
    str x9, [x0, #424]
    str d25, [x0, #376]
    umov x9, v25.d[1]
    str x9, [x0, #352]
    str d26, [x0, #280]
    umov x9, v26.d[1]
    str x9, [x0, #256]
    str d27, [x0, #328]
    umov x9, v27.d[1]
    str x9, [x0, #304]
    str d14, [x0, #592]
    umov x9, v14.d[1]
    str x9, [x0, #616]
    str d15, [x0, #568]
    umov x9, v15.d[1]
    str x9, [x0, #544]
    str d16, [x0, #472]
    umov x9, v16.d[1]
    str x9, [x0, #448]
    str d17, [x0, #520]
    umov x9, v17.d[1]
    str x9, [x0, #496]
    // canonical blocks 80..95
    ld1 {v18.8H, v19.8H, v20.8H}, [x1], #48
    ld1 {v26.8H, v27.8H, v28.8H}, [x1], #48
    trn1 v31.2D, v18.2D, v26.2D
    trn2 v14.2D, v18.2D, v26.2D
    trn2 v2.2D, v19.2D, v27.2D
    trn1 v17.2D, v20.2D, v28.2D
    trn1 v27.2D, v19.2D, v27.2D
    trn2 v30.2D, v20.2D, v28.2D
    trn2 v15.4S, v14.4S, v17.4S
    trn1 v29.4S, v31.4S, v2.4S
    trn2 v23.4S, v31.4S, v2.4S
    trn1 v21.4S, v27.4S, v30.4S
    trn2 v13.8H, v29.8H, v15.8H
    trn1 v16.8H, v29.8H, v15.8H
    trn1 v18.4S, v14.4S, v17.4S
    trn1 v25.8H, v23.8H, v21.8H
    trn2 v2.4S, v27.4S, v30.4S
    ushr v5.8H, v13.8H, #8
    shl v20.8H, v25.8H, #8
    and v24.16B, v16.16B, v0.16B
    shl v19.8H, v13.8H, #4
    trn1 v4.8H, v18.8H, v2.8H
    ushr v10.8H, v16.8H, #12
    eor v29.16B, v5.16B, v20.16B
    trn2 v15.8H, v18.8H, v2.8H
    ushr v5.8H, v25.8H, #4
    eor v19.16B, v10.16B, v19.16B
    and v26.16B, v29.16B, v0.16B
    and v27.16B, v5.16B, v0.16B
    shl v22.8H, v4.8H, #4
    and v25.16B, v19.16B, v0.16B
    shl v5.8H, v15.8H, #8
    trn2 v29.8H, v23.8H, v21.8H
    ushr v13.8H, v15.8H, #4
    ushr v6.8H, v4.8H, #8
    ushr v28.8H, v29.8H, #12
    eor v6.16B, v6.16B, v5.16B
    eor v30.16B, v28.16B, v22.16B
    and v14.16B, v29.16B, v0.16B
    and v16.16B, v6.16B, v0.16B
    and v17.16B, v13.16B, v0.16B
    and v15.16B, v30.16B, v0.16B
    trn1 v1.8h, v24.8h, v25.8h
    trn2 v2.8h, v24.8h, v25.8h
    trn1 v3.8h, v26.8h, v27.8h
    trn2 v4.8h, v26.8h, v27.8h
    trn1 v5.8h, v14.8h, v15.8h
    trn2 v6.8h, v14.8h, v15.8h
    trn1 v7.8h, v16.8h, v17.8h
    trn2 v8.8h, v16.8h, v17.8h
    trn1 v24.4s, v1.4s, v3.4s
    trn2 v26.4s, v1.4s, v3.4s
    trn1 v25.4s, v2.4s, v4.4s
    trn2 v27.4s, v2.4s, v4.4s
    trn1 v14.4s, v5.4s, v7.4s
    trn2 v16.4s, v5.4s, v7.4s
    trn1 v15.4s, v6.4s, v8.4s
    trn2 v17.4s, v6.4s, v8.4s
    trn2 v1.2d, v24.2d, v14.2d
    trn1 v24.2d, v24.2d, v14.2d
    mov v14.16b, v1.16b
    trn2 v2.2d, v25.2d, v15.2d
    trn1 v25.2d, v25.2d, v15.2d
    mov v15.16b, v2.16b
    trn2 v3.2d, v26.2d, v16.2d
    trn1 v26.2d, v26.2d, v16.2d
    mov v16.16b, v3.16b
    trn2 v4.2d, v27.2d, v17.2d
    trn1 v27.2d, v27.2d, v17.2d
    mov v17.16b, v4.16b
    str d24, [x0, #16]
    umov x9, v24.d[1]
    str x9, [x0, #40]
    str d25, [x0, #760]
    umov x9, v25.d[1]
    str x9, [x0, #736]
    str d26, [x0, #664]
    umov x9, v26.d[1]
    str x9, [x0, #640]
    str d27, [x0, #712]
    umov x9, v27.d[1]
    str x9, [x0, #688]
    str d14, [x0, #208]
    umov x9, v14.d[1]
    str x9, [x0, #232]
    str d15, [x0, #184]
    umov x9, v15.d[1]
    str x9, [x0, #160]
    str d16, [x0, #88]
    umov x9, v16.d[1]
    str x9, [x0, #64]
    str d17, [x0, #136]
    umov x9, v17.d[1]
    str x9, [x0, #112]
    // canonical blocks 96..111
    ld1 {v18.8H, v19.8H, v20.8H}, [x1], #48
    ld1 {v26.8H, v27.8H, v28.8H}, [x1], #48
    trn1 v31.2D, v18.2D, v26.2D
    trn2 v14.2D, v18.2D, v26.2D
    trn2 v2.2D, v19.2D, v27.2D
    trn1 v17.2D, v20.2D, v28.2D
    trn1 v27.2D, v19.2D, v27.2D
    trn2 v30.2D, v20.2D, v28.2D
    trn2 v15.4S, v14.4S, v17.4S
    trn1 v29.4S, v31.4S, v2.4S
    trn2 v23.4S, v31.4S, v2.4S
    trn1 v21.4S, v27.4S, v30.4S
    trn2 v13.8H, v29.8H, v15.8H
    trn1 v16.8H, v29.8H, v15.8H
    trn1 v18.4S, v14.4S, v17.4S
    trn1 v25.8H, v23.8H, v21.8H
    trn2 v2.4S, v27.4S, v30.4S
    ushr v5.8H, v13.8H, #8
    shl v20.8H, v25.8H, #8
    and v24.16B, v16.16B, v0.16B
    shl v19.8H, v13.8H, #4
    trn1 v4.8H, v18.8H, v2.8H
    ushr v10.8H, v16.8H, #12
    eor v29.16B, v5.16B, v20.16B
    trn2 v15.8H, v18.8H, v2.8H
    ushr v5.8H, v25.8H, #4
    eor v19.16B, v10.16B, v19.16B
    and v26.16B, v29.16B, v0.16B
    and v27.16B, v5.16B, v0.16B
    shl v22.8H, v4.8H, #4
    and v25.16B, v19.16B, v0.16B
    shl v5.8H, v15.8H, #8
    trn2 v29.8H, v23.8H, v21.8H
    ushr v13.8H, v15.8H, #4
    ushr v6.8H, v4.8H, #8
    ushr v28.8H, v29.8H, #12
    eor v6.16B, v6.16B, v5.16B
    eor v30.16B, v28.16B, v22.16B
    and v14.16B, v29.16B, v0.16B
    and v16.16B, v6.16B, v0.16B
    and v17.16B, v13.16B, v0.16B
    and v15.16B, v30.16B, v0.16B
    trn1 v1.8h, v24.8h, v25.8h
    trn2 v2.8h, v24.8h, v25.8h
    trn1 v3.8h, v26.8h, v27.8h
    trn2 v4.8h, v26.8h, v27.8h
    trn1 v5.8h, v14.8h, v15.8h
    trn2 v6.8h, v14.8h, v15.8h
    trn1 v7.8h, v16.8h, v17.8h
    trn2 v8.8h, v16.8h, v17.8h
    trn1 v24.4s, v1.4s, v3.4s
    trn2 v26.4s, v1.4s, v3.4s
    trn1 v25.4s, v2.4s, v4.4s
    trn2 v27.4s, v2.4s, v4.4s
    trn1 v14.4s, v5.4s, v7.4s
    trn2 v16.4s, v5.4s, v7.4s
    trn1 v15.4s, v6.4s, v8.4s
    trn2 v17.4s, v6.4s, v8.4s
    trn2 v1.2d, v24.2d, v14.2d
    trn1 v24.2d, v24.2d, v14.2d
    mov v14.16b, v1.16b
    trn2 v2.2d, v25.2d, v15.2d
    trn1 v25.2d, v25.2d, v15.2d
    mov v15.16b, v2.16b
    trn2 v3.2d, v26.2d, v16.2d
    trn1 v26.2d, v26.2d, v16.2d
    mov v16.16b, v3.16b
    trn2 v4.2d, v27.2d, v17.2d
    trn1 v27.2d, v27.2d, v17.2d
    mov v17.16b, v4.16b
    str d24, [x0, #1136]
    umov x9, v24.d[1]
    str x9, [x0, #1160]
    str d25, [x0, #1112]
    umov x9, v25.d[1]
    str x9, [x0, #1088]
    str d26, [x0, #1232]
    umov x9, v26.d[1]
    str x9, [x0, #1256]
    str d27, [x0, #1208]
    umov x9, v27.d[1]
    str x9, [x0, #1184]
    str d14, [x0, #1040]
    umov x9, v14.d[1]
    str x9, [x0, #1064]
    str d15, [x0, #1016]
    umov x9, v15.d[1]
    str x9, [x0, #992]
    str d16, [x0, #920]
    umov x9, v16.d[1]
    str x9, [x0, #896]
    str d17, [x0, #968]
    umov x9, v17.d[1]
    str x9, [x0, #944]
    // canonical blocks 112..127
    ld1 {v18.8H, v19.8H, v20.8H}, [x1], #48
    ld1 {v26.8H, v27.8H, v28.8H}, [x1], #48
    trn1 v31.2D, v18.2D, v26.2D
    trn2 v14.2D, v18.2D, v26.2D
    trn2 v2.2D, v19.2D, v27.2D
    trn1 v17.2D, v20.2D, v28.2D
    trn1 v27.2D, v19.2D, v27.2D
    trn2 v30.2D, v20.2D, v28.2D
    trn2 v15.4S, v14.4S, v17.4S
    trn1 v29.4S, v31.4S, v2.4S
    trn2 v23.4S, v31.4S, v2.4S
    trn1 v21.4S, v27.4S, v30.4S
    trn2 v13.8H, v29.8H, v15.8H
    trn1 v16.8H, v29.8H, v15.8H
    trn1 v18.4S, v14.4S, v17.4S
    trn1 v25.8H, v23.8H, v21.8H
    trn2 v2.4S, v27.4S, v30.4S
    ushr v5.8H, v13.8H, #8
    shl v20.8H, v25.8H, #8
    and v24.16B, v16.16B, v0.16B
    shl v19.8H, v13.8H, #4
    trn1 v4.8H, v18.8H, v2.8H
    ushr v10.8H, v16.8H, #12
    eor v29.16B, v5.16B, v20.16B
    trn2 v15.8H, v18.8H, v2.8H
    ushr v5.8H, v25.8H, #4
    eor v19.16B, v10.16B, v19.16B
    and v26.16B, v29.16B, v0.16B
    and v27.16B, v5.16B, v0.16B
    shl v22.8H, v4.8H, #4
    and v25.16B, v19.16B, v0.16B
    shl v5.8H, v15.8H, #8
    trn2 v29.8H, v23.8H, v21.8H
    ushr v13.8H, v15.8H, #4
    ushr v6.8H, v4.8H, #8
    ushr v28.8H, v29.8H, #12
    eor v6.16B, v6.16B, v5.16B
    eor v30.16B, v28.16B, v22.16B
    and v14.16B, v29.16B, v0.16B
    and v16.16B, v6.16B, v0.16B
    and v17.16B, v13.16B, v0.16B
    and v15.16B, v30.16B, v0.16B
    trn1 v1.8h, v24.8h, v25.8h
    trn2 v2.8h, v24.8h, v25.8h
    trn1 v3.8h, v26.8h, v27.8h
    trn2 v4.8h, v26.8h, v27.8h
    trn1 v5.8h, v14.8h, v15.8h
    trn2 v6.8h, v14.8h, v15.8h
    trn1 v7.8h, v16.8h, v17.8h
    trn2 v8.8h, v16.8h, v17.8h
    trn1 v24.4s, v1.4s, v3.4s
    trn2 v26.4s, v1.4s, v3.4s
    trn1 v25.4s, v2.4s, v4.4s
    trn2 v27.4s, v2.4s, v4.4s
    trn1 v14.4s, v5.4s, v7.4s
    trn2 v16.4s, v5.4s, v7.4s
    trn1 v15.4s, v6.4s, v8.4s
    trn2 v17.4s, v6.4s, v8.4s
    trn2 v1.2d, v24.2d, v14.2d
    trn1 v24.2d, v24.2d, v14.2d
    mov v14.16b, v1.16b
    trn2 v2.2d, v25.2d, v15.2d
    trn1 v25.2d, v25.2d, v15.2d
    mov v15.16b, v2.16b
    trn2 v3.2d, v26.2d, v16.2d
    trn1 v26.2d, v26.2d, v16.2d
    mov v16.16b, v3.16b
    trn2 v4.2d, v27.2d, v17.2d
    trn1 v27.2d, v27.2d, v17.2d
    mov v17.16b, v4.16b
    str d24, [x0, #1424]
    umov x9, v24.d[1]
    str x9, [x0, #1448]
    str d25, [x0, #1400]
    umov x9, v25.d[1]
    str x9, [x0, #1376]
    str d26, [x0, #1304]
    umov x9, v26.d[1]
    str x9, [x0, #1280]
    str d27, [x0, #1352]
    umov x9, v27.d[1]
    str x9, [x0, #1328]
    str d14, [x0, #848]
    umov x9, v14.d[1]
    str x9, [x0, #872]
    str d15, [x0, #824]
    umov x9, v15.d[1]
    str x9, [x0, #800]
    str d16, [x0, #1496]
    umov x9, v16.d[1]
    str x9, [x0, #1472]
    str d17, [x0, #776]
    umov x9, v17.d[1]
    str x9, [x0, #1520]
    // canonical blocks 128..143
    ld1 {v18.8H, v19.8H, v20.8H}, [x1], #48
    ld1 {v26.8H, v27.8H, v28.8H}, [x1], #48
    trn1 v31.2D, v18.2D, v26.2D
    trn2 v14.2D, v18.2D, v26.2D
    trn2 v2.2D, v19.2D, v27.2D
    trn1 v17.2D, v20.2D, v28.2D
    trn1 v27.2D, v19.2D, v27.2D
    trn2 v30.2D, v20.2D, v28.2D
    trn2 v15.4S, v14.4S, v17.4S
    trn1 v29.4S, v31.4S, v2.4S
    trn2 v23.4S, v31.4S, v2.4S
    trn1 v21.4S, v27.4S, v30.4S
    trn2 v13.8H, v29.8H, v15.8H
    trn1 v16.8H, v29.8H, v15.8H
    trn1 v18.4S, v14.4S, v17.4S
    trn1 v25.8H, v23.8H, v21.8H
    trn2 v2.4S, v27.4S, v30.4S
    ushr v5.8H, v13.8H, #8
    shl v20.8H, v25.8H, #8
    and v24.16B, v16.16B, v0.16B
    shl v19.8H, v13.8H, #4
    trn1 v4.8H, v18.8H, v2.8H
    ushr v10.8H, v16.8H, #12
    eor v29.16B, v5.16B, v20.16B
    trn2 v15.8H, v18.8H, v2.8H
    ushr v5.8H, v25.8H, #4
    eor v19.16B, v10.16B, v19.16B
    and v26.16B, v29.16B, v0.16B
    and v27.16B, v5.16B, v0.16B
    shl v22.8H, v4.8H, #4
    and v25.16B, v19.16B, v0.16B
    shl v5.8H, v15.8H, #8
    trn2 v29.8H, v23.8H, v21.8H
    ushr v13.8H, v15.8H, #4
    ushr v6.8H, v4.8H, #8
    ushr v28.8H, v29.8H, #12
    eor v6.16B, v6.16B, v5.16B
    eor v30.16B, v28.16B, v22.16B
    and v14.16B, v29.16B, v0.16B
    and v16.16B, v6.16B, v0.16B
    and v17.16B, v13.16B, v0.16B
    and v15.16B, v30.16B, v0.16B
    trn1 v1.8h, v24.8h, v25.8h
    trn2 v2.8h, v24.8h, v25.8h
    trn1 v3.8h, v26.8h, v27.8h
    trn2 v4.8h, v26.8h, v27.8h
    trn1 v5.8h, v14.8h, v15.8h
    trn2 v6.8h, v14.8h, v15.8h
    trn1 v7.8h, v16.8h, v17.8h
    trn2 v8.8h, v16.8h, v17.8h
    trn1 v24.4s, v1.4s, v3.4s
    trn2 v26.4s, v1.4s, v3.4s
    trn1 v25.4s, v2.4s, v4.4s
    trn2 v27.4s, v2.4s, v4.4s
    trn1 v14.4s, v5.4s, v7.4s
    trn2 v16.4s, v5.4s, v7.4s
    trn1 v15.4s, v6.4s, v8.4s
    trn2 v17.4s, v6.4s, v8.4s
    trn2 v1.2d, v24.2d, v14.2d
    trn1 v24.2d, v24.2d, v14.2d
    mov v14.16b, v1.16b
    trn2 v2.2d, v25.2d, v15.2d
    trn1 v25.2d, v25.2d, v15.2d
    mov v15.16b, v2.16b
    trn2 v3.2d, v26.2d, v16.2d
    trn1 v26.2d, v26.2d, v16.2d
    mov v16.16b, v3.16b
    trn2 v4.2d, v27.2d, v17.2d
    trn1 v27.2d, v27.2d, v17.2d
    mov v17.16b, v4.16b
    str d24, [x0, #1336]
    umov x9, v24.d[1]
    str x9, [x0, #1312]
    str d25, [x0, #1384]
    umov x9, v25.d[1]
    str x9, [x0, #1360]
    str d26, [x0, #1288]
    umov x9, v26.d[1]
    str x9, [x0, #1264]
    str d27, [x0, #1216]
    umov x9, v27.d[1]
    str x9, [x0, #1240]
    str d14, [x0, #1096]
    umov x9, v14.d[1]
    str x9, [x0, #1072]
    str d15, [x0, #1024]
    umov x9, v15.d[1]
    str x9, [x0, #1048]
    str d16, [x0, #1192]
    umov x9, v16.d[1]
    str x9, [x0, #1168]
    str d17, [x0, #1120]
    umov x9, v17.d[1]
    str x9, [x0, #1144]
    // canonical blocks 144..159
    ld1 {v18.8H, v19.8H, v20.8H}, [x1], #48
    ld1 {v26.8H, v27.8H, v28.8H}, [x1], #48
    trn1 v31.2D, v18.2D, v26.2D
    trn2 v14.2D, v18.2D, v26.2D
    trn2 v2.2D, v19.2D, v27.2D
    trn1 v17.2D, v20.2D, v28.2D
    trn1 v27.2D, v19.2D, v27.2D
    trn2 v30.2D, v20.2D, v28.2D
    trn2 v15.4S, v14.4S, v17.4S
    trn1 v29.4S, v31.4S, v2.4S
    trn2 v23.4S, v31.4S, v2.4S
    trn1 v21.4S, v27.4S, v30.4S
    trn2 v13.8H, v29.8H, v15.8H
    trn1 v16.8H, v29.8H, v15.8H
    trn1 v18.4S, v14.4S, v17.4S
    trn1 v25.8H, v23.8H, v21.8H
    trn2 v2.4S, v27.4S, v30.4S
    ushr v5.8H, v13.8H, #8
    shl v20.8H, v25.8H, #8
    and v24.16B, v16.16B, v0.16B
    shl v19.8H, v13.8H, #4
    trn1 v4.8H, v18.8H, v2.8H
    ushr v10.8H, v16.8H, #12
    eor v29.16B, v5.16B, v20.16B
    trn2 v15.8H, v18.8H, v2.8H
    ushr v5.8H, v25.8H, #4
    eor v19.16B, v10.16B, v19.16B
    and v26.16B, v29.16B, v0.16B
    and v27.16B, v5.16B, v0.16B
    shl v22.8H, v4.8H, #4
    and v25.16B, v19.16B, v0.16B
    shl v5.8H, v15.8H, #8
    trn2 v29.8H, v23.8H, v21.8H
    ushr v13.8H, v15.8H, #4
    ushr v6.8H, v4.8H, #8
    ushr v28.8H, v29.8H, #12
    eor v6.16B, v6.16B, v5.16B
    eor v30.16B, v28.16B, v22.16B
    and v14.16B, v29.16B, v0.16B
    and v16.16B, v6.16B, v0.16B
    and v17.16B, v13.16B, v0.16B
    and v15.16B, v30.16B, v0.16B
    trn1 v1.8h, v24.8h, v25.8h
    trn2 v2.8h, v24.8h, v25.8h
    trn1 v3.8h, v26.8h, v27.8h
    trn2 v4.8h, v26.8h, v27.8h
    trn1 v5.8h, v14.8h, v15.8h
    trn2 v6.8h, v14.8h, v15.8h
    trn1 v7.8h, v16.8h, v17.8h
    trn2 v8.8h, v16.8h, v17.8h
    trn1 v24.4s, v1.4s, v3.4s
    trn2 v26.4s, v1.4s, v3.4s
    trn1 v25.4s, v2.4s, v4.4s
    trn2 v27.4s, v2.4s, v4.4s
    trn1 v14.4s, v5.4s, v7.4s
    trn2 v16.4s, v5.4s, v7.4s
    trn1 v15.4s, v6.4s, v8.4s
    trn2 v17.4s, v6.4s, v8.4s
    trn2 v1.2d, v24.2d, v14.2d
    trn1 v24.2d, v24.2d, v14.2d
    mov v14.16b, v1.16b
    trn2 v2.2d, v25.2d, v15.2d
    trn1 v25.2d, v25.2d, v15.2d
    mov v15.16b, v2.16b
    trn2 v3.2d, v26.2d, v16.2d
    trn1 v26.2d, v26.2d, v16.2d
    mov v16.16b, v3.16b
    trn2 v4.2d, v27.2d, v17.2d
    trn1 v27.2d, v27.2d, v17.2d
    mov v17.16b, v4.16b
    str d24, [x0, #952]
    umov x9, v24.d[1]
    str x9, [x0, #928]
    str d25, [x0, #1000]
    umov x9, v25.d[1]
    str x9, [x0, #976]
    str d26, [x0, #904]
    umov x9, v26.d[1]
    str x9, [x0, #880]
    str d27, [x0, #832]
    umov x9, v27.d[1]
    str x9, [x0, #856]
    str d14, [x0, #1480]
    umov x9, v14.d[1]
    str x9, [x0, #1456]
    str d15, [x0, #1408]
    umov x9, v15.d[1]
    str x9, [x0, #1432]
    str d16, [x0, #808]
    umov x9, v16.d[1]
    str x9, [x0, #784]
    str d17, [x0, #1504]
    umov x9, v17.d[1]
    str x9, [x0, #1528]
    // canonical blocks 160..175
    ld1 {v18.8H, v19.8H, v20.8H}, [x1], #48
    ld1 {v26.8H, v27.8H, v28.8H}, [x1], #48
    trn1 v31.2D, v18.2D, v26.2D
    trn2 v14.2D, v18.2D, v26.2D
    trn2 v2.2D, v19.2D, v27.2D
    trn1 v17.2D, v20.2D, v28.2D
    trn1 v27.2D, v19.2D, v27.2D
    trn2 v30.2D, v20.2D, v28.2D
    trn2 v15.4S, v14.4S, v17.4S
    trn1 v29.4S, v31.4S, v2.4S
    trn2 v23.4S, v31.4S, v2.4S
    trn1 v21.4S, v27.4S, v30.4S
    trn2 v13.8H, v29.8H, v15.8H
    trn1 v16.8H, v29.8H, v15.8H
    trn1 v18.4S, v14.4S, v17.4S
    trn1 v25.8H, v23.8H, v21.8H
    trn2 v2.4S, v27.4S, v30.4S
    ushr v5.8H, v13.8H, #8
    shl v20.8H, v25.8H, #8
    and v24.16B, v16.16B, v0.16B
    shl v19.8H, v13.8H, #4
    trn1 v4.8H, v18.8H, v2.8H
    ushr v10.8H, v16.8H, #12
    eor v29.16B, v5.16B, v20.16B
    trn2 v15.8H, v18.8H, v2.8H
    ushr v5.8H, v25.8H, #4
    eor v19.16B, v10.16B, v19.16B
    and v26.16B, v29.16B, v0.16B
    and v27.16B, v5.16B, v0.16B
    shl v22.8H, v4.8H, #4
    and v25.16B, v19.16B, v0.16B
    shl v5.8H, v15.8H, #8
    trn2 v29.8H, v23.8H, v21.8H
    ushr v13.8H, v15.8H, #4
    ushr v6.8H, v4.8H, #8
    ushr v28.8H, v29.8H, #12
    eor v6.16B, v6.16B, v5.16B
    eor v30.16B, v28.16B, v22.16B
    and v14.16B, v29.16B, v0.16B
    and v16.16B, v6.16B, v0.16B
    and v17.16B, v13.16B, v0.16B
    and v15.16B, v30.16B, v0.16B
    trn1 v1.8h, v24.8h, v25.8h
    trn2 v2.8h, v24.8h, v25.8h
    trn1 v3.8h, v26.8h, v27.8h
    trn2 v4.8h, v26.8h, v27.8h
    trn1 v5.8h, v14.8h, v15.8h
    trn2 v6.8h, v14.8h, v15.8h
    trn1 v7.8h, v16.8h, v17.8h
    trn2 v8.8h, v16.8h, v17.8h
    trn1 v24.4s, v1.4s, v3.4s
    trn2 v26.4s, v1.4s, v3.4s
    trn1 v25.4s, v2.4s, v4.4s
    trn2 v27.4s, v2.4s, v4.4s
    trn1 v14.4s, v5.4s, v7.4s
    trn2 v16.4s, v5.4s, v7.4s
    trn1 v15.4s, v6.4s, v8.4s
    trn2 v17.4s, v6.4s, v8.4s
    trn2 v1.2d, v24.2d, v14.2d
    trn1 v24.2d, v24.2d, v14.2d
    mov v14.16b, v1.16b
    trn2 v2.2d, v25.2d, v15.2d
    trn1 v25.2d, v25.2d, v15.2d
    mov v15.16b, v2.16b
    trn2 v3.2d, v26.2d, v16.2d
    trn1 v26.2d, v26.2d, v16.2d
    mov v16.16b, v3.16b
    trn2 v4.2d, v27.2d, v17.2d
    trn1 v27.2d, v27.2d, v17.2d
    mov v17.16b, v4.16b
    str d24, [x0, #1152]
    umov x9, v24.d[1]
    str x9, [x0, #1176]
    str d25, [x0, #1200]
    umov x9, v25.d[1]
    str x9, [x0, #1224]
    str d26, [x0, #1248]
    umov x9, v26.d[1]
    str x9, [x0, #1272]
    str d27, [x0, #1296]
    umov x9, v27.d[1]
    str x9, [x0, #1320]
    str d14, [x0, #1344]
    umov x9, v14.d[1]
    str x9, [x0, #1368]
    str d15, [x0, #1392]
    umov x9, v15.d[1]
    str x9, [x0, #1416]
    str d16, [x0, #1440]
    umov x9, v16.d[1]
    str x9, [x0, #1464]
    str d17, [x0, #1488]
    umov x9, v17.d[1]
    str x9, [x0, #1512]
    // canonical blocks 176..191
    ld1 {v18.8H, v19.8H, v20.8H}, [x1], #48
    ld1 {v26.8H, v27.8H, v28.8H}, [x1], #48
    trn1 v31.2D, v18.2D, v26.2D
    trn2 v14.2D, v18.2D, v26.2D
    trn2 v2.2D, v19.2D, v27.2D
    trn1 v17.2D, v20.2D, v28.2D
    trn1 v27.2D, v19.2D, v27.2D
    trn2 v30.2D, v20.2D, v28.2D
    trn2 v15.4S, v14.4S, v17.4S
    trn1 v29.4S, v31.4S, v2.4S
    trn2 v23.4S, v31.4S, v2.4S
    trn1 v21.4S, v27.4S, v30.4S
    trn2 v13.8H, v29.8H, v15.8H
    trn1 v16.8H, v29.8H, v15.8H
    trn1 v18.4S, v14.4S, v17.4S
    trn1 v25.8H, v23.8H, v21.8H
    trn2 v2.4S, v27.4S, v30.4S
    ushr v5.8H, v13.8H, #8
    shl v20.8H, v25.8H, #8
    and v24.16B, v16.16B, v0.16B
    shl v19.8H, v13.8H, #4
    trn1 v4.8H, v18.8H, v2.8H
    ushr v10.8H, v16.8H, #12
    eor v29.16B, v5.16B, v20.16B
    trn2 v15.8H, v18.8H, v2.8H
    ushr v5.8H, v25.8H, #4
    eor v19.16B, v10.16B, v19.16B
    and v26.16B, v29.16B, v0.16B
    and v27.16B, v5.16B, v0.16B
    shl v22.8H, v4.8H, #4
    and v25.16B, v19.16B, v0.16B
    shl v5.8H, v15.8H, #8
    trn2 v29.8H, v23.8H, v21.8H
    ushr v13.8H, v15.8H, #4
    ushr v6.8H, v4.8H, #8
    ushr v28.8H, v29.8H, #12
    eor v6.16B, v6.16B, v5.16B
    eor v30.16B, v28.16B, v22.16B
    and v14.16B, v29.16B, v0.16B
    and v16.16B, v6.16B, v0.16B
    and v17.16B, v13.16B, v0.16B
    and v15.16B, v30.16B, v0.16B
    trn1 v1.8h, v24.8h, v25.8h
    trn2 v2.8h, v24.8h, v25.8h
    trn1 v3.8h, v26.8h, v27.8h
    trn2 v4.8h, v26.8h, v27.8h
    trn1 v5.8h, v14.8h, v15.8h
    trn2 v6.8h, v14.8h, v15.8h
    trn1 v7.8h, v16.8h, v17.8h
    trn2 v8.8h, v16.8h, v17.8h
    trn1 v24.4s, v1.4s, v3.4s
    trn2 v26.4s, v1.4s, v3.4s
    trn1 v25.4s, v2.4s, v4.4s
    trn2 v27.4s, v2.4s, v4.4s
    trn1 v14.4s, v5.4s, v7.4s
    trn2 v16.4s, v5.4s, v7.4s
    trn1 v15.4s, v6.4s, v8.4s
    trn2 v17.4s, v6.4s, v8.4s
    trn2 v1.2d, v24.2d, v14.2d
    trn1 v24.2d, v24.2d, v14.2d
    mov v14.16b, v1.16b
    trn2 v2.2d, v25.2d, v15.2d
    trn1 v25.2d, v25.2d, v15.2d
    mov v15.16b, v2.16b
    trn2 v3.2d, v26.2d, v16.2d
    trn1 v26.2d, v26.2d, v16.2d
    mov v16.16b, v3.16b
    trn2 v4.2d, v27.2d, v17.2d
    trn1 v27.2d, v27.2d, v17.2d
    mov v17.16b, v4.16b
    str d24, [x0, #960]
    umov x9, v24.d[1]
    str x9, [x0, #984]
    str d25, [x0, #1008]
    umov x9, v25.d[1]
    str x9, [x0, #1032]
    str d26, [x0, #1056]
    umov x9, v26.d[1]
    str x9, [x0, #1080]
    str d27, [x0, #1104]
    umov x9, v27.d[1]
    str x9, [x0, #1128]
    str d14, [x0, #864]
    umov x9, v14.d[1]
    str x9, [x0, #888]
    str d15, [x0, #912]
    umov x9, v15.d[1]
    str x9, [x0, #936]
    str d16, [x0, #816]
    umov x9, v16.d[1]
    str x9, [x0, #840]
    str d17, [x0, #792]
    umov x9, v17.d[1]
    str x9, [x0, #768]
    ldp d8, d9, [sp, #0]
    ldp d10, d11, [sp, #16]
    ldp d12, d13, [sp, #32]
    ldp d14, d15, [sp, #48]
    add sp, sp, #64
    ret

.p2align 4
canonical_pack_const_mask_0fff:
    .hword 0x0fff, 0x0fff, 0x0fff, 0x0fff
    .hword 0x0fff, 0x0fff, 0x0fff, 0x0fff
#endif

.p2align 4
canonical_pack_const_q:
    .hword 3457, 3457, 3457, 3457
    .hword 3457, 3457, 3457, 3457
