/* BEGIN original pack.S; private namespace module_pack_ */
/* Production Wave 8 dual-entry canonical pack. */
/* Promoted from production_pack_sha256=03d69c69946f5e55f5c6b1f13bf1a62f43f2b1453b246c8dc8f5f39b2482b346. */
/* poly_tobytes_encap keeps the reduced fast path; the Wave 8 entry */
/* canonicalizes arbitrary signed-16 block-major representatives. */
// Production compact shared-core canonical pack.
#ifdef __APPLE__
.text
#else
.section .text.module_pack_body,"ax",%progbits
#endif
.p2align 4
.global poly_tobytes_encap
.global _poly_tobytes_encap
#ifndef __APPLE__
.type poly_tobytes_encap, %function
#endif
.global poly_tobytes_encap_loose
.global _poly_tobytes_encap_loose
#ifndef __APPLE__
.type poly_tobytes_encap_loose, %function
#endif
poly_tobytes_encap_loose:
_poly_tobytes_encap_loose:
    mov w3, #1
    b module_pack_.Lwave8_dual_pack_entry
poly_tobytes_encap:
_poly_tobytes_encap:
    mov w3, #0
module_pack_.Lwave8_dual_pack_entry:
    sub sp, sp, #80
    stp d8, d9, [sp, #0]
    stp d10, d11, [sp, #16]
    stp d12, d13, [sp, #32]
    stp d14, d15, [sp, #48]
    str x30, [sp, #64]
    adr x2, module_pack_.Lcanonical_pack_compact_q
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
    bl module_pack_.Lcanonical_pack_compact_core
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
    bl module_pack_.Lcanonical_pack_compact_core
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
    bl module_pack_.Lcanonical_pack_compact_core
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
    bl module_pack_.Lcanonical_pack_compact_core
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
    bl module_pack_.Lcanonical_pack_compact_core
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
    bl module_pack_.Lcanonical_pack_compact_core
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
    bl module_pack_.Lcanonical_pack_compact_core
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
    bl module_pack_.Lcanonical_pack_compact_core
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
    bl module_pack_.Lcanonical_pack_compact_core
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
    bl module_pack_.Lcanonical_pack_compact_core
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
    bl module_pack_.Lcanonical_pack_compact_core
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
    bl module_pack_.Lcanonical_pack_compact_core
    ldr x30, [sp, #64]
    ldp d8, d9, [sp, #0]
    ldp d10, d11, [sp, #16]
    ldp d12, d13, [sp, #32]
    ldp d14, d15, [sp, #48]
    add sp, sp, #80
    ret

.p2align 4
module_pack_.Lcanonical_pack_compact_core:
    /* WAVE8 v2: skip this block for already-reduced consumers. */
    cbz w3, module_pack_.Lwave8_pack_already_reduced
    ldr q30, [x2, #16]
    sqdmulh v31.8H, v1.8H, v30.8H
    srshr v31.8H, v31.8H, #11
    mls v1.8H, v31.8H, v0.8H
    sqdmulh v31.8H, v2.8H, v30.8H
    srshr v31.8H, v31.8H, #11
    mls v2.8H, v31.8H, v0.8H
    sqdmulh v31.8H, v3.8H, v30.8H
    srshr v31.8H, v31.8H, #11
    mls v3.8H, v31.8H, v0.8H
    sqdmulh v31.8H, v4.8H, v30.8H
    srshr v31.8H, v31.8H, #11
    mls v4.8H, v31.8H, v0.8H
    sqdmulh v31.8H, v5.8H, v30.8H
    srshr v31.8H, v31.8H, #11
    mls v5.8H, v31.8H, v0.8H
    sqdmulh v31.8H, v6.8H, v30.8H
    srshr v31.8H, v31.8H, #11
    mls v6.8H, v31.8H, v0.8H
    sqdmulh v31.8H, v7.8H, v30.8H
    srshr v31.8H, v31.8H, #11
    mls v7.8H, v31.8H, v0.8H
    sqdmulh v31.8H, v8.8H, v30.8H
    srshr v31.8H, v31.8H, #11
    mls v8.8H, v31.8H, v0.8H
module_pack_.Lwave8_pack_already_reduced:
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
module_pack_.Lcanonical_pack_compact_q:
    .hword 3457, 3457, 3457, 3457
    .hword 3457, 3457, 3457, 3457
    /* Barrett quotient constant, one value per halfword lane. */
    .hword 19412, 19412, 19412, 19412
    .hword 19412, 19412, 19412, 19412
#ifndef __APPLE__
.size poly_tobytes_encap, .-poly_tobytes_encap
#endif

/* END original pack.S */

/* BEGIN original unpack.S; private namespace module_unpack_ */
// Generated checked U1 canonical unpack from clean GT Production; strategy=globalmax.
#ifdef __APPLE__
.text
#else
.section .text.module_unpack_body,"ax",%progbits
#endif
.p2align 4
.global poly_frombytes_encap
.global _poly_frombytes_encap
poly_frombytes_encap:
_poly_frombytes_encap:
    sub sp, sp, #64
    stp d8, d9, [sp, #0]
    stp d10, d11, [sp, #16]
    stp d12, d13, [sp, #32]
    stp d14, d15, [sp, #48]
    adr x2, module_unpack_.Lcanonical_unpack_candidate_mask
    ldr q0, [x2]
    mov w10, #3457
    dup v8.8h, w10
    movi v7.16b, #0
    movi v22.16b, #0
    movi v24.16b, #0
    movi v25.16b, #0
    // canonical blocks 0..15
    ld1 {v14.8H, v15.8H, v16.8H}, [x1], #48
    ld1 {v18.8H, v19.8H, v20.8H}, [x1], #48
    trn2 v9.2D, v16.2D, v20.2D
    trn1 v4.2D, v16.2D, v20.2D
    trn2 v30.2D, v14.2D, v18.2D
    trn1 v11.2D, v15.2D, v19.2D
    trn2 v12.2D, v15.2D, v19.2D
    trn1 v23.2D, v14.2D, v18.2D
    trn1 v31.4S, v30.4S, v4.4S
    trn2 v5.4S, v11.4S, v9.4S
    trn2 v15.4S, v30.4S, v4.4S
    trn1 v29.4S, v23.4S, v12.4S
    trn2 v14.4S, v23.4S, v12.4S
    trn2 v4.8H, v31.8H, v5.8H
    trn1 v27.4S, v11.4S, v9.4S
    trn2 v11.8H, v29.8H, v15.8H
    trn1 v31.8H, v31.8H, v5.8H
    ushr v10.8H, v4.8H, #4
    trn2 v26.8H, v14.8H, v27.8H
    ushr v28.8H, v11.8H, #8
    ushr v21.8H, v31.8H, #8
    trn1 v1.8H, v29.8H, v15.8H
    ushr v18.8H, v26.8H, #12
    and v6.16B, v26.16B, v0.16B
    trn1 v19.8H, v14.8H, v27.8H
    shl v30.8H, v31.8H, #4
    shl v12.8H, v4.8H, #8
    and v23.16B, v1.16B, v0.16B
    eor v31.16B, v18.16B, v30.16B
    shl v13.8H, v11.8H, #4
    eor v3.16B, v21.16B, v12.16B
    ushr v9.8H, v1.8H, #12
    shl v2.8H, v19.8H, #8
    and v20.16B, v31.16B, v0.16B
    eor v12.16B, v9.16B, v13.16B
    ushr v17.8H, v19.8H, #4
    and v31.16B, v10.16B, v0.16B
    eor v9.16B, v28.16B, v2.16B
    and v13.16B, v17.16B, v0.16B
    and v15.16B, v12.16B, v0.16B
    and v10.16B, v9.16B, v0.16B
    and v3.16B, v3.16B, v0.16B
    // Accumulate four independent unsigned maxima.
    umax v7.8h, v7.8h, v6.8h
    umax v7.8h, v7.8h, v23.8h
    umax v22.8h, v22.8h, v20.8h
    umax v22.8h, v22.8h, v31.8h
    umax v24.8h, v24.8h, v13.8h
    umax v24.8h, v24.8h, v15.8h
    umax v25.8h, v25.8h, v10.8h
    umax v25.8h, v25.8h, v3.8h
    trn1 v21.8H, v6.8H, v20.8H
    trn1 v2.8H, v23.8H, v15.8H
    trn1 v4.8H, v3.8H, v31.8H
    trn1 v14.8H, v10.8H, v13.8H
    trn2 v9.8H, v10.8H, v13.8H
    trn2 v26.8H, v3.8H, v31.8H
    trn2 v28.4S, v2.4S, v14.4S
    trn2 v17.4S, v21.4S, v4.4S
    trn1 v19.4S, v2.4S, v14.4S
    trn2 v30.8H, v6.8H, v20.8H
    trn2 v20.2D, v28.2D, v17.2D
    trn2 v5.8H, v23.8H, v15.8H
    trn1 v27.4S, v30.4S, v26.4S
    umov x9, v20.d[1]
    trn2 v10.4S, v30.4S, v26.4S
    trn1 v14.2D, v28.2D, v17.2D
    trn2 v28.4S, v5.4S, v9.4S
    trn1 v30.4S, v21.4S, v4.4S
    trn1 v18.4S, v5.4S, v9.4S
    str x9, [x0, #144]
    umov x9, v14.d[1]
    trn2 v31.2D, v28.2D, v10.2D
    trn1 v3.2D, v28.2D, v10.2D
    trn1 v23.2D, v19.2D, v30.2D
    trn2 v4.2D, v19.2D, v30.2D
    str d14, [x0, #264]
    str x9, [x0, #240]
    trn1 v17.2D, v18.2D, v27.2D
    umov x9, v23.d[1]
    str d23, [x0, #312]
    str d4, [x0, #72]
    trn2 v23.2D, v18.2D, v27.2D
    str d17, [x0, #360]
    str x9, [x0, #288]
    umov x9, v4.d[1]
    str d31, [x0, #96]
    str d23, [x0, #0]
    str x9, [x0, #48]
    umov x9, v23.d[1]
    str d3, [x0, #192]
    str x9, [x0, #24]
    umov x9, v17.d[1]
    str x9, [x0, #336]
    umov x9, v3.d[1]
    str d20, [x0, #168]
    str x9, [x0, #216]
    umov x9, v31.d[1]
    str x9, [x0, #120]
    // canonical blocks 16..31
    ld1 {v14.8H, v15.8H, v16.8H}, [x1], #48
    ld1 {v18.8H, v19.8H, v20.8H}, [x1], #48
    trn2 v9.2D, v16.2D, v20.2D
    trn1 v4.2D, v16.2D, v20.2D
    trn2 v30.2D, v14.2D, v18.2D
    trn1 v11.2D, v15.2D, v19.2D
    trn2 v12.2D, v15.2D, v19.2D
    trn1 v23.2D, v14.2D, v18.2D
    trn1 v31.4S, v30.4S, v4.4S
    trn2 v5.4S, v11.4S, v9.4S
    trn2 v15.4S, v30.4S, v4.4S
    trn1 v29.4S, v23.4S, v12.4S
    trn2 v14.4S, v23.4S, v12.4S
    trn2 v4.8H, v31.8H, v5.8H
    trn1 v27.4S, v11.4S, v9.4S
    trn2 v11.8H, v29.8H, v15.8H
    trn1 v31.8H, v31.8H, v5.8H
    ushr v10.8H, v4.8H, #4
    trn2 v26.8H, v14.8H, v27.8H
    ushr v28.8H, v11.8H, #8
    ushr v21.8H, v31.8H, #8
    trn1 v1.8H, v29.8H, v15.8H
    ushr v18.8H, v26.8H, #12
    and v6.16B, v26.16B, v0.16B
    trn1 v19.8H, v14.8H, v27.8H
    shl v30.8H, v31.8H, #4
    shl v12.8H, v4.8H, #8
    and v23.16B, v1.16B, v0.16B
    eor v31.16B, v18.16B, v30.16B
    shl v13.8H, v11.8H, #4
    eor v3.16B, v21.16B, v12.16B
    ushr v9.8H, v1.8H, #12
    shl v2.8H, v19.8H, #8
    and v20.16B, v31.16B, v0.16B
    eor v12.16B, v9.16B, v13.16B
    ushr v17.8H, v19.8H, #4
    and v31.16B, v10.16B, v0.16B
    eor v9.16B, v28.16B, v2.16B
    and v13.16B, v17.16B, v0.16B
    and v15.16B, v12.16B, v0.16B
    and v10.16B, v9.16B, v0.16B
    and v3.16B, v3.16B, v0.16B
    // Accumulate four independent unsigned maxima.
    umax v7.8h, v7.8h, v6.8h
    umax v7.8h, v7.8h, v23.8h
    umax v22.8h, v22.8h, v20.8h
    umax v22.8h, v22.8h, v31.8h
    umax v24.8h, v24.8h, v13.8h
    umax v24.8h, v24.8h, v15.8h
    umax v25.8h, v25.8h, v10.8h
    umax v25.8h, v25.8h, v3.8h
    trn1 v21.8H, v6.8H, v20.8H
    trn1 v2.8H, v23.8H, v15.8H
    trn1 v4.8H, v3.8H, v31.8H
    trn1 v14.8H, v10.8H, v13.8H
    trn2 v9.8H, v10.8H, v13.8H
    trn2 v26.8H, v3.8H, v31.8H
    trn2 v28.4S, v2.4S, v14.4S
    trn2 v17.4S, v21.4S, v4.4S
    trn1 v19.4S, v2.4S, v14.4S
    trn2 v30.8H, v6.8H, v20.8H
    trn2 v20.2D, v28.2D, v17.2D
    trn2 v5.8H, v23.8H, v15.8H
    trn1 v27.4S, v30.4S, v26.4S
    umov x9, v20.d[1]
    trn2 v10.4S, v30.4S, v26.4S
    trn1 v14.2D, v28.2D, v17.2D
    trn2 v28.4S, v5.4S, v9.4S
    trn1 v30.4S, v21.4S, v4.4S
    trn1 v18.4S, v5.4S, v9.4S
    str x9, [x0, #528]
    umov x9, v14.d[1]
    trn2 v31.2D, v28.2D, v10.2D
    trn1 v3.2D, v28.2D, v10.2D
    trn1 v23.2D, v19.2D, v30.2D
    trn2 v4.2D, v19.2D, v30.2D
    str d14, [x0, #648]
    str x9, [x0, #624]
    trn1 v17.2D, v18.2D, v27.2D
    umov x9, v23.d[1]
    str d23, [x0, #696]
    str d4, [x0, #456]
    trn2 v23.2D, v18.2D, v27.2D
    str d17, [x0, #744]
    str x9, [x0, #672]
    umov x9, v4.d[1]
    str d31, [x0, #480]
    str d23, [x0, #384]
    str x9, [x0, #432]
    umov x9, v23.d[1]
    str d3, [x0, #576]
    str x9, [x0, #408]
    umov x9, v17.d[1]
    str x9, [x0, #720]
    umov x9, v3.d[1]
    str d20, [x0, #552]
    str x9, [x0, #600]
    umov x9, v31.d[1]
    str x9, [x0, #504]
    // canonical blocks 32..47
    ld1 {v14.8H, v15.8H, v16.8H}, [x1], #48
    ld1 {v18.8H, v19.8H, v20.8H}, [x1], #48
    trn2 v9.2D, v16.2D, v20.2D
    trn1 v4.2D, v16.2D, v20.2D
    trn2 v30.2D, v14.2D, v18.2D
    trn1 v11.2D, v15.2D, v19.2D
    trn2 v12.2D, v15.2D, v19.2D
    trn1 v23.2D, v14.2D, v18.2D
    trn1 v31.4S, v30.4S, v4.4S
    trn2 v5.4S, v11.4S, v9.4S
    trn2 v15.4S, v30.4S, v4.4S
    trn1 v29.4S, v23.4S, v12.4S
    trn2 v14.4S, v23.4S, v12.4S
    trn2 v4.8H, v31.8H, v5.8H
    trn1 v27.4S, v11.4S, v9.4S
    trn2 v11.8H, v29.8H, v15.8H
    trn1 v31.8H, v31.8H, v5.8H
    ushr v10.8H, v4.8H, #4
    trn2 v26.8H, v14.8H, v27.8H
    ushr v28.8H, v11.8H, #8
    ushr v21.8H, v31.8H, #8
    trn1 v1.8H, v29.8H, v15.8H
    ushr v18.8H, v26.8H, #12
    and v6.16B, v26.16B, v0.16B
    trn1 v19.8H, v14.8H, v27.8H
    shl v30.8H, v31.8H, #4
    shl v12.8H, v4.8H, #8
    and v23.16B, v1.16B, v0.16B
    eor v31.16B, v18.16B, v30.16B
    shl v13.8H, v11.8H, #4
    eor v3.16B, v21.16B, v12.16B
    ushr v9.8H, v1.8H, #12
    shl v2.8H, v19.8H, #8
    and v20.16B, v31.16B, v0.16B
    eor v12.16B, v9.16B, v13.16B
    ushr v17.8H, v19.8H, #4
    and v31.16B, v10.16B, v0.16B
    eor v9.16B, v28.16B, v2.16B
    and v13.16B, v17.16B, v0.16B
    and v15.16B, v12.16B, v0.16B
    and v10.16B, v9.16B, v0.16B
    and v3.16B, v3.16B, v0.16B
    // Accumulate four independent unsigned maxima.
    umax v7.8h, v7.8h, v6.8h
    umax v7.8h, v7.8h, v23.8h
    umax v22.8h, v22.8h, v20.8h
    umax v22.8h, v22.8h, v31.8h
    umax v24.8h, v24.8h, v13.8h
    umax v24.8h, v24.8h, v15.8h
    umax v25.8h, v25.8h, v10.8h
    umax v25.8h, v25.8h, v3.8h
    trn1 v21.8H, v6.8H, v20.8H
    trn1 v2.8H, v23.8H, v15.8H
    trn1 v4.8H, v3.8H, v31.8H
    trn1 v14.8H, v10.8H, v13.8H
    trn2 v9.8H, v10.8H, v13.8H
    trn2 v26.8H, v3.8H, v31.8H
    trn2 v28.4S, v2.4S, v14.4S
    trn2 v17.4S, v21.4S, v4.4S
    trn1 v19.4S, v2.4S, v14.4S
    trn2 v30.8H, v6.8H, v20.8H
    trn2 v20.2D, v28.2D, v17.2D
    trn2 v5.8H, v23.8H, v15.8H
    trn1 v27.4S, v30.4S, v26.4S
    umov x9, v20.d[1]
    trn2 v10.4S, v30.4S, v26.4S
    trn1 v14.2D, v28.2D, v17.2D
    trn2 v28.4S, v5.4S, v9.4S
    trn1 v30.4S, v21.4S, v4.4S
    trn1 v18.4S, v5.4S, v9.4S
    str x9, [x0, #440]
    umov x9, v14.d[1]
    trn2 v31.2D, v28.2D, v10.2D
    trn1 v3.2D, v28.2D, v10.2D
    trn1 v23.2D, v19.2D, v30.2D
    trn2 v4.2D, v19.2D, v30.2D
    str d14, [x0, #224]
    str x9, [x0, #248]
    trn1 v17.2D, v18.2D, v27.2D
    umov x9, v23.d[1]
    str d23, [x0, #128]
    str d4, [x0, #320]
    trn2 v23.2D, v18.2D, v27.2D
    str d17, [x0, #176]
    str x9, [x0, #152]
    umov x9, v4.d[1]
    str d31, [x0, #464]
    str d23, [x0, #368]
    str x9, [x0, #344]
    umov x9, v23.d[1]
    str d3, [x0, #272]
    str x9, [x0, #392]
    umov x9, v17.d[1]
    str x9, [x0, #200]
    umov x9, v3.d[1]
    str d20, [x0, #416]
    str x9, [x0, #296]
    umov x9, v31.d[1]
    str x9, [x0, #488]
    // canonical blocks 48..63
    ld1 {v14.8H, v15.8H, v16.8H}, [x1], #48
    ld1 {v18.8H, v19.8H, v20.8H}, [x1], #48
    trn2 v9.2D, v16.2D, v20.2D
    trn1 v4.2D, v16.2D, v20.2D
    trn2 v30.2D, v14.2D, v18.2D
    trn1 v11.2D, v15.2D, v19.2D
    trn2 v12.2D, v15.2D, v19.2D
    trn1 v23.2D, v14.2D, v18.2D
    trn1 v31.4S, v30.4S, v4.4S
    trn2 v5.4S, v11.4S, v9.4S
    trn2 v15.4S, v30.4S, v4.4S
    trn1 v29.4S, v23.4S, v12.4S
    trn2 v14.4S, v23.4S, v12.4S
    trn2 v4.8H, v31.8H, v5.8H
    trn1 v27.4S, v11.4S, v9.4S
    trn2 v11.8H, v29.8H, v15.8H
    trn1 v31.8H, v31.8H, v5.8H
    ushr v10.8H, v4.8H, #4
    trn2 v26.8H, v14.8H, v27.8H
    ushr v28.8H, v11.8H, #8
    ushr v21.8H, v31.8H, #8
    trn1 v1.8H, v29.8H, v15.8H
    ushr v18.8H, v26.8H, #12
    and v6.16B, v26.16B, v0.16B
    trn1 v19.8H, v14.8H, v27.8H
    shl v30.8H, v31.8H, #4
    shl v12.8H, v4.8H, #8
    and v23.16B, v1.16B, v0.16B
    eor v31.16B, v18.16B, v30.16B
    shl v13.8H, v11.8H, #4
    eor v3.16B, v21.16B, v12.16B
    ushr v9.8H, v1.8H, #12
    shl v2.8H, v19.8H, #8
    and v20.16B, v31.16B, v0.16B
    eor v12.16B, v9.16B, v13.16B
    ushr v17.8H, v19.8H, #4
    and v31.16B, v10.16B, v0.16B
    eor v9.16B, v28.16B, v2.16B
    and v13.16B, v17.16B, v0.16B
    and v15.16B, v12.16B, v0.16B
    and v10.16B, v9.16B, v0.16B
    and v3.16B, v3.16B, v0.16B
    // Accumulate four independent unsigned maxima.
    umax v7.8h, v7.8h, v6.8h
    umax v7.8h, v7.8h, v23.8h
    umax v22.8h, v22.8h, v20.8h
    umax v22.8h, v22.8h, v31.8h
    umax v24.8h, v24.8h, v13.8h
    umax v24.8h, v24.8h, v15.8h
    umax v25.8h, v25.8h, v10.8h
    umax v25.8h, v25.8h, v3.8h
    trn1 v21.8H, v6.8H, v20.8H
    trn1 v2.8H, v23.8H, v15.8H
    trn1 v4.8H, v3.8H, v31.8H
    trn1 v14.8H, v10.8H, v13.8H
    trn2 v9.8H, v10.8H, v13.8H
    trn2 v26.8H, v3.8H, v31.8H
    trn2 v28.4S, v2.4S, v14.4S
    trn2 v17.4S, v21.4S, v4.4S
    trn1 v19.4S, v2.4S, v14.4S
    trn2 v30.8H, v6.8H, v20.8H
    trn2 v20.2D, v28.2D, v17.2D
    trn2 v5.8H, v23.8H, v15.8H
    trn1 v27.4S, v30.4S, v26.4S
    umov x9, v20.d[1]
    trn2 v10.4S, v30.4S, v26.4S
    trn1 v14.2D, v28.2D, v17.2D
    trn2 v28.4S, v5.4S, v9.4S
    trn1 v30.4S, v21.4S, v4.4S
    trn1 v18.4S, v5.4S, v9.4S
    str x9, [x0, #584]
    umov x9, v14.d[1]
    trn2 v31.2D, v28.2D, v10.2D
    trn1 v3.2D, v28.2D, v10.2D
    trn1 v23.2D, v19.2D, v30.2D
    trn2 v4.2D, v19.2D, v30.2D
    str d14, [x0, #32]
    str x9, [x0, #56]
    trn1 v17.2D, v18.2D, v27.2D
    umov x9, v23.d[1]
    str d23, [x0, #704]
    str d4, [x0, #608]
    trn2 v23.2D, v18.2D, v27.2D
    str d17, [x0, #752]
    str x9, [x0, #728]
    umov x9, v4.d[1]
    str d31, [x0, #536]
    str d23, [x0, #656]
    str x9, [x0, #632]
    umov x9, v23.d[1]
    str d3, [x0, #80]
    str x9, [x0, #680]
    umov x9, v17.d[1]
    str x9, [x0, #8]
    umov x9, v3.d[1]
    str d20, [x0, #560]
    str x9, [x0, #104]
    umov x9, v31.d[1]
    str x9, [x0, #512]
    // canonical blocks 64..79
    ld1 {v14.8H, v15.8H, v16.8H}, [x1], #48
    ld1 {v18.8H, v19.8H, v20.8H}, [x1], #48
    trn2 v9.2D, v16.2D, v20.2D
    trn1 v4.2D, v16.2D, v20.2D
    trn2 v30.2D, v14.2D, v18.2D
    trn1 v11.2D, v15.2D, v19.2D
    trn2 v12.2D, v15.2D, v19.2D
    trn1 v23.2D, v14.2D, v18.2D
    trn1 v31.4S, v30.4S, v4.4S
    trn2 v5.4S, v11.4S, v9.4S
    trn2 v15.4S, v30.4S, v4.4S
    trn1 v29.4S, v23.4S, v12.4S
    trn2 v14.4S, v23.4S, v12.4S
    trn2 v4.8H, v31.8H, v5.8H
    trn1 v27.4S, v11.4S, v9.4S
    trn2 v11.8H, v29.8H, v15.8H
    trn1 v31.8H, v31.8H, v5.8H
    ushr v10.8H, v4.8H, #4
    trn2 v26.8H, v14.8H, v27.8H
    ushr v28.8H, v11.8H, #8
    ushr v21.8H, v31.8H, #8
    trn1 v1.8H, v29.8H, v15.8H
    ushr v18.8H, v26.8H, #12
    and v6.16B, v26.16B, v0.16B
    trn1 v19.8H, v14.8H, v27.8H
    shl v30.8H, v31.8H, #4
    shl v12.8H, v4.8H, #8
    and v23.16B, v1.16B, v0.16B
    eor v31.16B, v18.16B, v30.16B
    shl v13.8H, v11.8H, #4
    eor v3.16B, v21.16B, v12.16B
    ushr v9.8H, v1.8H, #12
    shl v2.8H, v19.8H, #8
    and v20.16B, v31.16B, v0.16B
    eor v12.16B, v9.16B, v13.16B
    ushr v17.8H, v19.8H, #4
    and v31.16B, v10.16B, v0.16B
    eor v9.16B, v28.16B, v2.16B
    and v13.16B, v17.16B, v0.16B
    and v15.16B, v12.16B, v0.16B
    and v10.16B, v9.16B, v0.16B
    and v3.16B, v3.16B, v0.16B
    // Accumulate four independent unsigned maxima.
    umax v7.8h, v7.8h, v6.8h
    umax v7.8h, v7.8h, v23.8h
    umax v22.8h, v22.8h, v20.8h
    umax v22.8h, v22.8h, v31.8h
    umax v24.8h, v24.8h, v13.8h
    umax v24.8h, v24.8h, v15.8h
    umax v25.8h, v25.8h, v10.8h
    umax v25.8h, v25.8h, v3.8h
    trn1 v21.8H, v6.8H, v20.8H
    trn1 v2.8H, v23.8H, v15.8H
    trn1 v4.8H, v3.8H, v31.8H
    trn1 v14.8H, v10.8H, v13.8H
    trn2 v9.8H, v10.8H, v13.8H
    trn2 v26.8H, v3.8H, v31.8H
    trn2 v28.4S, v2.4S, v14.4S
    trn2 v17.4S, v21.4S, v4.4S
    trn1 v19.4S, v2.4S, v14.4S
    trn2 v30.8H, v6.8H, v20.8H
    trn2 v20.2D, v28.2D, v17.2D
    trn2 v5.8H, v23.8H, v15.8H
    trn1 v27.4S, v30.4S, v26.4S
    umov x9, v20.d[1]
    trn2 v10.4S, v30.4S, v26.4S
    trn1 v14.2D, v28.2D, v17.2D
    trn2 v28.4S, v5.4S, v9.4S
    trn1 v30.4S, v21.4S, v4.4S
    trn1 v18.4S, v5.4S, v9.4S
    str x9, [x0, #448]
    umov x9, v14.d[1]
    trn2 v31.2D, v28.2D, v10.2D
    trn1 v3.2D, v28.2D, v10.2D
    trn1 v23.2D, v19.2D, v30.2D
    trn2 v4.2D, v19.2D, v30.2D
    str d14, [x0, #280]
    str x9, [x0, #256]
    trn1 v17.2D, v18.2D, v27.2D
    umov x9, v23.d[1]
    str d23, [x0, #400]
    str d4, [x0, #592]
    trn2 v23.2D, v18.2D, v27.2D
    str d17, [x0, #376]
    str x9, [x0, #424]
    umov x9, v4.d[1]
    str d31, [x0, #520]
    str d23, [x0, #568]
    str x9, [x0, #616]
    umov x9, v23.d[1]
    str d3, [x0, #328]
    str x9, [x0, #544]
    umov x9, v17.d[1]
    str x9, [x0, #352]
    umov x9, v3.d[1]
    str d20, [x0, #472]
    str x9, [x0, #304]
    umov x9, v31.d[1]
    str x9, [x0, #496]
    // canonical blocks 80..95
    ld1 {v14.8H, v15.8H, v16.8H}, [x1], #48
    ld1 {v18.8H, v19.8H, v20.8H}, [x1], #48
    trn2 v9.2D, v16.2D, v20.2D
    trn1 v4.2D, v16.2D, v20.2D
    trn2 v30.2D, v14.2D, v18.2D
    trn1 v11.2D, v15.2D, v19.2D
    trn2 v12.2D, v15.2D, v19.2D
    trn1 v23.2D, v14.2D, v18.2D
    trn1 v31.4S, v30.4S, v4.4S
    trn2 v5.4S, v11.4S, v9.4S
    trn2 v15.4S, v30.4S, v4.4S
    trn1 v29.4S, v23.4S, v12.4S
    trn2 v14.4S, v23.4S, v12.4S
    trn2 v4.8H, v31.8H, v5.8H
    trn1 v27.4S, v11.4S, v9.4S
    trn2 v11.8H, v29.8H, v15.8H
    trn1 v31.8H, v31.8H, v5.8H
    ushr v10.8H, v4.8H, #4
    trn2 v26.8H, v14.8H, v27.8H
    ushr v28.8H, v11.8H, #8
    ushr v21.8H, v31.8H, #8
    trn1 v1.8H, v29.8H, v15.8H
    ushr v18.8H, v26.8H, #12
    and v6.16B, v26.16B, v0.16B
    trn1 v19.8H, v14.8H, v27.8H
    shl v30.8H, v31.8H, #4
    shl v12.8H, v4.8H, #8
    and v23.16B, v1.16B, v0.16B
    eor v31.16B, v18.16B, v30.16B
    shl v13.8H, v11.8H, #4
    eor v3.16B, v21.16B, v12.16B
    ushr v9.8H, v1.8H, #12
    shl v2.8H, v19.8H, #8
    and v20.16B, v31.16B, v0.16B
    eor v12.16B, v9.16B, v13.16B
    ushr v17.8H, v19.8H, #4
    and v31.16B, v10.16B, v0.16B
    eor v9.16B, v28.16B, v2.16B
    and v13.16B, v17.16B, v0.16B
    and v15.16B, v12.16B, v0.16B
    and v10.16B, v9.16B, v0.16B
    and v3.16B, v3.16B, v0.16B
    // Accumulate four independent unsigned maxima.
    umax v7.8h, v7.8h, v6.8h
    umax v7.8h, v7.8h, v23.8h
    umax v22.8h, v22.8h, v20.8h
    umax v22.8h, v22.8h, v31.8h
    umax v24.8h, v24.8h, v13.8h
    umax v24.8h, v24.8h, v15.8h
    umax v25.8h, v25.8h, v10.8h
    umax v25.8h, v25.8h, v3.8h
    trn1 v21.8H, v6.8H, v20.8H
    trn1 v2.8H, v23.8H, v15.8H
    trn1 v4.8H, v3.8H, v31.8H
    trn1 v14.8H, v10.8H, v13.8H
    trn2 v9.8H, v10.8H, v13.8H
    trn2 v26.8H, v3.8H, v31.8H
    trn2 v28.4S, v2.4S, v14.4S
    trn2 v17.4S, v21.4S, v4.4S
    trn1 v19.4S, v2.4S, v14.4S
    trn2 v30.8H, v6.8H, v20.8H
    trn2 v20.2D, v28.2D, v17.2D
    trn2 v5.8H, v23.8H, v15.8H
    trn1 v27.4S, v30.4S, v26.4S
    umov x9, v20.d[1]
    trn2 v10.4S, v30.4S, v26.4S
    trn1 v14.2D, v28.2D, v17.2D
    trn2 v28.4S, v5.4S, v9.4S
    trn1 v30.4S, v21.4S, v4.4S
    trn1 v18.4S, v5.4S, v9.4S
    str x9, [x0, #64]
    umov x9, v14.d[1]
    trn2 v31.2D, v28.2D, v10.2D
    trn1 v3.2D, v28.2D, v10.2D
    trn1 v23.2D, v19.2D, v30.2D
    trn2 v4.2D, v19.2D, v30.2D
    str d14, [x0, #664]
    str x9, [x0, #640]
    trn1 v17.2D, v18.2D, v27.2D
    umov x9, v23.d[1]
    str d23, [x0, #16]
    str d4, [x0, #208]
    trn2 v23.2D, v18.2D, v27.2D
    str d17, [x0, #760]
    str x9, [x0, #40]
    umov x9, v4.d[1]
    str d31, [x0, #136]
    str d23, [x0, #184]
    str x9, [x0, #232]
    umov x9, v23.d[1]
    str d3, [x0, #712]
    str x9, [x0, #160]
    umov x9, v17.d[1]
    str x9, [x0, #736]
    umov x9, v3.d[1]
    str d20, [x0, #88]
    str x9, [x0, #688]
    umov x9, v31.d[1]
    str x9, [x0, #112]
    // canonical blocks 96..111
    ld1 {v14.8H, v15.8H, v16.8H}, [x1], #48
    ld1 {v18.8H, v19.8H, v20.8H}, [x1], #48
    trn2 v9.2D, v16.2D, v20.2D
    trn1 v4.2D, v16.2D, v20.2D
    trn2 v30.2D, v14.2D, v18.2D
    trn1 v11.2D, v15.2D, v19.2D
    trn2 v12.2D, v15.2D, v19.2D
    trn1 v23.2D, v14.2D, v18.2D
    trn1 v31.4S, v30.4S, v4.4S
    trn2 v5.4S, v11.4S, v9.4S
    trn2 v15.4S, v30.4S, v4.4S
    trn1 v29.4S, v23.4S, v12.4S
    trn2 v14.4S, v23.4S, v12.4S
    trn2 v4.8H, v31.8H, v5.8H
    trn1 v27.4S, v11.4S, v9.4S
    trn2 v11.8H, v29.8H, v15.8H
    trn1 v31.8H, v31.8H, v5.8H
    ushr v10.8H, v4.8H, #4
    trn2 v26.8H, v14.8H, v27.8H
    ushr v28.8H, v11.8H, #8
    ushr v21.8H, v31.8H, #8
    trn1 v1.8H, v29.8H, v15.8H
    ushr v18.8H, v26.8H, #12
    and v6.16B, v26.16B, v0.16B
    trn1 v19.8H, v14.8H, v27.8H
    shl v30.8H, v31.8H, #4
    shl v12.8H, v4.8H, #8
    and v23.16B, v1.16B, v0.16B
    eor v31.16B, v18.16B, v30.16B
    shl v13.8H, v11.8H, #4
    eor v3.16B, v21.16B, v12.16B
    ushr v9.8H, v1.8H, #12
    shl v2.8H, v19.8H, #8
    and v20.16B, v31.16B, v0.16B
    eor v12.16B, v9.16B, v13.16B
    ushr v17.8H, v19.8H, #4
    and v31.16B, v10.16B, v0.16B
    eor v9.16B, v28.16B, v2.16B
    and v13.16B, v17.16B, v0.16B
    and v15.16B, v12.16B, v0.16B
    and v10.16B, v9.16B, v0.16B
    and v3.16B, v3.16B, v0.16B
    // Accumulate four independent unsigned maxima.
    umax v7.8h, v7.8h, v6.8h
    umax v7.8h, v7.8h, v23.8h
    umax v22.8h, v22.8h, v20.8h
    umax v22.8h, v22.8h, v31.8h
    umax v24.8h, v24.8h, v13.8h
    umax v24.8h, v24.8h, v15.8h
    umax v25.8h, v25.8h, v10.8h
    umax v25.8h, v25.8h, v3.8h
    trn1 v21.8H, v6.8H, v20.8H
    trn1 v2.8H, v23.8H, v15.8H
    trn1 v4.8H, v3.8H, v31.8H
    trn1 v14.8H, v10.8H, v13.8H
    trn2 v9.8H, v10.8H, v13.8H
    trn2 v26.8H, v3.8H, v31.8H
    trn2 v28.4S, v2.4S, v14.4S
    trn2 v17.4S, v21.4S, v4.4S
    trn1 v19.4S, v2.4S, v14.4S
    trn2 v30.8H, v6.8H, v20.8H
    trn2 v20.2D, v28.2D, v17.2D
    trn2 v5.8H, v23.8H, v15.8H
    trn1 v27.4S, v30.4S, v26.4S
    umov x9, v20.d[1]
    trn2 v10.4S, v30.4S, v26.4S
    trn1 v14.2D, v28.2D, v17.2D
    trn2 v28.4S, v5.4S, v9.4S
    trn1 v30.4S, v21.4S, v4.4S
    trn1 v18.4S, v5.4S, v9.4S
    str x9, [x0, #896]
    umov x9, v14.d[1]
    trn2 v31.2D, v28.2D, v10.2D
    trn1 v3.2D, v28.2D, v10.2D
    trn1 v23.2D, v19.2D, v30.2D
    trn2 v4.2D, v19.2D, v30.2D
    str d14, [x0, #1232]
    str x9, [x0, #1256]
    trn1 v17.2D, v18.2D, v27.2D
    umov x9, v23.d[1]
    str d23, [x0, #1136]
    str d4, [x0, #1040]
    trn2 v23.2D, v18.2D, v27.2D
    str d17, [x0, #1112]
    str x9, [x0, #1160]
    umov x9, v4.d[1]
    str d31, [x0, #968]
    str d23, [x0, #1016]
    str x9, [x0, #1064]
    umov x9, v23.d[1]
    str d3, [x0, #1208]
    str x9, [x0, #992]
    umov x9, v17.d[1]
    str x9, [x0, #1088]
    umov x9, v3.d[1]
    str d20, [x0, #920]
    str x9, [x0, #1184]
    umov x9, v31.d[1]
    str x9, [x0, #944]
    // canonical blocks 112..127
    ld1 {v14.8H, v15.8H, v16.8H}, [x1], #48
    ld1 {v18.8H, v19.8H, v20.8H}, [x1], #48
    trn2 v9.2D, v16.2D, v20.2D
    trn1 v4.2D, v16.2D, v20.2D
    trn2 v30.2D, v14.2D, v18.2D
    trn1 v11.2D, v15.2D, v19.2D
    trn2 v12.2D, v15.2D, v19.2D
    trn1 v23.2D, v14.2D, v18.2D
    trn1 v31.4S, v30.4S, v4.4S
    trn2 v5.4S, v11.4S, v9.4S
    trn2 v15.4S, v30.4S, v4.4S
    trn1 v29.4S, v23.4S, v12.4S
    trn2 v14.4S, v23.4S, v12.4S
    trn2 v4.8H, v31.8H, v5.8H
    trn1 v27.4S, v11.4S, v9.4S
    trn2 v11.8H, v29.8H, v15.8H
    trn1 v31.8H, v31.8H, v5.8H
    ushr v10.8H, v4.8H, #4
    trn2 v26.8H, v14.8H, v27.8H
    ushr v28.8H, v11.8H, #8
    ushr v21.8H, v31.8H, #8
    trn1 v1.8H, v29.8H, v15.8H
    ushr v18.8H, v26.8H, #12
    and v6.16B, v26.16B, v0.16B
    trn1 v19.8H, v14.8H, v27.8H
    shl v30.8H, v31.8H, #4
    shl v12.8H, v4.8H, #8
    and v23.16B, v1.16B, v0.16B
    eor v31.16B, v18.16B, v30.16B
    shl v13.8H, v11.8H, #4
    eor v3.16B, v21.16B, v12.16B
    ushr v9.8H, v1.8H, #12
    shl v2.8H, v19.8H, #8
    and v20.16B, v31.16B, v0.16B
    eor v12.16B, v9.16B, v13.16B
    ushr v17.8H, v19.8H, #4
    and v31.16B, v10.16B, v0.16B
    eor v9.16B, v28.16B, v2.16B
    and v13.16B, v17.16B, v0.16B
    and v15.16B, v12.16B, v0.16B
    and v10.16B, v9.16B, v0.16B
    and v3.16B, v3.16B, v0.16B
    // Accumulate four independent unsigned maxima.
    umax v7.8h, v7.8h, v6.8h
    umax v7.8h, v7.8h, v23.8h
    umax v22.8h, v22.8h, v20.8h
    umax v22.8h, v22.8h, v31.8h
    umax v24.8h, v24.8h, v13.8h
    umax v24.8h, v24.8h, v15.8h
    umax v25.8h, v25.8h, v10.8h
    umax v25.8h, v25.8h, v3.8h
    trn1 v21.8H, v6.8H, v20.8H
    trn1 v2.8H, v23.8H, v15.8H
    trn1 v4.8H, v3.8H, v31.8H
    trn1 v14.8H, v10.8H, v13.8H
    trn2 v9.8H, v10.8H, v13.8H
    trn2 v26.8H, v3.8H, v31.8H
    trn2 v28.4S, v2.4S, v14.4S
    trn2 v17.4S, v21.4S, v4.4S
    trn1 v19.4S, v2.4S, v14.4S
    trn2 v30.8H, v6.8H, v20.8H
    trn2 v20.2D, v28.2D, v17.2D
    trn2 v5.8H, v23.8H, v15.8H
    trn1 v27.4S, v30.4S, v26.4S
    umov x9, v20.d[1]
    trn2 v10.4S, v30.4S, v26.4S
    trn1 v14.2D, v28.2D, v17.2D
    trn2 v28.4S, v5.4S, v9.4S
    trn1 v30.4S, v21.4S, v4.4S
    trn1 v18.4S, v5.4S, v9.4S
    str x9, [x0, #1472]
    umov x9, v14.d[1]
    trn2 v31.2D, v28.2D, v10.2D
    trn1 v3.2D, v28.2D, v10.2D
    trn1 v23.2D, v19.2D, v30.2D
    trn2 v4.2D, v19.2D, v30.2D
    str d14, [x0, #1304]
    str x9, [x0, #1280]
    trn1 v17.2D, v18.2D, v27.2D
    umov x9, v23.d[1]
    str d23, [x0, #1424]
    str d4, [x0, #848]
    trn2 v23.2D, v18.2D, v27.2D
    str d17, [x0, #1400]
    str x9, [x0, #1448]
    umov x9, v4.d[1]
    str d31, [x0, #776]
    str d23, [x0, #824]
    str x9, [x0, #872]
    umov x9, v23.d[1]
    str d3, [x0, #1352]
    str x9, [x0, #800]
    umov x9, v17.d[1]
    str x9, [x0, #1376]
    umov x9, v3.d[1]
    str d20, [x0, #1496]
    str x9, [x0, #1328]
    umov x9, v31.d[1]
    str x9, [x0, #1520]
    // canonical blocks 128..143
    ld1 {v14.8H, v15.8H, v16.8H}, [x1], #48
    ld1 {v18.8H, v19.8H, v20.8H}, [x1], #48
    trn2 v9.2D, v16.2D, v20.2D
    trn1 v4.2D, v16.2D, v20.2D
    trn2 v30.2D, v14.2D, v18.2D
    trn1 v11.2D, v15.2D, v19.2D
    trn2 v12.2D, v15.2D, v19.2D
    trn1 v23.2D, v14.2D, v18.2D
    trn1 v31.4S, v30.4S, v4.4S
    trn2 v5.4S, v11.4S, v9.4S
    trn2 v15.4S, v30.4S, v4.4S
    trn1 v29.4S, v23.4S, v12.4S
    trn2 v14.4S, v23.4S, v12.4S
    trn2 v4.8H, v31.8H, v5.8H
    trn1 v27.4S, v11.4S, v9.4S
    trn2 v11.8H, v29.8H, v15.8H
    trn1 v31.8H, v31.8H, v5.8H
    ushr v10.8H, v4.8H, #4
    trn2 v26.8H, v14.8H, v27.8H
    ushr v28.8H, v11.8H, #8
    ushr v21.8H, v31.8H, #8
    trn1 v1.8H, v29.8H, v15.8H
    ushr v18.8H, v26.8H, #12
    and v6.16B, v26.16B, v0.16B
    trn1 v19.8H, v14.8H, v27.8H
    shl v30.8H, v31.8H, #4
    shl v12.8H, v4.8H, #8
    and v23.16B, v1.16B, v0.16B
    eor v31.16B, v18.16B, v30.16B
    shl v13.8H, v11.8H, #4
    eor v3.16B, v21.16B, v12.16B
    ushr v9.8H, v1.8H, #12
    shl v2.8H, v19.8H, #8
    and v20.16B, v31.16B, v0.16B
    eor v12.16B, v9.16B, v13.16B
    ushr v17.8H, v19.8H, #4
    and v31.16B, v10.16B, v0.16B
    eor v9.16B, v28.16B, v2.16B
    and v13.16B, v17.16B, v0.16B
    and v15.16B, v12.16B, v0.16B
    and v10.16B, v9.16B, v0.16B
    and v3.16B, v3.16B, v0.16B
    // Accumulate four independent unsigned maxima.
    umax v7.8h, v7.8h, v6.8h
    umax v7.8h, v7.8h, v23.8h
    umax v22.8h, v22.8h, v20.8h
    umax v22.8h, v22.8h, v31.8h
    umax v24.8h, v24.8h, v13.8h
    umax v24.8h, v24.8h, v15.8h
    umax v25.8h, v25.8h, v10.8h
    umax v25.8h, v25.8h, v3.8h
    trn1 v21.8H, v6.8H, v20.8H
    trn1 v2.8H, v23.8H, v15.8H
    trn1 v4.8H, v3.8H, v31.8H
    trn1 v14.8H, v10.8H, v13.8H
    trn2 v9.8H, v10.8H, v13.8H
    trn2 v26.8H, v3.8H, v31.8H
    trn2 v28.4S, v2.4S, v14.4S
    trn2 v17.4S, v21.4S, v4.4S
    trn1 v19.4S, v2.4S, v14.4S
    trn2 v30.8H, v6.8H, v20.8H
    trn2 v20.2D, v28.2D, v17.2D
    trn2 v5.8H, v23.8H, v15.8H
    trn1 v27.4S, v30.4S, v26.4S
    umov x9, v20.d[1]
    trn2 v10.4S, v30.4S, v26.4S
    trn1 v14.2D, v28.2D, v17.2D
    trn2 v28.4S, v5.4S, v9.4S
    trn1 v30.4S, v21.4S, v4.4S
    trn1 v18.4S, v5.4S, v9.4S
    str x9, [x0, #1168]
    umov x9, v14.d[1]
    trn2 v31.2D, v28.2D, v10.2D
    trn1 v3.2D, v28.2D, v10.2D
    trn1 v23.2D, v19.2D, v30.2D
    trn2 v4.2D, v19.2D, v30.2D
    str d14, [x0, #1288]
    str x9, [x0, #1264]
    trn1 v17.2D, v18.2D, v27.2D
    umov x9, v23.d[1]
    str d23, [x0, #1336]
    str d4, [x0, #1096]
    trn2 v23.2D, v18.2D, v27.2D
    str d17, [x0, #1384]
    str x9, [x0, #1312]
    umov x9, v4.d[1]
    str d31, [x0, #1120]
    str d23, [x0, #1024]
    str x9, [x0, #1072]
    umov x9, v23.d[1]
    str d3, [x0, #1216]
    str x9, [x0, #1048]
    umov x9, v17.d[1]
    str x9, [x0, #1360]
    umov x9, v3.d[1]
    str d20, [x0, #1192]
    str x9, [x0, #1240]
    umov x9, v31.d[1]
    str x9, [x0, #1144]
    // canonical blocks 144..159
    ld1 {v14.8H, v15.8H, v16.8H}, [x1], #48
    ld1 {v18.8H, v19.8H, v20.8H}, [x1], #48
    trn2 v9.2D, v16.2D, v20.2D
    trn1 v4.2D, v16.2D, v20.2D
    trn2 v30.2D, v14.2D, v18.2D
    trn1 v11.2D, v15.2D, v19.2D
    trn2 v12.2D, v15.2D, v19.2D
    trn1 v23.2D, v14.2D, v18.2D
    trn1 v31.4S, v30.4S, v4.4S
    trn2 v5.4S, v11.4S, v9.4S
    trn2 v15.4S, v30.4S, v4.4S
    trn1 v29.4S, v23.4S, v12.4S
    trn2 v14.4S, v23.4S, v12.4S
    trn2 v4.8H, v31.8H, v5.8H
    trn1 v27.4S, v11.4S, v9.4S
    trn2 v11.8H, v29.8H, v15.8H
    trn1 v31.8H, v31.8H, v5.8H
    ushr v10.8H, v4.8H, #4
    trn2 v26.8H, v14.8H, v27.8H
    ushr v28.8H, v11.8H, #8
    ushr v21.8H, v31.8H, #8
    trn1 v1.8H, v29.8H, v15.8H
    ushr v18.8H, v26.8H, #12
    and v6.16B, v26.16B, v0.16B
    trn1 v19.8H, v14.8H, v27.8H
    shl v30.8H, v31.8H, #4
    shl v12.8H, v4.8H, #8
    and v23.16B, v1.16B, v0.16B
    eor v31.16B, v18.16B, v30.16B
    shl v13.8H, v11.8H, #4
    eor v3.16B, v21.16B, v12.16B
    ushr v9.8H, v1.8H, #12
    shl v2.8H, v19.8H, #8
    and v20.16B, v31.16B, v0.16B
    eor v12.16B, v9.16B, v13.16B
    ushr v17.8H, v19.8H, #4
    and v31.16B, v10.16B, v0.16B
    eor v9.16B, v28.16B, v2.16B
    and v13.16B, v17.16B, v0.16B
    and v15.16B, v12.16B, v0.16B
    and v10.16B, v9.16B, v0.16B
    and v3.16B, v3.16B, v0.16B
    // Accumulate four independent unsigned maxima.
    umax v7.8h, v7.8h, v6.8h
    umax v7.8h, v7.8h, v23.8h
    umax v22.8h, v22.8h, v20.8h
    umax v22.8h, v22.8h, v31.8h
    umax v24.8h, v24.8h, v13.8h
    umax v24.8h, v24.8h, v15.8h
    umax v25.8h, v25.8h, v10.8h
    umax v25.8h, v25.8h, v3.8h
    trn1 v21.8H, v6.8H, v20.8H
    trn1 v2.8H, v23.8H, v15.8H
    trn1 v4.8H, v3.8H, v31.8H
    trn1 v14.8H, v10.8H, v13.8H
    trn2 v9.8H, v10.8H, v13.8H
    trn2 v26.8H, v3.8H, v31.8H
    trn2 v28.4S, v2.4S, v14.4S
    trn2 v17.4S, v21.4S, v4.4S
    trn1 v19.4S, v2.4S, v14.4S
    trn2 v30.8H, v6.8H, v20.8H
    trn2 v20.2D, v28.2D, v17.2D
    trn2 v5.8H, v23.8H, v15.8H
    trn1 v27.4S, v30.4S, v26.4S
    umov x9, v20.d[1]
    trn2 v10.4S, v30.4S, v26.4S
    trn1 v14.2D, v28.2D, v17.2D
    trn2 v28.4S, v5.4S, v9.4S
    trn1 v30.4S, v21.4S, v4.4S
    trn1 v18.4S, v5.4S, v9.4S
    str x9, [x0, #784]
    umov x9, v14.d[1]
    trn2 v31.2D, v28.2D, v10.2D
    trn1 v3.2D, v28.2D, v10.2D
    trn1 v23.2D, v19.2D, v30.2D
    trn2 v4.2D, v19.2D, v30.2D
    str d14, [x0, #904]
    str x9, [x0, #880]
    trn1 v17.2D, v18.2D, v27.2D
    umov x9, v23.d[1]
    str d23, [x0, #952]
    str d4, [x0, #1480]
    trn2 v23.2D, v18.2D, v27.2D
    str d17, [x0, #1000]
    str x9, [x0, #928]
    umov x9, v4.d[1]
    str d31, [x0, #1504]
    str d23, [x0, #1408]
    str x9, [x0, #1456]
    umov x9, v23.d[1]
    str d3, [x0, #832]
    str x9, [x0, #1432]
    umov x9, v17.d[1]
    str x9, [x0, #976]
    umov x9, v3.d[1]
    str d20, [x0, #808]
    str x9, [x0, #856]
    umov x9, v31.d[1]
    str x9, [x0, #1528]
    // canonical blocks 160..175
    ld1 {v14.8H, v15.8H, v16.8H}, [x1], #48
    ld1 {v18.8H, v19.8H, v20.8H}, [x1], #48
    trn2 v9.2D, v16.2D, v20.2D
    trn1 v4.2D, v16.2D, v20.2D
    trn2 v30.2D, v14.2D, v18.2D
    trn1 v11.2D, v15.2D, v19.2D
    trn2 v12.2D, v15.2D, v19.2D
    trn1 v23.2D, v14.2D, v18.2D
    trn1 v31.4S, v30.4S, v4.4S
    trn2 v5.4S, v11.4S, v9.4S
    trn2 v15.4S, v30.4S, v4.4S
    trn1 v29.4S, v23.4S, v12.4S
    trn2 v14.4S, v23.4S, v12.4S
    trn2 v4.8H, v31.8H, v5.8H
    trn1 v27.4S, v11.4S, v9.4S
    trn2 v11.8H, v29.8H, v15.8H
    trn1 v31.8H, v31.8H, v5.8H
    ushr v10.8H, v4.8H, #4
    trn2 v26.8H, v14.8H, v27.8H
    ushr v28.8H, v11.8H, #8
    ushr v21.8H, v31.8H, #8
    trn1 v1.8H, v29.8H, v15.8H
    ushr v18.8H, v26.8H, #12
    and v6.16B, v26.16B, v0.16B
    trn1 v19.8H, v14.8H, v27.8H
    shl v30.8H, v31.8H, #4
    shl v12.8H, v4.8H, #8
    and v23.16B, v1.16B, v0.16B
    eor v31.16B, v18.16B, v30.16B
    shl v13.8H, v11.8H, #4
    eor v3.16B, v21.16B, v12.16B
    ushr v9.8H, v1.8H, #12
    shl v2.8H, v19.8H, #8
    and v20.16B, v31.16B, v0.16B
    eor v12.16B, v9.16B, v13.16B
    ushr v17.8H, v19.8H, #4
    and v31.16B, v10.16B, v0.16B
    eor v9.16B, v28.16B, v2.16B
    and v13.16B, v17.16B, v0.16B
    and v15.16B, v12.16B, v0.16B
    and v10.16B, v9.16B, v0.16B
    and v3.16B, v3.16B, v0.16B
    // Accumulate four independent unsigned maxima.
    umax v7.8h, v7.8h, v6.8h
    umax v7.8h, v7.8h, v23.8h
    umax v22.8h, v22.8h, v20.8h
    umax v22.8h, v22.8h, v31.8h
    umax v24.8h, v24.8h, v13.8h
    umax v24.8h, v24.8h, v15.8h
    umax v25.8h, v25.8h, v10.8h
    umax v25.8h, v25.8h, v3.8h
    trn1 v21.8H, v6.8H, v20.8H
    trn1 v2.8H, v23.8H, v15.8H
    trn1 v4.8H, v3.8H, v31.8H
    trn1 v14.8H, v10.8H, v13.8H
    trn2 v9.8H, v10.8H, v13.8H
    trn2 v26.8H, v3.8H, v31.8H
    trn2 v28.4S, v2.4S, v14.4S
    trn2 v17.4S, v21.4S, v4.4S
    trn1 v19.4S, v2.4S, v14.4S
    trn2 v30.8H, v6.8H, v20.8H
    trn2 v20.2D, v28.2D, v17.2D
    trn2 v5.8H, v23.8H, v15.8H
    trn1 v27.4S, v30.4S, v26.4S
    umov x9, v20.d[1]
    trn2 v10.4S, v30.4S, v26.4S
    trn1 v14.2D, v28.2D, v17.2D
    trn2 v28.4S, v5.4S, v9.4S
    trn1 v30.4S, v21.4S, v4.4S
    trn1 v18.4S, v5.4S, v9.4S
    str x9, [x0, #1464]
    umov x9, v14.d[1]
    trn2 v31.2D, v28.2D, v10.2D
    trn1 v3.2D, v28.2D, v10.2D
    trn1 v23.2D, v19.2D, v30.2D
    trn2 v4.2D, v19.2D, v30.2D
    str d14, [x0, #1248]
    str x9, [x0, #1272]
    trn1 v17.2D, v18.2D, v27.2D
    umov x9, v23.d[1]
    str d23, [x0, #1152]
    str d4, [x0, #1344]
    trn2 v23.2D, v18.2D, v27.2D
    str d17, [x0, #1200]
    str x9, [x0, #1176]
    umov x9, v4.d[1]
    str d31, [x0, #1488]
    str d23, [x0, #1392]
    str x9, [x0, #1368]
    umov x9, v23.d[1]
    str d3, [x0, #1296]
    str x9, [x0, #1416]
    umov x9, v17.d[1]
    str x9, [x0, #1224]
    umov x9, v3.d[1]
    str d20, [x0, #1440]
    str x9, [x0, #1320]
    umov x9, v31.d[1]
    str x9, [x0, #1512]
    // canonical blocks 176..191
    ld1 {v14.8H, v15.8H, v16.8H}, [x1], #48
    ld1 {v18.8H, v19.8H, v20.8H}, [x1], #48
    trn2 v9.2D, v16.2D, v20.2D
    trn1 v4.2D, v16.2D, v20.2D
    trn2 v30.2D, v14.2D, v18.2D
    trn1 v11.2D, v15.2D, v19.2D
    trn2 v12.2D, v15.2D, v19.2D
    trn1 v23.2D, v14.2D, v18.2D
    trn1 v31.4S, v30.4S, v4.4S
    trn2 v5.4S, v11.4S, v9.4S
    trn2 v15.4S, v30.4S, v4.4S
    trn1 v29.4S, v23.4S, v12.4S
    trn2 v14.4S, v23.4S, v12.4S
    trn2 v4.8H, v31.8H, v5.8H
    trn1 v27.4S, v11.4S, v9.4S
    trn2 v11.8H, v29.8H, v15.8H
    trn1 v31.8H, v31.8H, v5.8H
    ushr v10.8H, v4.8H, #4
    trn2 v26.8H, v14.8H, v27.8H
    ushr v28.8H, v11.8H, #8
    ushr v21.8H, v31.8H, #8
    trn1 v1.8H, v29.8H, v15.8H
    ushr v18.8H, v26.8H, #12
    and v6.16B, v26.16B, v0.16B
    trn1 v19.8H, v14.8H, v27.8H
    shl v30.8H, v31.8H, #4
    shl v12.8H, v4.8H, #8
    and v23.16B, v1.16B, v0.16B
    eor v31.16B, v18.16B, v30.16B
    shl v13.8H, v11.8H, #4
    eor v3.16B, v21.16B, v12.16B
    ushr v9.8H, v1.8H, #12
    shl v2.8H, v19.8H, #8
    and v20.16B, v31.16B, v0.16B
    eor v12.16B, v9.16B, v13.16B
    ushr v17.8H, v19.8H, #4
    and v31.16B, v10.16B, v0.16B
    eor v9.16B, v28.16B, v2.16B
    and v13.16B, v17.16B, v0.16B
    and v15.16B, v12.16B, v0.16B
    and v10.16B, v9.16B, v0.16B
    and v3.16B, v3.16B, v0.16B
    // Accumulate four independent unsigned maxima.
    umax v7.8h, v7.8h, v6.8h
    umax v7.8h, v7.8h, v23.8h
    umax v22.8h, v22.8h, v20.8h
    umax v22.8h, v22.8h, v31.8h
    umax v24.8h, v24.8h, v13.8h
    umax v24.8h, v24.8h, v15.8h
    umax v25.8h, v25.8h, v10.8h
    umax v25.8h, v25.8h, v3.8h
    trn1 v21.8H, v6.8H, v20.8H
    trn1 v2.8H, v23.8H, v15.8H
    trn1 v4.8H, v3.8H, v31.8H
    trn1 v14.8H, v10.8H, v13.8H
    trn2 v9.8H, v10.8H, v13.8H
    trn2 v26.8H, v3.8H, v31.8H
    trn2 v28.4S, v2.4S, v14.4S
    trn2 v17.4S, v21.4S, v4.4S
    trn1 v19.4S, v2.4S, v14.4S
    trn2 v30.8H, v6.8H, v20.8H
    trn2 v20.2D, v28.2D, v17.2D
    trn2 v5.8H, v23.8H, v15.8H
    trn1 v27.4S, v30.4S, v26.4S
    umov x9, v20.d[1]
    trn2 v10.4S, v30.4S, v26.4S
    trn1 v14.2D, v28.2D, v17.2D
    trn2 v28.4S, v5.4S, v9.4S
    trn1 v30.4S, v21.4S, v4.4S
    trn1 v18.4S, v5.4S, v9.4S
    str x9, [x0, #840]
    umov x9, v14.d[1]
    trn2 v31.2D, v28.2D, v10.2D
    trn1 v3.2D, v28.2D, v10.2D
    trn1 v23.2D, v19.2D, v30.2D
    trn2 v4.2D, v19.2D, v30.2D
    str d14, [x0, #1056]
    str x9, [x0, #1080]
    trn1 v17.2D, v18.2D, v27.2D
    umov x9, v23.d[1]
    str d23, [x0, #960]
    str d4, [x0, #864]
    trn2 v23.2D, v18.2D, v27.2D
    str d17, [x0, #1008]
    str x9, [x0, #984]
    umov x9, v4.d[1]
    str d31, [x0, #792]
    str d23, [x0, #912]
    str x9, [x0, #888]
    umov x9, v23.d[1]
    str d3, [x0, #1104]
    str x9, [x0, #936]
    umov x9, v17.d[1]
    str x9, [x0, #1032]
    umov x9, v3.d[1]
    str d20, [x0, #816]
    str x9, [x0, #1128]
    umov x9, v31.d[1]
    str x9, [x0, #768]
    umax v7.8h, v7.8h, v22.8h
    umax v24.8h, v24.8h, v25.8h
    umax v7.8h, v7.8h, v24.8h
    cmhs v7.8h, v7.8h, v8.8h
    umaxv h22, v7.8h
    umov w0, v22.h[0]
    cmp w0, #0
    cset w0, ne
    ldp d8, d9, [sp, #0]
    ldp d10, d11, [sp, #16]
    ldp d12, d13, [sp, #32]
    ldp d14, d15, [sp, #48]
    add sp, sp, #64
    ret

.p2align 4
module_unpack_.Lcanonical_unpack_candidate_mask:
    .hword 0x0fff, 0x0fff, 0x0fff, 0x0fff
    .hword 0x0fff, 0x0fff, 0x0fff, 0x0fff

/* END original unpack.S */

/* BEGIN original keygen_pack.S; private namespace module_keygen_pack_ */
// Production CQ pack with shared 60-instruction pack64 core.
// The layout frontend and 60-instruction pack64 semantics are unchanged.
// Generated by generate_cq_canonical_pack.py for the fixed Direct-CQ
// key-generation pipeline.
// CQ[g][c][lane] -> canonical 12-bit byte stream without CQ->GT repair.
#ifdef __APPLE__
.text
#else
.section .text.module_keygen_pack_body,"ax",%progbits
#endif
.p2align 4
.global poly_tobytes_keygen_cq
.global _poly_tobytes_keygen_cq
poly_tobytes_keygen_cq:
_poly_tobytes_keygen_cq:
    sub sp, sp, #80
    stp d8, d9, [sp, #0]
    stp d10, d11, [sp, #16]
    stp d12, d13, [sp, #32]
    stp d14, d15, [sp, #48]
    str x30, [sp, #64]
    adr x2, module_keygen_pack_.Lbpq_cq_pack_indexes
    adr x3, module_keygen_pack_.Lbpq_cq_pack_q
    ldr q0, [x3]
    // canonical blocks 0..7; CQ groups 2/3
    ldr q1, [x1, #128]
    ldr q2, [x1, #192]
    ldr q3, [x1, #144]
    ldr q4, [x1, #208]
    ldr q5, [x1, #160]
    ldr q6, [x1, #224]
    ldr q7, [x1, #176]
    ldr q8, [x1, #240]
    ldr q13, [x2, #0]
    tbl v9.16b, {v1.16b, v2.16b}, v13.16b
    tbl v10.16b, {v3.16b, v4.16b}, v13.16b
    tbl v11.16b, {v5.16b, v6.16b}, v13.16b
    tbl v12.16b, {v7.16b, v8.16b}, v13.16b
    // canonical blocks 8..15; CQ groups 0/1
    ldr q1, [x1, #0]
    ldr q2, [x1, #64]
    ldr q3, [x1, #16]
    ldr q4, [x1, #80]
    ldr q5, [x1, #32]
    ldr q6, [x1, #96]
    ldr q7, [x1, #48]
    ldr q8, [x1, #112]
    ldr q13, [x2, #16]
    tbl v26.16b, {v1.16b, v2.16b}, v13.16b
    tbl v27.16b, {v3.16b, v4.16b}, v13.16b
    tbl v28.16b, {v5.16b, v6.16b}, v13.16b
    tbl v29.16b, {v7.16b, v8.16b}, v13.16b
    uzp1 v18.8h, v9.8h, v26.8h
    uzp2 v26.8h, v9.8h, v26.8h
    mov v9.16b, v18.16b
    uzp1 v19.8h, v10.8h, v27.8h
    uzp2 v27.8h, v10.8h, v27.8h
    mov v10.16b, v19.16b
    uzp1 v20.8h, v11.8h, v28.8h
    uzp2 v28.8h, v11.8h, v28.8h
    mov v11.16b, v20.16b
    uzp1 v21.8h, v12.8h, v29.8h
    uzp2 v29.8h, v12.8h, v29.8h
    mov v12.16b, v21.16b
    bl module_keygen_pack_.Lgt_keygen_shared_pack64_core
    // canonical blocks 16..23; CQ groups 6/7
    ldr q1, [x1, #384]
    ldr q2, [x1, #448]
    ldr q3, [x1, #400]
    ldr q4, [x1, #464]
    ldr q5, [x1, #416]
    ldr q6, [x1, #480]
    ldr q7, [x1, #432]
    ldr q8, [x1, #496]
    ldr q13, [x2, #32]
    tbl v9.16b, {v1.16b, v2.16b}, v13.16b
    tbl v10.16b, {v3.16b, v4.16b}, v13.16b
    tbl v11.16b, {v5.16b, v6.16b}, v13.16b
    tbl v12.16b, {v7.16b, v8.16b}, v13.16b
    // canonical blocks 24..31; CQ groups 4/5
    ldr q1, [x1, #256]
    ldr q2, [x1, #320]
    ldr q3, [x1, #272]
    ldr q4, [x1, #336]
    ldr q5, [x1, #288]
    ldr q6, [x1, #352]
    ldr q7, [x1, #304]
    ldr q8, [x1, #368]
    ldr q13, [x2, #48]
    tbl v26.16b, {v1.16b, v2.16b}, v13.16b
    tbl v27.16b, {v3.16b, v4.16b}, v13.16b
    tbl v28.16b, {v5.16b, v6.16b}, v13.16b
    tbl v29.16b, {v7.16b, v8.16b}, v13.16b
    uzp1 v18.8h, v9.8h, v26.8h
    uzp2 v26.8h, v9.8h, v26.8h
    mov v9.16b, v18.16b
    uzp1 v19.8h, v10.8h, v27.8h
    uzp2 v27.8h, v10.8h, v27.8h
    mov v10.16b, v19.16b
    uzp1 v20.8h, v11.8h, v28.8h
    uzp2 v28.8h, v11.8h, v28.8h
    mov v11.16b, v20.16b
    uzp1 v21.8h, v12.8h, v29.8h
    uzp2 v29.8h, v12.8h, v29.8h
    mov v12.16b, v21.16b
    bl module_keygen_pack_.Lgt_keygen_shared_pack64_core
    // canonical blocks 32..39; CQ groups 20/21
    ldr q1, [x1, #1280]
    ldr q2, [x1, #1344]
    ldr q3, [x1, #1296]
    ldr q4, [x1, #1360]
    ldr q5, [x1, #1312]
    ldr q6, [x1, #1376]
    ldr q7, [x1, #1328]
    ldr q8, [x1, #1392]
    ldr q13, [x2, #64]
    tbl v9.16b, {v1.16b, v2.16b}, v13.16b
    tbl v10.16b, {v3.16b, v4.16b}, v13.16b
    tbl v11.16b, {v5.16b, v6.16b}, v13.16b
    tbl v12.16b, {v7.16b, v8.16b}, v13.16b
    // canonical blocks 40..47; CQ groups 22/23
    ldr q1, [x1, #1408]
    ldr q2, [x1, #1472]
    ldr q3, [x1, #1424]
    ldr q4, [x1, #1488]
    ldr q5, [x1, #1440]
    ldr q6, [x1, #1504]
    ldr q7, [x1, #1456]
    ldr q8, [x1, #1520]
    ldr q13, [x2, #80]
    tbl v26.16b, {v1.16b, v2.16b}, v13.16b
    tbl v27.16b, {v3.16b, v4.16b}, v13.16b
    tbl v28.16b, {v5.16b, v6.16b}, v13.16b
    tbl v29.16b, {v7.16b, v8.16b}, v13.16b
    uzp1 v18.8h, v9.8h, v26.8h
    uzp2 v26.8h, v9.8h, v26.8h
    mov v9.16b, v18.16b
    uzp1 v19.8h, v10.8h, v27.8h
    uzp2 v27.8h, v10.8h, v27.8h
    mov v10.16b, v19.16b
    uzp1 v20.8h, v11.8h, v28.8h
    uzp2 v28.8h, v11.8h, v28.8h
    mov v11.16b, v20.16b
    uzp1 v21.8h, v12.8h, v29.8h
    uzp2 v29.8h, v12.8h, v29.8h
    mov v12.16b, v21.16b
    bl module_keygen_pack_.Lgt_keygen_shared_pack64_core
    // canonical blocks 48..55; CQ groups 18/19
    ldr q1, [x1, #1152]
    ldr q2, [x1, #1216]
    ldr q3, [x1, #1168]
    ldr q4, [x1, #1232]
    ldr q5, [x1, #1184]
    ldr q6, [x1, #1248]
    ldr q7, [x1, #1200]
    ldr q8, [x1, #1264]
    ldr q13, [x2, #96]
    tbl v9.16b, {v1.16b, v2.16b}, v13.16b
    tbl v10.16b, {v3.16b, v4.16b}, v13.16b
    tbl v11.16b, {v5.16b, v6.16b}, v13.16b
    tbl v12.16b, {v7.16b, v8.16b}, v13.16b
    // canonical blocks 56..63; CQ groups 16/17
    ldr q1, [x1, #1024]
    ldr q2, [x1, #1088]
    ldr q3, [x1, #1040]
    ldr q4, [x1, #1104]
    ldr q5, [x1, #1056]
    ldr q6, [x1, #1120]
    ldr q7, [x1, #1072]
    ldr q8, [x1, #1136]
    ldr q13, [x2, #112]
    tbl v26.16b, {v1.16b, v2.16b}, v13.16b
    tbl v27.16b, {v3.16b, v4.16b}, v13.16b
    tbl v28.16b, {v5.16b, v6.16b}, v13.16b
    tbl v29.16b, {v7.16b, v8.16b}, v13.16b
    uzp1 v18.8h, v9.8h, v26.8h
    uzp2 v26.8h, v9.8h, v26.8h
    mov v9.16b, v18.16b
    uzp1 v19.8h, v10.8h, v27.8h
    uzp2 v27.8h, v10.8h, v27.8h
    mov v10.16b, v19.16b
    uzp1 v20.8h, v11.8h, v28.8h
    uzp2 v28.8h, v11.8h, v28.8h
    mov v11.16b, v20.16b
    uzp1 v21.8h, v12.8h, v29.8h
    uzp2 v29.8h, v12.8h, v29.8h
    mov v12.16b, v21.16b
    bl module_keygen_pack_.Lgt_keygen_shared_pack64_core
    // canonical blocks 64..71; CQ groups 8/9
    ldr q1, [x1, #512]
    ldr q2, [x1, #576]
    ldr q3, [x1, #528]
    ldr q4, [x1, #592]
    ldr q5, [x1, #544]
    ldr q6, [x1, #608]
    ldr q7, [x1, #560]
    ldr q8, [x1, #624]
    ldr q13, [x2, #128]
    tbl v9.16b, {v1.16b, v2.16b}, v13.16b
    tbl v10.16b, {v3.16b, v4.16b}, v13.16b
    tbl v11.16b, {v5.16b, v6.16b}, v13.16b
    tbl v12.16b, {v7.16b, v8.16b}, v13.16b
    // canonical blocks 72..79; CQ groups 10/11
    ldr q1, [x1, #640]
    ldr q2, [x1, #704]
    ldr q3, [x1, #656]
    ldr q4, [x1, #720]
    ldr q5, [x1, #672]
    ldr q6, [x1, #736]
    ldr q7, [x1, #688]
    ldr q8, [x1, #752]
    ldr q13, [x2, #144]
    tbl v26.16b, {v1.16b, v2.16b}, v13.16b
    tbl v27.16b, {v3.16b, v4.16b}, v13.16b
    tbl v28.16b, {v5.16b, v6.16b}, v13.16b
    tbl v29.16b, {v7.16b, v8.16b}, v13.16b
    uzp1 v18.8h, v9.8h, v26.8h
    uzp2 v26.8h, v9.8h, v26.8h
    mov v9.16b, v18.16b
    uzp1 v19.8h, v10.8h, v27.8h
    uzp2 v27.8h, v10.8h, v27.8h
    mov v10.16b, v19.16b
    uzp1 v20.8h, v11.8h, v28.8h
    uzp2 v28.8h, v11.8h, v28.8h
    mov v11.16b, v20.16b
    uzp1 v21.8h, v12.8h, v29.8h
    uzp2 v29.8h, v12.8h, v29.8h
    mov v12.16b, v21.16b
    bl module_keygen_pack_.Lgt_keygen_shared_pack64_core
    // canonical blocks 80..87; CQ groups 12/13
    ldr q1, [x1, #768]
    ldr q2, [x1, #832]
    ldr q3, [x1, #784]
    ldr q4, [x1, #848]
    ldr q5, [x1, #800]
    ldr q6, [x1, #864]
    ldr q7, [x1, #816]
    ldr q8, [x1, #880]
    ldr q13, [x2, #160]
    tbl v9.16b, {v1.16b, v2.16b}, v13.16b
    tbl v10.16b, {v3.16b, v4.16b}, v13.16b
    tbl v11.16b, {v5.16b, v6.16b}, v13.16b
    tbl v12.16b, {v7.16b, v8.16b}, v13.16b
    // canonical blocks 88..95; CQ groups 14/15
    ldr q1, [x1, #896]
    ldr q2, [x1, #960]
    ldr q3, [x1, #912]
    ldr q4, [x1, #976]
    ldr q5, [x1, #928]
    ldr q6, [x1, #992]
    ldr q7, [x1, #944]
    ldr q8, [x1, #1008]
    ldr q13, [x2, #176]
    tbl v26.16b, {v1.16b, v2.16b}, v13.16b
    tbl v27.16b, {v3.16b, v4.16b}, v13.16b
    tbl v28.16b, {v5.16b, v6.16b}, v13.16b
    tbl v29.16b, {v7.16b, v8.16b}, v13.16b
    uzp1 v18.8h, v9.8h, v26.8h
    uzp2 v26.8h, v9.8h, v26.8h
    mov v9.16b, v18.16b
    uzp1 v19.8h, v10.8h, v27.8h
    uzp2 v27.8h, v10.8h, v27.8h
    mov v10.16b, v19.16b
    uzp1 v20.8h, v11.8h, v28.8h
    uzp2 v28.8h, v11.8h, v28.8h
    mov v11.16b, v20.16b
    uzp1 v21.8h, v12.8h, v29.8h
    uzp2 v29.8h, v12.8h, v29.8h
    mov v12.16b, v21.16b
    bl module_keygen_pack_.Lgt_keygen_shared_pack64_core
    // canonical blocks 96..103; CQ groups 22/23
    ldr q1, [x1, #1408]
    ldr q2, [x1, #1472]
    ldr q3, [x1, #1424]
    ldr q4, [x1, #1488]
    ldr q5, [x1, #1440]
    ldr q6, [x1, #1504]
    ldr q7, [x1, #1456]
    ldr q8, [x1, #1520]
    ldr q13, [x2, #192]
    tbl v9.16b, {v1.16b, v2.16b}, v13.16b
    tbl v10.16b, {v3.16b, v4.16b}, v13.16b
    tbl v11.16b, {v5.16b, v6.16b}, v13.16b
    tbl v12.16b, {v7.16b, v8.16b}, v13.16b
    // canonical blocks 104..111; CQ groups 20/21
    ldr q1, [x1, #1280]
    ldr q2, [x1, #1344]
    ldr q3, [x1, #1296]
    ldr q4, [x1, #1360]
    ldr q5, [x1, #1312]
    ldr q6, [x1, #1376]
    ldr q7, [x1, #1328]
    ldr q8, [x1, #1392]
    ldr q13, [x2, #208]
    tbl v26.16b, {v1.16b, v2.16b}, v13.16b
    tbl v27.16b, {v3.16b, v4.16b}, v13.16b
    tbl v28.16b, {v5.16b, v6.16b}, v13.16b
    tbl v29.16b, {v7.16b, v8.16b}, v13.16b
    uzp1 v18.8h, v9.8h, v26.8h
    uzp2 v26.8h, v9.8h, v26.8h
    mov v9.16b, v18.16b
    uzp1 v19.8h, v10.8h, v27.8h
    uzp2 v27.8h, v10.8h, v27.8h
    mov v10.16b, v19.16b
    uzp1 v20.8h, v11.8h, v28.8h
    uzp2 v28.8h, v11.8h, v28.8h
    mov v11.16b, v20.16b
    uzp1 v21.8h, v12.8h, v29.8h
    uzp2 v29.8h, v12.8h, v29.8h
    mov v12.16b, v21.16b
    bl module_keygen_pack_.Lgt_keygen_shared_pack64_core
    // canonical blocks 112..119; CQ groups 16/17
    ldr q1, [x1, #1024]
    ldr q2, [x1, #1088]
    ldr q3, [x1, #1040]
    ldr q4, [x1, #1104]
    ldr q5, [x1, #1056]
    ldr q6, [x1, #1120]
    ldr q7, [x1, #1072]
    ldr q8, [x1, #1136]
    ldr q13, [x2, #224]
    tbl v9.16b, {v1.16b, v2.16b}, v13.16b
    tbl v10.16b, {v3.16b, v4.16b}, v13.16b
    tbl v11.16b, {v5.16b, v6.16b}, v13.16b
    tbl v12.16b, {v7.16b, v8.16b}, v13.16b
    // canonical blocks 120..127; CQ groups 18/19
    ldr q1, [x1, #1152]
    ldr q2, [x1, #1216]
    ldr q3, [x1, #1168]
    ldr q4, [x1, #1232]
    ldr q5, [x1, #1184]
    ldr q6, [x1, #1248]
    ldr q7, [x1, #1200]
    ldr q8, [x1, #1264]
    ldr q13, [x2, #240]
    tbl v26.16b, {v1.16b, v2.16b}, v13.16b
    tbl v27.16b, {v3.16b, v4.16b}, v13.16b
    tbl v28.16b, {v5.16b, v6.16b}, v13.16b
    tbl v29.16b, {v7.16b, v8.16b}, v13.16b
    uzp1 v18.8h, v9.8h, v26.8h
    uzp2 v26.8h, v9.8h, v26.8h
    mov v9.16b, v18.16b
    uzp1 v19.8h, v10.8h, v27.8h
    uzp2 v27.8h, v10.8h, v27.8h
    mov v10.16b, v19.16b
    uzp1 v20.8h, v11.8h, v28.8h
    uzp2 v28.8h, v11.8h, v28.8h
    mov v11.16b, v20.16b
    uzp1 v21.8h, v12.8h, v29.8h
    uzp2 v29.8h, v12.8h, v29.8h
    mov v12.16b, v21.16b
    bl module_keygen_pack_.Lgt_keygen_shared_pack64_core
    // canonical blocks 128..135; CQ groups 10/11
    ldr q1, [x1, #640]
    ldr q2, [x1, #704]
    ldr q3, [x1, #656]
    ldr q4, [x1, #720]
    ldr q5, [x1, #672]
    ldr q6, [x1, #736]
    ldr q7, [x1, #688]
    ldr q8, [x1, #752]
    ldr q13, [x2, #256]
    tbl v9.16b, {v1.16b, v2.16b}, v13.16b
    tbl v10.16b, {v3.16b, v4.16b}, v13.16b
    tbl v11.16b, {v5.16b, v6.16b}, v13.16b
    tbl v12.16b, {v7.16b, v8.16b}, v13.16b
    // canonical blocks 136..143; CQ groups 8/9
    ldr q1, [x1, #512]
    ldr q2, [x1, #576]
    ldr q3, [x1, #528]
    ldr q4, [x1, #592]
    ldr q5, [x1, #544]
    ldr q6, [x1, #608]
    ldr q7, [x1, #560]
    ldr q8, [x1, #624]
    ldr q13, [x2, #272]
    tbl v26.16b, {v1.16b, v2.16b}, v13.16b
    tbl v27.16b, {v3.16b, v4.16b}, v13.16b
    tbl v28.16b, {v5.16b, v6.16b}, v13.16b
    tbl v29.16b, {v7.16b, v8.16b}, v13.16b
    uzp1 v18.8h, v9.8h, v26.8h
    uzp2 v26.8h, v9.8h, v26.8h
    mov v9.16b, v18.16b
    uzp1 v19.8h, v10.8h, v27.8h
    uzp2 v27.8h, v10.8h, v27.8h
    mov v10.16b, v19.16b
    uzp1 v20.8h, v11.8h, v28.8h
    uzp2 v28.8h, v11.8h, v28.8h
    mov v11.16b, v20.16b
    uzp1 v21.8h, v12.8h, v29.8h
    uzp2 v29.8h, v12.8h, v29.8h
    mov v12.16b, v21.16b
    bl module_keygen_pack_.Lgt_keygen_shared_pack64_core
    // canonical blocks 144..151; CQ groups 14/15
    ldr q1, [x1, #896]
    ldr q2, [x1, #960]
    ldr q3, [x1, #912]
    ldr q4, [x1, #976]
    ldr q5, [x1, #928]
    ldr q6, [x1, #992]
    ldr q7, [x1, #944]
    ldr q8, [x1, #1008]
    ldr q13, [x2, #288]
    tbl v9.16b, {v1.16b, v2.16b}, v13.16b
    tbl v10.16b, {v3.16b, v4.16b}, v13.16b
    tbl v11.16b, {v5.16b, v6.16b}, v13.16b
    tbl v12.16b, {v7.16b, v8.16b}, v13.16b
    // canonical blocks 152..159; CQ groups 12/13
    ldr q1, [x1, #768]
    ldr q2, [x1, #832]
    ldr q3, [x1, #784]
    ldr q4, [x1, #848]
    ldr q5, [x1, #800]
    ldr q6, [x1, #864]
    ldr q7, [x1, #816]
    ldr q8, [x1, #880]
    ldr q13, [x2, #304]
    tbl v26.16b, {v1.16b, v2.16b}, v13.16b
    tbl v27.16b, {v3.16b, v4.16b}, v13.16b
    tbl v28.16b, {v5.16b, v6.16b}, v13.16b
    tbl v29.16b, {v7.16b, v8.16b}, v13.16b
    uzp1 v18.8h, v9.8h, v26.8h
    uzp2 v26.8h, v9.8h, v26.8h
    mov v9.16b, v18.16b
    uzp1 v19.8h, v10.8h, v27.8h
    uzp2 v27.8h, v10.8h, v27.8h
    mov v10.16b, v19.16b
    uzp1 v20.8h, v11.8h, v28.8h
    uzp2 v28.8h, v11.8h, v28.8h
    mov v11.16b, v20.16b
    uzp1 v21.8h, v12.8h, v29.8h
    uzp2 v29.8h, v12.8h, v29.8h
    mov v12.16b, v21.16b
    bl module_keygen_pack_.Lgt_keygen_shared_pack64_core
    // canonical blocks 160..167; CQ groups 4/5
    ldr q1, [x1, #256]
    ldr q2, [x1, #320]
    ldr q3, [x1, #272]
    ldr q4, [x1, #336]
    ldr q5, [x1, #288]
    ldr q6, [x1, #352]
    ldr q7, [x1, #304]
    ldr q8, [x1, #368]
    ldr q13, [x2, #320]
    tbl v9.16b, {v1.16b, v2.16b}, v13.16b
    tbl v10.16b, {v3.16b, v4.16b}, v13.16b
    tbl v11.16b, {v5.16b, v6.16b}, v13.16b
    tbl v12.16b, {v7.16b, v8.16b}, v13.16b
    // canonical blocks 168..175; CQ groups 6/7
    ldr q1, [x1, #384]
    ldr q2, [x1, #448]
    ldr q3, [x1, #400]
    ldr q4, [x1, #464]
    ldr q5, [x1, #416]
    ldr q6, [x1, #480]
    ldr q7, [x1, #432]
    ldr q8, [x1, #496]
    ldr q13, [x2, #336]
    tbl v26.16b, {v1.16b, v2.16b}, v13.16b
    tbl v27.16b, {v3.16b, v4.16b}, v13.16b
    tbl v28.16b, {v5.16b, v6.16b}, v13.16b
    tbl v29.16b, {v7.16b, v8.16b}, v13.16b
    uzp1 v18.8h, v9.8h, v26.8h
    uzp2 v26.8h, v9.8h, v26.8h
    mov v9.16b, v18.16b
    uzp1 v19.8h, v10.8h, v27.8h
    uzp2 v27.8h, v10.8h, v27.8h
    mov v10.16b, v19.16b
    uzp1 v20.8h, v11.8h, v28.8h
    uzp2 v28.8h, v11.8h, v28.8h
    mov v11.16b, v20.16b
    uzp1 v21.8h, v12.8h, v29.8h
    uzp2 v29.8h, v12.8h, v29.8h
    mov v12.16b, v21.16b
    bl module_keygen_pack_.Lgt_keygen_shared_pack64_core
    // canonical blocks 176..183; CQ groups 2/3
    ldr q1, [x1, #128]
    ldr q2, [x1, #192]
    ldr q3, [x1, #144]
    ldr q4, [x1, #208]
    ldr q5, [x1, #160]
    ldr q6, [x1, #224]
    ldr q7, [x1, #176]
    ldr q8, [x1, #240]
    ldr q13, [x2, #352]
    tbl v9.16b, {v1.16b, v2.16b}, v13.16b
    tbl v10.16b, {v3.16b, v4.16b}, v13.16b
    tbl v11.16b, {v5.16b, v6.16b}, v13.16b
    tbl v12.16b, {v7.16b, v8.16b}, v13.16b
    // canonical blocks 184..191; CQ groups 0/1
    ldr q1, [x1, #0]
    ldr q2, [x1, #64]
    ldr q3, [x1, #16]
    ldr q4, [x1, #80]
    ldr q5, [x1, #32]
    ldr q6, [x1, #96]
    ldr q7, [x1, #48]
    ldr q8, [x1, #112]
    ldr q13, [x2, #368]
    tbl v26.16b, {v1.16b, v2.16b}, v13.16b
    tbl v27.16b, {v3.16b, v4.16b}, v13.16b
    tbl v28.16b, {v5.16b, v6.16b}, v13.16b
    tbl v29.16b, {v7.16b, v8.16b}, v13.16b
    uzp1 v18.8h, v9.8h, v26.8h
    uzp2 v26.8h, v9.8h, v26.8h
    mov v9.16b, v18.16b
    uzp1 v19.8h, v10.8h, v27.8h
    uzp2 v27.8h, v10.8h, v27.8h
    mov v10.16b, v19.16b
    uzp1 v20.8h, v11.8h, v28.8h
    uzp2 v28.8h, v11.8h, v28.8h
    mov v11.16b, v20.16b
    uzp1 v21.8h, v12.8h, v29.8h
    uzp2 v29.8h, v12.8h, v29.8h
    mov v12.16b, v21.16b
    bl module_keygen_pack_.Lgt_keygen_shared_pack64_core
    ldr x30, [sp, #64]
    ldp d8, d9, [sp, #0]
    ldp d10, d11, [sp, #16]
    ldp d12, d13, [sp, #32]
    ldp d14, d15, [sp, #48]
    add sp, sp, #80
    ret

.p2align 4
.p2align 4
module_keygen_pack_.Lgt_keygen_shared_pack64_core:
    sshr v8.8h, v9.8h, #15
    sshr v30.8h, v10.8h, #15
    and v25.16b, v8.16b, v0.16b
    sshr v24.8h, v12.8h, #15
    sshr v18.8h, v11.8h, #15
    and v30.16b, v30.16b, v0.16b
    add v7.8h, v9.8h, v25.8h
    and v4.16b, v24.16b, v0.16b
    sshr v3.8h, v26.8h, #15
    and v9.16b, v18.16b, v0.16b
    add v24.8h, v12.8h, v4.8h
    sshr v19.8h, v29.8h, #15
    add v21.8h, v11.8h, v9.8h
    sshr v9.8h, v27.8h, #15
    and v19.16b, v19.16b, v0.16b
    shl v11.8h, v24.8h, #4
    and v25.16b, v9.16b, v0.16b
    sshr v1.8h, v28.8h, #15
    add v10.8h, v10.8h, v30.8h
    add v9.8h, v29.8h, v19.8h
    add v25.8h, v27.8h, v25.8h
    ushr v8.8h, v21.8h, #8
    and v22.16b, v3.16b, v0.16b
    ushr v20.8h, v10.8h, #4
    shl v24.8h, v9.8h, #4
    and v3.16b, v1.16b, v0.16b
    eor v11.16b, v8.16b, v11.16b
    ushr v15.8h, v25.8h, #4
    add v2.8h, v28.8h, v3.8h
    shl v19.8h, v10.8h, #12
    shl v18.8h, v21.8h, #8
    add v5.8h, v26.8h, v22.8h
    shl v25.8h, v25.8h, #12
    eor v31.16b, v7.16b, v19.16b
    shl v9.8h, v2.8h, #8
    eor v6.16b, v20.16b, v18.16b
    ushr v3.8h, v2.8h, #8
    eor v8.16b, v5.16b, v25.16b
    trn1 v1.8h, v31.8h, v6.8h
    eor v27.16b, v15.16b, v9.16b
    eor v3.16b, v3.16b, v24.16b
    trn1 v9.8h, v11.8h, v8.8h
    trn2 v30.8h, v31.8h, v6.8h
    trn2 v5.8h, v11.8h, v8.8h
    trn2 v14.4s, v1.4s, v9.4s
    trn2 v8.8h, v27.8h, v3.8h
    trn1 v18.8h, v27.8h, v3.8h
    trn1 v25.4s, v1.4s, v9.4s
    trn1 v22.4s, v5.4s, v8.4s
    trn2 v24.4s, v5.4s, v8.4s
    trn1 v10.4s, v18.4s, v30.4s
    trn2 v18.4s, v18.4s, v30.4s
    trn1 v2.2d, v22.2d, v14.2d
    trn2 v5.2d, v22.2d, v14.2d
    trn1 v1.2d, v25.2d, v10.2d
    trn1 v3.2d, v18.2d, v24.2d
    trn2 v4.2d, v25.2d, v10.2d
    trn2 v6.2d, v18.2d, v24.2d
    st1 {v1.8h, v2.8h, v3.8h}, [x0], #48
    st1 {v4.8h, v5.8h, v6.8h}, [x0], #48
    ret

.p2align 4
module_keygen_pack_.Lbpq_cq_pack_indexes:
    .byte 18, 19, 16, 17, 22, 23, 20, 21, 6, 7, 4, 5, 0, 1, 2, 3
    .byte 0, 1, 2, 3, 6, 7, 22, 23, 16, 17, 18, 19, 20, 21, 4, 5
    .byte 18, 19, 16, 17, 22, 23, 20, 21, 6, 7, 4, 5, 0, 1, 2, 3
    .byte 6, 7, 4, 5, 0, 1, 2, 3, 22, 23, 20, 21, 16, 17, 18, 19
    .byte 0, 1, 2, 3, 4, 5, 6, 7, 16, 17, 18, 19, 20, 21, 22, 23
    .byte 0, 1, 2, 3, 4, 5, 6, 7, 16, 17, 18, 19, 20, 21, 22, 23
    .byte 0, 1, 2, 3, 4, 5, 6, 7, 16, 17, 18, 19, 20, 21, 22, 23
    .byte 20, 21, 4, 5, 18, 19, 16, 17, 2, 3, 0, 1, 22, 23, 6, 7
    .byte 18, 19, 16, 17, 4, 5, 20, 21, 22, 23, 6, 7, 0, 1, 2, 3
    .byte 20, 21, 22, 23, 18, 19, 16, 17, 2, 3, 0, 1, 6, 7, 4, 5
    .byte 20, 21, 22, 23, 18, 19, 16, 17, 2, 3, 0, 1, 6, 7, 4, 5
    .byte 20, 21, 22, 23, 18, 19, 16, 17, 2, 3, 0, 1, 6, 7, 4, 5
    .byte 12, 13, 14, 15, 10, 11, 8, 9, 28, 29, 30, 31, 26, 27, 24, 25
    .byte 28, 29, 30, 31, 26, 27, 24, 25, 10, 11, 8, 9, 14, 15, 12, 13
    .byte 26, 27, 24, 25, 12, 13, 28, 29, 30, 31, 14, 15, 8, 9, 10, 11
    .byte 28, 29, 30, 31, 26, 27, 24, 25, 10, 11, 8, 9, 14, 15, 12, 13
    .byte 26, 27, 24, 25, 30, 31, 28, 29, 14, 15, 12, 13, 8, 9, 10, 11
    .byte 8, 9, 10, 11, 14, 15, 30, 31, 24, 25, 26, 27, 28, 29, 12, 13
    .byte 26, 27, 24, 25, 30, 31, 28, 29, 14, 15, 12, 13, 8, 9, 10, 11
    .byte 14, 15, 12, 13, 8, 9, 10, 11, 30, 31, 28, 29, 24, 25, 26, 27
    .byte 8, 9, 10, 11, 12, 13, 14, 15, 24, 25, 26, 27, 28, 29, 30, 31
    .byte 8, 9, 10, 11, 12, 13, 14, 15, 24, 25, 26, 27, 28, 29, 30, 31
    .byte 8, 9, 10, 11, 12, 13, 14, 15, 24, 25, 26, 27, 28, 29, 30, 31
    .byte 28, 29, 12, 13, 26, 27, 24, 25, 10, 11, 8, 9, 30, 31, 14, 15
.p2align 4
module_keygen_pack_.Lbpq_cq_pack_q:
    .hword 3457, 3457, 3457, 3457
    .hword 3457, 3457, 3457, 3457

/* END original keygen_pack.S */

/* BEGIN original decap_pack.S; private namespace module_decap_pack_ */
/*************************************************
* Name:        poly_frombytes_decap
*
* Description: De-serializes a polynomial from its canonical 12-bit
*              coefficient representation.
*
* Arguments:   - poly *r:          pointer to the output polynomial
*              - const uint8_t *a: pointer to NTRUPLUS_POLYBYTES input bytes
*
* Returns:     0 on success, 1 if any coefficient is greater than or equal to q.
*              Output coefficients lie in [0,4095].
**************************************************/
.global poly_frombytes_decap
.global _poly_frombytes_decap
poly_frombytes_decap:
_poly_frombytes_decap:
    stp d8,  d9,  [sp, #-64]!
    stp d10, d11, [sp, #16]
    stp d12, d13, [sp, #32]
    stp d14, d15, [sp, #48]

    module_decap_pack_dst       .req x0
    module_decap_pack_src       .req x1
    module_decap_pack_counter   .req x8

    adr x2, module_decap_pack_const_mask_0fff
    ldr q0, [x2]
    movi v29.8h, #0

    mov module_decap_pack_counter, #1536

module_decap_pack__loop_frombytes:
    ld1 {v1.8h-v3.8h}, [module_decap_pack_src], #48
    ld1 {v4.8h-v6.8h}, [module_decap_pack_src], #48

    trn1 v7.2d,  v1.2d, v4.2d
    trn2 v8.2d,  v1.2d, v4.2d
    trn1 v9.2d,  v2.2d, v5.2d
    trn2 v10.2d, v2.2d, v5.2d
    trn1 v11.2d, v3.2d, v6.2d
    trn2 v12.2d, v3.2d, v6.2d

    trn1 v13.4s, v7.4s, v10.4s
    trn2 v14.4s, v7.4s, v10.4s
    trn1 v15.4s, v8.4s, v11.4s
    trn2 v16.4s, v8.4s, v11.4s
    trn1 v17.4s, v9.4s, v12.4s
    trn2 v18.4s, v9.4s, v12.4s

    trn1 v19.8h, v13.8h, v16.8h
    trn2 v20.8h, v13.8h, v16.8h
    trn1 v21.8h, v14.8h, v17.8h
    trn2 v22.8h, v14.8h, v17.8h
    trn1 v23.8h, v15.8h, v18.8h
    trn2 v24.8h, v15.8h, v18.8h

    ushr v25.8h, v19.8h, #12
    sli  v25.8h, v20.8h, #4
    ushr v27.8h, v20.8h, #8
    sli  v27.8h, v21.8h, #8
    ushr v11.8h, v21.8h, #4

    ushr v30.8h, v22.8h, #12
    sli  v30.8h, v23.8h, #4
    ushr v1.8h,  v23.8h, #8
    sli  v1.8h,  v24.8h, #8
    ushr v15.8h, v24.8h, #4

    and v8.16b,  v19.16b, v0.16b
    and v9.16b,  v25.16b, v0.16b
    and v10.16b, v27.16b, v0.16b
    and v12.16b, v22.16b, v0.16b
    and v13.16b, v30.16b, v0.16b
    and v14.16b, v1.16b,  v0.16b

    st1 {v8.8h-v11.8h},  [module_decap_pack_dst], #64
    st1 {v12.8h-v15.8h}, [module_decap_pack_dst], #64

    umax v25.8h, v8.8h,  v9.8h
    umax v26.8h, v10.8h, v11.8h
    umax v27.8h, v12.8h, v13.8h
    umax v28.8h, v14.8h, v15.8h
    umax v25.8h, v25.8h, v26.8h
    umax v27.8h, v27.8h, v28.8h
    umax v25.8h, v25.8h, v27.8h
    umax v29.8h, v29.8h, v25.8h

    subs module_decap_pack_counter, module_decap_pack_counter, #128
    b.ne module_decap_pack__loop_frombytes

    .unreq module_decap_pack_dst
    .unreq module_decap_pack_src
    .unreq module_decap_pack_counter

    umaxv h29, v29.8h
    umov w0, v29.h[0]
    cmp w0, #3457
    cset w0, hs

    ldp d10, d11, [sp, #16]
    ldp d12, d13, [sp, #32]
    ldp d14, d15, [sp, #48]
    ldp d8,  d9,  [sp]
    add sp, sp, #64
    ret


/*************************************************
* Name:        poly_tobytes_decap
*
* Description: Reduces polynomial coefficients to [0,q) and serializes each
*              coefficient into 12 bits.
*
* Arguments:   - uint8_t *r:    pointer to NTRUPLUS_POLYBYTES output bytes
*              - const poly *a: pointer to the input polynomial;
*                               coefficients must lie in (-5q/2,5q/2)
*
* Returns:     none.
**************************************************/
.global poly_tobytes_decap
.global _poly_tobytes_decap
poly_tobytes_decap:
_poly_tobytes_decap:
    stp d8,  d9,  [sp, #-64]!
    stp d10, d11, [sp, #16]
    stp d12, d13, [sp, #32]
    stp d14, d15, [sp, #48]

    module_decap_pack_dst       .req x0
    module_decap_pack_src       .req x1
    module_decap_pack_counter   .req x8

    adr x2, module_decap_pack_const_q
    ldr q0, [x2]

    mov module_decap_pack_counter, #1536

module_decap_pack__loop_tobytes:
    #load
    ld1 {v1.8h-v4.8h}, [module_decap_pack_src], #64
    ld1 {v5.8h-v8.8h}, [module_decap_pack_src], #64

    # Barrett reduction with round(2^15/q) = 9
    sqrdmulh v10.8h, v1.8h, v0.h[1]
    sqrdmulh v11.8h, v2.8h, v0.h[1]
    sqrdmulh v12.8h, v3.8h, v0.h[1]
    sqrdmulh v13.8h, v4.8h, v0.h[1]
    sqrdmulh v14.8h, v5.8h, v0.h[1]
    sqrdmulh v15.8h, v6.8h, v0.h[1]
    sqrdmulh v16.8h, v7.8h, v0.h[1]
    sqrdmulh v17.8h, v8.8h, v0.h[1]
    mls v1.8h, v10.8h, v0.h[0]
    mls v2.8h, v11.8h, v0.h[0]
    mls v3.8h, v12.8h, v0.h[0]
    mls v4.8h, v13.8h, v0.h[0]
    mls v5.8h, v14.8h, v0.h[0]
    mls v6.8h, v15.8h, v0.h[0]
    mls v7.8h, v16.8h, v0.h[0]
    mls v8.8h, v17.8h, v0.h[0]

    cmlt v9.8h,  v1.8h, #0
    cmlt v10.8h, v2.8h, #0
    cmlt v11.8h, v3.8h, #0
    cmlt v12.8h, v4.8h, #0
    cmlt v13.8h, v5.8h, #0
    cmlt v14.8h, v6.8h, #0
    cmlt v15.8h, v7.8h, #0
    cmlt v16.8h, v8.8h, #0
    mls v1.8h, v9.8h,  v0.h[0]
    mls v2.8h, v10.8h, v0.h[0]
    mls v3.8h, v11.8h, v0.h[0]
    mls v4.8h, v12.8h, v0.h[0]
    mls v5.8h, v13.8h, v0.h[0]
    mls v6.8h, v14.8h, v0.h[0]
    mls v7.8h, v15.8h, v0.h[0]
    mls v8.8h, v16.8h, v0.h[0]

    sli  v1.8h, v2.8h, #12
    ushr v9.8h, v2.8h, #4
    sli  v9.8h, v3.8h, #8
    ushr v10.8h, v3.8h, #8
    sli  v10.8h, v4.8h, #4
    sli  v5.8h, v6.8h, #12
    ushr v11.8h, v6.8h, #4
    sli  v11.8h, v7.8h, #8
    ushr v12.8h, v7.8h, #8
    sli  v12.8h, v8.8h, #4

    trn1 v25.8h, v1.8h,  v9.8h
    trn1 v26.8h, v10.8h, v5.8h
    trn1 v27.8h, v11.8h, v12.8h
    trn2 v28.8h, v1.8h,  v9.8h
    trn2 v29.8h, v10.8h, v5.8h
    trn2 v30.8h, v11.8h, v12.8h

    trn1 v1.4s, v25.4s, v26.4s
    trn1 v2.4s, v27.4s, v28.4s
    trn1 v3.4s, v29.4s, v30.4s
    trn2 v4.4s, v25.4s, v26.4s
    trn2 v5.4s, v27.4s, v28.4s
    trn2 v6.4s, v29.4s, v30.4s

    trn1 v7.2d,  v1.2d, v2.2d
    trn1 v8.2d,  v3.2d, v4.2d
    trn1 v9.2d,  v5.2d, v6.2d
    trn2 v10.2d, v1.2d, v2.2d
    trn2 v11.2d, v3.2d, v4.2d
    trn2 v12.2d, v5.2d, v6.2d

    #store
    st1 {v7.8h-v9.8h},   [module_decap_pack_dst], #48
    st1 {v10.8h-v12.8h}, [module_decap_pack_dst], #48

    subs module_decap_pack_counter, module_decap_pack_counter, #128
    b.ne module_decap_pack__loop_tobytes

    .unreq    module_decap_pack_dst
    .unreq    module_decap_pack_src
    .unreq    module_decap_pack_counter

    ldp d10, d11, [sp, #16]
    ldp d12, d13, [sp, #32]
    ldp d14, d15, [sp, #48]
    ldp d8,  d9,  [sp]
    add sp, sp, #64
    ret


.align 4
module_decap_pack_const_mask_0fff:
    .hword 0x0fff, 0x0fff, 0x0fff, 0x0fff
    .hword 0x0fff, 0x0fff, 0x0fff, 0x0fff

.align 4
module_decap_pack_const_q:
    .hword 0x0d81, 0x0009, 0x0000, 0x0000
    .hword 0x0000, 0x0000, 0x0000, 0x0000

/* END original decap_pack.S */
