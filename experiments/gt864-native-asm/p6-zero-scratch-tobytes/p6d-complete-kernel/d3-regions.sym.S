.text
.global gt864_p6d3_route_a
gt864_p6d3_route_a:
// live-in: serialized frontier via x3, coefficient rows via x29, and fixed public tables via x30.
// live-out: exact next frontier via x4, or final canonical byte stream via the public output pointer.
// range: input coefficients are signed int16; normalized coefficients are 0..3456; packed lanes are bytes.
// reserved physical registers: x18 and sp; x29/x30 are intentionally fixed by the complete-function ABI.
gt864_p6d3_route_a_slothy_start:
    ldr Q<s0>, [x3, #0]
    ldr Q<s1>, [x3, #16]
    ldr Q<s2>, [x3, #32]
    ldr Q<s3>, [x3, #48]
    ldr Q<s4>, [x3, #64]
    ldr Q<s5>, [x3, #80]
    ldr Q<s6>, [x3, #96]
    ldr Q<s7>, [x3, #112]
    ldr Q<s8>, [x3, #128]
    ldr Q<s9>, [x3, #144]
    ldr Q<s10>, [x3, #160]
    ldr Q<s11>, [x3, #176]
    ldr Q<s12>, [x3, #192]
    ldr Q<aj0>, [x29, #832]
    ldr Q<aj1>, [x29, #784]
    ext V<aj1>.16b, V<aj1>.16b, V<aj1>.16b, #14
    ldr Q<aj2>, [x29, #736]
    ext V<aj2>.16b, V<aj2>.16b, V<aj2>.16b, #12
    ldr Q<aj3>, [x29, #688]
    ext V<aj3>.16b, V<aj3>.16b, V<aj3>.16b, #10
    ldr Q<aj4>, [x29, #640]
    ext V<aj4>.16b, V<aj4>.16b, V<aj4>.16b, #8
    ldr Q<aj5>, [x29, #592]
    ext V<aj5>.16b, V<aj5>.16b, V<aj5>.16b, #6
    ldr Q<aj6>, [x29, #544]
    ext V<aj6>.16b, V<aj6>.16b, V<aj6>.16b, #4
    ldr Q<aj7>, [x29, #496]
    ext V<aj7>.16b, V<aj7>.16b, V<aj7>.16b, #2
    ldr Q<aninth>, [x29, #448]
    trn1 V<au0>.8h, V<aj0>.8h, V<aj1>.8h
    trn2 V<au1>.8h, V<aj0>.8h, V<aj1>.8h
    trn1 V<au2>.8h, V<aj2>.8h, V<aj3>.8h
    trn2 V<au3>.8h, V<aj2>.8h, V<aj3>.8h
    trn1 V<au4>.8h, V<aj4>.8h, V<aj5>.8h
    trn2 V<au5>.8h, V<aj4>.8h, V<aj5>.8h
    trn1 V<au6>.8h, V<aj6>.8h, V<aj7>.8h
    trn2 V<au7>.8h, V<aj6>.8h, V<aj7>.8h
    trn1 V<az0>.4s, V<au0>.4s, V<au2>.4s
    trn2 V<az2>.4s, V<au0>.4s, V<au2>.4s
    trn1 V<az4>.4s, V<au4>.4s, V<au6>.4s
    trn2 V<az6>.4s, V<au4>.4s, V<au6>.4s
    trn1 V<az1>.4s, V<au1>.4s, V<au3>.4s
    trn2 V<az3>.4s, V<au1>.4s, V<au3>.4s
    trn1 V<az5>.4s, V<au5>.4s, V<au7>.4s
    trn2 V<az7>.4s, V<au5>.4s, V<au7>.4s
    trn1 V<at0>.2d, V<az0>.2d, V<az4>.2d
    trn2 V<at4>.2d, V<az0>.2d, V<az4>.2d
    trn1 V<at1>.2d, V<az1>.2d, V<az5>.2d
    trn2 V<at5>.2d, V<az1>.2d, V<az5>.2d
    trn1 V<at2>.2d, V<az2>.2d, V<az6>.2d
    trn2 V<at6>.2d, V<az2>.2d, V<az6>.2d
    trn1 V<at3>.2d, V<az3>.2d, V<az7>.2d
    trn2 V<at7>.2d, V<az3>.2d, V<az7>.2d
    orr V<a0>.16b, V<at0>.16b, V<at0>.16b
    ins V<a0>.h[0], V<aninth>.h[0]
    ldr Q<aidx0>, [x30, #160]
    tbl V<a0>.16b, {V<a0>.16b}, V<aidx0>.16b
    ldr Q<amask1>, [x30, #0]
    and V<a1>.16b, V<at0>.16b, V<amask1>.16b
    bic V<aother1>.16b, V<at1>.16b, V<amask1>.16b
    orr V<a1>.16b, V<a1>.16b, V<aother1>.16b
    ins V<a1>.h[1], V<aninth>.h[1]
    ldr Q<aidx1>, [x30, #176]
    tbl V<a1>.16b, {V<a1>.16b}, V<aidx1>.16b
    ldr Q<amask2>, [x30, #16]
    and V<a2>.16b, V<at1>.16b, V<amask2>.16b
    bic V<aother2>.16b, V<at2>.16b, V<amask2>.16b
    orr V<a2>.16b, V<a2>.16b, V<aother2>.16b
    ins V<a2>.h[2], V<aninth>.h[2]
    ldr Q<aidx2>, [x30, #192]
    tbl V<a2>.16b, {V<a2>.16b}, V<aidx2>.16b
    ldr Q<amask3>, [x30, #32]
    and V<a3>.16b, V<at2>.16b, V<amask3>.16b
    bic V<aother3>.16b, V<at3>.16b, V<amask3>.16b
    orr V<a3>.16b, V<a3>.16b, V<aother3>.16b
    ins V<a3>.h[3], V<aninth>.h[3]
    ldr Q<aidx3>, [x30, #208]
    tbl V<a3>.16b, {V<a3>.16b}, V<aidx3>.16b
    ldr Q<amask4>, [x30, #48]
    and V<a4>.16b, V<at3>.16b, V<amask4>.16b
    bic V<aother4>.16b, V<at4>.16b, V<amask4>.16b
    orr V<a4>.16b, V<a4>.16b, V<aother4>.16b
    ins V<a4>.h[4], V<aninth>.h[4]
    ldr Q<aidx4>, [x30, #224]
    tbl V<a4>.16b, {V<a4>.16b}, V<aidx4>.16b
    ldr Q<amask5>, [x30, #64]
    and V<a5>.16b, V<at4>.16b, V<amask5>.16b
    bic V<aother5>.16b, V<at5>.16b, V<amask5>.16b
    orr V<a5>.16b, V<a5>.16b, V<aother5>.16b
    ins V<a5>.h[5], V<aninth>.h[5]
    ldr Q<aidx5>, [x30, #240]
    tbl V<a5>.16b, {V<a5>.16b}, V<aidx5>.16b
    ldr Q<amask6>, [x30, #80]
    and V<a6>.16b, V<at5>.16b, V<amask6>.16b
    bic V<aother6>.16b, V<at6>.16b, V<amask6>.16b
    orr V<a6>.16b, V<a6>.16b, V<aother6>.16b
    ins V<a6>.h[6], V<aninth>.h[6]
    ldr Q<aidx6>, [x30, #256]
    tbl V<a6>.16b, {V<a6>.16b}, V<aidx6>.16b
    orr V<a7>.16b, V<at6>.16b, V<at6>.16b
    ins V<a7>.h[7], V<aninth>.h[7]
    ldr Q<aidx7>, [x30, #272]
    tbl V<a7>.16b, {V<a7>.16b}, V<aidx7>.16b
    orr V<a8>.16b, V<at7>.16b, V<at7>.16b
    ldr Q<aidx8>, [x30, #288]
    tbl V<a8>.16b, {V<a8>.16b}, V<aidx8>.16b
    str Q<s0>, [x4, #0]
    str Q<s1>, [x4, #16]
    str Q<s2>, [x4, #32]
    str Q<s3>, [x4, #48]
    str Q<s4>, [x4, #64]
    str Q<s5>, [x4, #80]
    str Q<s6>, [x4, #96]
    str Q<s7>, [x4, #112]
    str Q<s8>, [x4, #128]
    str Q<s9>, [x4, #144]
    str Q<s10>, [x4, #160]
    str Q<s11>, [x4, #176]
    str Q<s12>, [x4, #192]
    str Q<a0>, [x4, #208]
    str Q<a1>, [x4, #224]
    str Q<a2>, [x4, #240]
    str Q<a3>, [x4, #256]
    str Q<a4>, [x4, #272]
    str Q<a5>, [x4, #288]
    str Q<a6>, [x4, #304]
    str Q<a7>, [x4, #320]
    str Q<a8>, [x4, #336]
gt864_p6d3_route_a_slothy_end:
    ret

.global gt864_p6d3_pack_a
gt864_p6d3_pack_a:
// live-in: serialized frontier via x3, coefficient rows via x29, and fixed public tables via x30.
// live-out: exact next frontier via x4, or final canonical byte stream via the public output pointer.
// range: input coefficients are signed int16; normalized coefficients are 0..3456; packed lanes are bytes.
// reserved physical registers: x18 and sp; x29/x30 are intentionally fixed by the complete-function ABI.
gt864_p6d3_pack_a_slothy_start:
    ldr Q<s0>, [x3, #0]
    ldr Q<s1>, [x3, #16]
    ldr Q<s2>, [x3, #32]
    ldr Q<s3>, [x3, #48]
    ldr Q<s4>, [x3, #64]
    ldr Q<s5>, [x3, #80]
    ldr Q<s6>, [x3, #96]
    ldr Q<s7>, [x3, #112]
    ldr Q<s8>, [x3, #128]
    ldr Q<s9>, [x3, #144]
    ldr Q<s10>, [x3, #160]
    ldr Q<s11>, [x3, #176]
    ldr Q<s12>, [x3, #192]
    ldr Q<a0>, [x3, #208]
    ldr Q<a1>, [x3, #224]
    ldr Q<a2>, [x3, #240]
    ldr Q<a3>, [x3, #256]
    ldr Q<a4>, [x3, #272]
    ldr Q<a5>, [x3, #288]
    ldr Q<a6>, [x3, #304]
    ldr Q<a7>, [x3, #320]
    ldr Q<a8>, [x3, #336]
    ldr Q<modq>, [x30, #336]
    ldr Q<recip>, [x30, #352]
    sqrdmulh V<quota0>.8h, V<a0>.8h, V<recip>.8h
    mls V<a0>.8h, V<quota0>.8h, V<modq>.8h
    sshr V<quota0>.8h, V<a0>.8h, #15
    and V<quota0>.16b, V<quota0>.16b, V<modq>.16b
    add V<a0>.8h, V<a0>.8h, V<quota0>.8h
    xtn V<lo0>.8b, V<a0>.8h
    movi V<L0>.16b, #0
    mov V<L0>.d[0], V<lo0>.d[0]
    ushr V<hi0>.8h, V<a0>.8h, #8
    uzp1 V<he0>.8h, V<hi0>.8h, V<hi0>.8h
    uzp2 V<ho0>.8h, V<hi0>.8h, V<hi0>.8h
    sli V<he0>.8h, V<ho0>.8h, #4
    xtn V<hp0>.8b, V<he0>.8h
    movi V<H0>.16b, #0
    ins V<H0>.h[0], V<hp0>.h[0]
    ins V<H0>.h[1], V<hp0>.h[1]
    sqrdmulh V<quota1>.8h, V<a1>.8h, V<recip>.8h
    mls V<a1>.8h, V<quota1>.8h, V<modq>.8h
    sshr V<quota1>.8h, V<a1>.8h, #15
    and V<quota1>.16b, V<quota1>.16b, V<modq>.16b
    add V<a1>.8h, V<a1>.8h, V<quota1>.8h
    xtn V<lo1>.8b, V<a1>.8h
    mov V<L0>.d[1], V<lo1>.d[0]
    ushr V<hi1>.8h, V<a1>.8h, #8
    uzp1 V<he1>.8h, V<hi1>.8h, V<hi1>.8h
    uzp2 V<ho1>.8h, V<hi1>.8h, V<hi1>.8h
    sli V<he1>.8h, V<ho1>.8h, #4
    xtn V<hp1>.8b, V<he1>.8h
    ins V<H0>.h[2], V<hp1>.h[0]
    ins V<H0>.h[3], V<hp1>.h[1]
    sqrdmulh V<quota2>.8h, V<a2>.8h, V<recip>.8h
    mls V<a2>.8h, V<quota2>.8h, V<modq>.8h
    sshr V<quota2>.8h, V<a2>.8h, #15
    and V<quota2>.16b, V<quota2>.16b, V<modq>.16b
    add V<a2>.8h, V<a2>.8h, V<quota2>.8h
    xtn V<lo2>.8b, V<a2>.8h
    movi V<L1>.16b, #0
    mov V<L1>.d[0], V<lo2>.d[0]
    ushr V<hi2>.8h, V<a2>.8h, #8
    uzp1 V<he2>.8h, V<hi2>.8h, V<hi2>.8h
    uzp2 V<ho2>.8h, V<hi2>.8h, V<hi2>.8h
    sli V<he2>.8h, V<ho2>.8h, #4
    xtn V<hp2>.8b, V<he2>.8h
    ins V<H0>.h[4], V<hp2>.h[0]
    ins V<H0>.h[5], V<hp2>.h[1]
    sqrdmulh V<quota3>.8h, V<a3>.8h, V<recip>.8h
    mls V<a3>.8h, V<quota3>.8h, V<modq>.8h
    sshr V<quota3>.8h, V<a3>.8h, #15
    and V<quota3>.16b, V<quota3>.16b, V<modq>.16b
    add V<a3>.8h, V<a3>.8h, V<quota3>.8h
    xtn V<lo3>.8b, V<a3>.8h
    mov V<L1>.d[1], V<lo3>.d[0]
    ushr V<hi3>.8h, V<a3>.8h, #8
    uzp1 V<he3>.8h, V<hi3>.8h, V<hi3>.8h
    uzp2 V<ho3>.8h, V<hi3>.8h, V<hi3>.8h
    sli V<he3>.8h, V<ho3>.8h, #4
    xtn V<hp3>.8b, V<he3>.8h
    ins V<H0>.h[6], V<hp3>.h[0]
    ins V<H0>.h[7], V<hp3>.h[1]
    sqrdmulh V<quota4>.8h, V<a4>.8h, V<recip>.8h
    mls V<a4>.8h, V<quota4>.8h, V<modq>.8h
    sshr V<quota4>.8h, V<a4>.8h, #15
    and V<quota4>.16b, V<quota4>.16b, V<modq>.16b
    add V<a4>.8h, V<a4>.8h, V<quota4>.8h
    xtn V<lo4>.8b, V<a4>.8h
    movi V<L2>.16b, #0
    mov V<L2>.d[0], V<lo4>.d[0]
    ushr V<hi4>.8h, V<a4>.8h, #8
    uzp1 V<he4>.8h, V<hi4>.8h, V<hi4>.8h
    uzp2 V<ho4>.8h, V<hi4>.8h, V<hi4>.8h
    sli V<he4>.8h, V<ho4>.8h, #4
    xtn V<hp4>.8b, V<he4>.8h
    movi V<H1>.16b, #0
    ins V<H1>.h[0], V<hp4>.h[0]
    ins V<H1>.h[1], V<hp4>.h[1]
    sqrdmulh V<quota5>.8h, V<a5>.8h, V<recip>.8h
    mls V<a5>.8h, V<quota5>.8h, V<modq>.8h
    sshr V<quota5>.8h, V<a5>.8h, #15
    and V<quota5>.16b, V<quota5>.16b, V<modq>.16b
    add V<a5>.8h, V<a5>.8h, V<quota5>.8h
    xtn V<lo5>.8b, V<a5>.8h
    mov V<L2>.d[1], V<lo5>.d[0]
    ushr V<hi5>.8h, V<a5>.8h, #8
    uzp1 V<he5>.8h, V<hi5>.8h, V<hi5>.8h
    uzp2 V<ho5>.8h, V<hi5>.8h, V<hi5>.8h
    sli V<he5>.8h, V<ho5>.8h, #4
    xtn V<hp5>.8b, V<he5>.8h
    ins V<H1>.h[2], V<hp5>.h[0]
    ins V<H1>.h[3], V<hp5>.h[1]
    sqrdmulh V<quota6>.8h, V<a6>.8h, V<recip>.8h
    mls V<a6>.8h, V<quota6>.8h, V<modq>.8h
    sshr V<quota6>.8h, V<a6>.8h, #15
    and V<quota6>.16b, V<quota6>.16b, V<modq>.16b
    add V<a6>.8h, V<a6>.8h, V<quota6>.8h
    xtn V<lo6>.8b, V<a6>.8h
    movi V<L3>.16b, #0
    mov V<L3>.d[0], V<lo6>.d[0]
    ushr V<hi6>.8h, V<a6>.8h, #8
    uzp1 V<he6>.8h, V<hi6>.8h, V<hi6>.8h
    uzp2 V<ho6>.8h, V<hi6>.8h, V<hi6>.8h
    sli V<he6>.8h, V<ho6>.8h, #4
    xtn V<hp6>.8b, V<he6>.8h
    ins V<H1>.h[4], V<hp6>.h[0]
    ins V<H1>.h[5], V<hp6>.h[1]
    sqrdmulh V<quota7>.8h, V<a7>.8h, V<recip>.8h
    mls V<a7>.8h, V<quota7>.8h, V<modq>.8h
    sshr V<quota7>.8h, V<a7>.8h, #15
    and V<quota7>.16b, V<quota7>.16b, V<modq>.16b
    add V<a7>.8h, V<a7>.8h, V<quota7>.8h
    xtn V<lo7>.8b, V<a7>.8h
    mov V<L3>.d[1], V<lo7>.d[0]
    ushr V<hi7>.8h, V<a7>.8h, #8
    uzp1 V<he7>.8h, V<hi7>.8h, V<hi7>.8h
    uzp2 V<ho7>.8h, V<hi7>.8h, V<hi7>.8h
    sli V<he7>.8h, V<ho7>.8h, #4
    xtn V<hp7>.8b, V<he7>.8h
    ins V<H1>.h[6], V<hp7>.h[0]
    ins V<H1>.h[7], V<hp7>.h[1]
    sqrdmulh V<quota8>.8h, V<a8>.8h, V<recip>.8h
    mls V<a8>.8h, V<quota8>.8h, V<modq>.8h
    sshr V<quota8>.8h, V<a8>.8h, #15
    and V<quota8>.16b, V<quota8>.16b, V<modq>.16b
    add V<a8>.8h, V<a8>.8h, V<quota8>.8h
    xtn V<lo8>.8b, V<a8>.8h
    movi V<L4>.16b, #0
    mov V<L4>.d[0], V<lo8>.d[0]
    ushr V<hi8>.8h, V<a8>.8h, #8
    uzp1 V<he8>.8h, V<hi8>.8h, V<hi8>.8h
    uzp2 V<ho8>.8h, V<hi8>.8h, V<hi8>.8h
    sli V<he8>.8h, V<ho8>.8h, #4
    xtn V<hp8>.8b, V<he8>.8h
    ins V<L4>.h[4], V<hp8>.h[0]
    ins V<L4>.h[5], V<hp8>.h[1]
    str Q<s0>, [x4, #0]
    str Q<s1>, [x4, #16]
    str Q<s2>, [x4, #32]
    str Q<s3>, [x4, #48]
    str Q<s4>, [x4, #64]
    str Q<s5>, [x4, #80]
    str Q<s6>, [x4, #96]
    str Q<s7>, [x4, #112]
    str Q<s8>, [x4, #128]
    str Q<s9>, [x4, #144]
    str Q<s10>, [x4, #160]
    str Q<s11>, [x4, #176]
    str Q<s12>, [x4, #192]
    str Q<L0>, [x4, #208]
    str Q<L1>, [x4, #224]
    str Q<L2>, [x4, #240]
    str Q<L3>, [x4, #256]
    str Q<L4>, [x4, #272]
    str Q<H0>, [x4, #288]
    str Q<H1>, [x4, #304]
gt864_p6d3_pack_a_slothy_end:
    ret

.global gt864_p6d3_route_b
gt864_p6d3_route_b:
// live-in: serialized frontier via x3, coefficient rows via x29, and fixed public tables via x30.
// live-out: exact next frontier via x4, or final canonical byte stream via the public output pointer.
// range: input coefficients are signed int16; normalized coefficients are 0..3456; packed lanes are bytes.
// reserved physical registers: x18 and sp; x29/x30 are intentionally fixed by the complete-function ABI.
gt864_p6d3_route_b_slothy_start:
    ldr Q<s0>, [x3, #0]
    ldr Q<s1>, [x3, #16]
    ldr Q<s2>, [x3, #32]
    ldr Q<s3>, [x3, #48]
    ldr Q<s4>, [x3, #64]
    ldr Q<s5>, [x3, #80]
    ldr Q<s6>, [x3, #96]
    ldr Q<s7>, [x3, #112]
    ldr Q<s8>, [x3, #128]
    ldr Q<s9>, [x3, #144]
    ldr Q<s10>, [x3, #160]
    ldr Q<s11>, [x3, #176]
    ldr Q<s12>, [x3, #192]
    ldr Q<L0>, [x3, #208]
    ldr Q<L1>, [x3, #224]
    ldr Q<L2>, [x3, #240]
    ldr Q<L3>, [x3, #256]
    ldr Q<L4>, [x3, #272]
    ldr Q<H0>, [x3, #288]
    ldr Q<H1>, [x3, #304]
    ldr Q<bj0>, [x29, #848]
    ldr Q<bj1>, [x29, #800]
    ext V<bj1>.16b, V<bj1>.16b, V<bj1>.16b, #14
    ldr Q<bj2>, [x29, #752]
    ext V<bj2>.16b, V<bj2>.16b, V<bj2>.16b, #12
    ldr Q<bj3>, [x29, #704]
    ext V<bj3>.16b, V<bj3>.16b, V<bj3>.16b, #10
    ldr Q<bj4>, [x29, #656]
    ext V<bj4>.16b, V<bj4>.16b, V<bj4>.16b, #8
    ldr Q<bj5>, [x29, #608]
    ext V<bj5>.16b, V<bj5>.16b, V<bj5>.16b, #6
    ldr Q<bj6>, [x29, #560]
    ext V<bj6>.16b, V<bj6>.16b, V<bj6>.16b, #4
    ldr Q<bj7>, [x29, #512]
    ext V<bj7>.16b, V<bj7>.16b, V<bj7>.16b, #2
    ldr Q<bninth>, [x29, #464]
    trn1 V<bu0>.8h, V<bj0>.8h, V<bj1>.8h
    trn2 V<bu1>.8h, V<bj0>.8h, V<bj1>.8h
    trn1 V<bu2>.8h, V<bj2>.8h, V<bj3>.8h
    trn2 V<bu3>.8h, V<bj2>.8h, V<bj3>.8h
    trn1 V<bu4>.8h, V<bj4>.8h, V<bj5>.8h
    trn2 V<bu5>.8h, V<bj4>.8h, V<bj5>.8h
    trn1 V<bu6>.8h, V<bj6>.8h, V<bj7>.8h
    trn2 V<bu7>.8h, V<bj6>.8h, V<bj7>.8h
    trn1 V<bz0>.4s, V<bu0>.4s, V<bu2>.4s
    trn2 V<bz2>.4s, V<bu0>.4s, V<bu2>.4s
    trn1 V<bz4>.4s, V<bu4>.4s, V<bu6>.4s
    trn2 V<bz6>.4s, V<bu4>.4s, V<bu6>.4s
    trn1 V<bz1>.4s, V<bu1>.4s, V<bu3>.4s
    trn2 V<bz3>.4s, V<bu1>.4s, V<bu3>.4s
    trn1 V<bz5>.4s, V<bu5>.4s, V<bu7>.4s
    trn2 V<bz7>.4s, V<bu5>.4s, V<bu7>.4s
    trn1 V<bt0>.2d, V<bz0>.2d, V<bz4>.2d
    trn2 V<bt4>.2d, V<bz0>.2d, V<bz4>.2d
    trn1 V<bt1>.2d, V<bz1>.2d, V<bz5>.2d
    trn2 V<bt5>.2d, V<bz1>.2d, V<bz5>.2d
    trn1 V<bt2>.2d, V<bz2>.2d, V<bz6>.2d
    trn2 V<bt6>.2d, V<bz2>.2d, V<bz6>.2d
    trn1 V<bt3>.2d, V<bz3>.2d, V<bz7>.2d
    trn2 V<bt7>.2d, V<bz3>.2d, V<bz7>.2d
    orr V<b0>.16b, V<bt0>.16b, V<bt0>.16b
    ins V<b0>.h[0], V<bninth>.h[0]
    ldr Q<bidx0>, [x30, #160]
    tbl V<b0>.16b, {V<b0>.16b}, V<bidx0>.16b
    ldr Q<bmask1>, [x30, #0]
    and V<b1>.16b, V<bt0>.16b, V<bmask1>.16b
    bic V<bother1>.16b, V<bt1>.16b, V<bmask1>.16b
    orr V<b1>.16b, V<b1>.16b, V<bother1>.16b
    ins V<b1>.h[1], V<bninth>.h[1]
    ldr Q<bidx1>, [x30, #176]
    tbl V<b1>.16b, {V<b1>.16b}, V<bidx1>.16b
    ldr Q<bmask2>, [x30, #16]
    and V<b2>.16b, V<bt1>.16b, V<bmask2>.16b
    bic V<bother2>.16b, V<bt2>.16b, V<bmask2>.16b
    orr V<b2>.16b, V<b2>.16b, V<bother2>.16b
    ins V<b2>.h[2], V<bninth>.h[2]
    ldr Q<bidx2>, [x30, #192]
    tbl V<b2>.16b, {V<b2>.16b}, V<bidx2>.16b
    ldr Q<bmask3>, [x30, #32]
    and V<b3>.16b, V<bt2>.16b, V<bmask3>.16b
    bic V<bother3>.16b, V<bt3>.16b, V<bmask3>.16b
    orr V<b3>.16b, V<b3>.16b, V<bother3>.16b
    ins V<b3>.h[3], V<bninth>.h[3]
    ldr Q<bidx3>, [x30, #208]
    tbl V<b3>.16b, {V<b3>.16b}, V<bidx3>.16b
    ldr Q<bmask4>, [x30, #48]
    and V<b4>.16b, V<bt3>.16b, V<bmask4>.16b
    bic V<bother4>.16b, V<bt4>.16b, V<bmask4>.16b
    orr V<b4>.16b, V<b4>.16b, V<bother4>.16b
    ins V<b4>.h[4], V<bninth>.h[4]
    ldr Q<bidx4>, [x30, #224]
    tbl V<b4>.16b, {V<b4>.16b}, V<bidx4>.16b
    ldr Q<bmask5>, [x30, #64]
    and V<b5>.16b, V<bt4>.16b, V<bmask5>.16b
    bic V<bother5>.16b, V<bt5>.16b, V<bmask5>.16b
    orr V<b5>.16b, V<b5>.16b, V<bother5>.16b
    ins V<b5>.h[5], V<bninth>.h[5]
    ldr Q<bidx5>, [x30, #240]
    tbl V<b5>.16b, {V<b5>.16b}, V<bidx5>.16b
    ldr Q<bmask6>, [x30, #80]
    and V<b6>.16b, V<bt5>.16b, V<bmask6>.16b
    bic V<bother6>.16b, V<bt6>.16b, V<bmask6>.16b
    orr V<b6>.16b, V<b6>.16b, V<bother6>.16b
    ins V<b6>.h[6], V<bninth>.h[6]
    ldr Q<bidx6>, [x30, #256]
    tbl V<b6>.16b, {V<b6>.16b}, V<bidx6>.16b
    orr V<b7>.16b, V<bt6>.16b, V<bt6>.16b
    ins V<b7>.h[7], V<bninth>.h[7]
    ldr Q<bidx7>, [x30, #272]
    tbl V<b7>.16b, {V<b7>.16b}, V<bidx7>.16b
    orr V<b8>.16b, V<bt7>.16b, V<bt7>.16b
    ldr Q<bidx8>, [x30, #288]
    tbl V<b8>.16b, {V<b8>.16b}, V<bidx8>.16b
    str Q<s0>, [x4, #0]
    str Q<s1>, [x4, #16]
    str Q<s2>, [x4, #32]
    str Q<s3>, [x4, #48]
    str Q<s4>, [x4, #64]
    str Q<s5>, [x4, #80]
    str Q<s6>, [x4, #96]
    str Q<s7>, [x4, #112]
    str Q<s8>, [x4, #128]
    str Q<s9>, [x4, #144]
    str Q<s10>, [x4, #160]
    str Q<s11>, [x4, #176]
    str Q<s12>, [x4, #192]
    str Q<L0>, [x4, #208]
    str Q<L1>, [x4, #224]
    str Q<L2>, [x4, #240]
    str Q<L3>, [x4, #256]
    str Q<L4>, [x4, #272]
    str Q<H0>, [x4, #288]
    str Q<H1>, [x4, #304]
    str Q<b0>, [x4, #320]
    str Q<b1>, [x4, #336]
    str Q<b2>, [x4, #352]
    str Q<b3>, [x4, #368]
    str Q<b4>, [x4, #384]
    str Q<b5>, [x4, #400]
    str Q<b6>, [x4, #416]
    str Q<b7>, [x4, #432]
    str Q<b8>, [x4, #448]
gt864_p6d3_route_b_slothy_end:
    ret

.global gt864_p6d3_row0
gt864_p6d3_row0:
// live-in: serialized frontier via x3, coefficient rows via x29, and fixed public tables via x30.
// live-out: exact next frontier via x4, or final canonical byte stream via the public output pointer.
// range: input coefficients are signed int16; normalized coefficients are 0..3456; packed lanes are bytes.
// reserved physical registers: x18 and sp; x29/x30 are intentionally fixed by the complete-function ABI.
gt864_p6d3_row0_slothy_start:
    ldr Q<s0>, [x3, #0]
    ldr Q<s1>, [x3, #16]
    ldr Q<s2>, [x3, #32]
    ldr Q<s3>, [x3, #48]
    ldr Q<s4>, [x3, #64]
    ldr Q<s5>, [x3, #80]
    ldr Q<s6>, [x3, #96]
    ldr Q<s7>, [x3, #112]
    ldr Q<s8>, [x3, #128]
    ldr Q<s9>, [x3, #144]
    ldr Q<s10>, [x3, #160]
    ldr Q<s11>, [x3, #176]
    ldr Q<s12>, [x3, #192]
    ldr Q<L0>, [x3, #208]
    ldr Q<L1>, [x3, #224]
    ldr Q<L2>, [x3, #240]
    ldr Q<L3>, [x3, #256]
    ldr Q<L4>, [x3, #272]
    ldr Q<H0>, [x3, #288]
    ldr Q<H1>, [x3, #304]
    ldr Q<b0>, [x3, #320]
    ldr Q<b1>, [x3, #336]
    ldr Q<b2>, [x3, #352]
    ldr Q<b3>, [x3, #368]
    ldr Q<b4>, [x3, #384]
    ldr Q<b5>, [x3, #400]
    ldr Q<b6>, [x3, #416]
    ldr Q<b7>, [x3, #432]
    ldr Q<b8>, [x3, #448]
    ldr Q<modq>, [x30, #336]
    ldr Q<recip>, [x30, #352]
    sqrdmulh V<quotb0>.8h, V<b0>.8h, V<recip>.8h
    mls V<b0>.8h, V<quotb0>.8h, V<modq>.8h
    sshr V<quotb0>.8h, V<b0>.8h, #15
    and V<quotb0>.16b, V<quotb0>.16b, V<modq>.16b
    add V<b0>.8h, V<b0>.8h, V<quotb0>.8h
    eor V<modq>.16b, V<modq>.16b, V<modq>.16b
    sli V<modq>.8h, V<b0>.8h, #4
    xtn V<bmid>.8b, V<modq>.8h
    ushr V<bhighh>.8h, V<b0>.8h, #4
    xtn V<bhigh>.8b, V<bhighh>.8h
    ldr Q<nibble>, [x30, #608]
    and V<ahlo>.16b, V<H0>.16b, V<nibble>.16b
    ushr V<ahhi>.16b, V<H0>.16b, #4
    zip1 V<ahi>.16b, V<ahlo>.16b, V<ahhi>.16b
    orr V<bmid>.8b, V<bmid>.8b, V<ahi>.8b
    ldr Q<p0_0>, [x30, #368]
    tbl V<p0_0>.16b, {V<s0>.16b, V<s1>.16b}, V<p0_0>.16b
    ldr Q<p1_0>, [x30, #384]
    tbl V<p1_0>.16b, {V<s1>.16b, V<s2>.16b}, V<p1_0>.16b
    orr V<p0_0>.16b, V<p0_0>.16b, V<p1_0>.16b
    ldr Q<p2_0>, [x30, #400]
    tbl V<p2_0>.16b, {V<L0>.16b, V<bmid>.16b, V<bhigh>.16b}, V<p2_0>.16b
    orr V<p0_0>.16b, V<p0_0>.16b, V<p2_0>.16b
    str Q<p0_0>, [x29, #0]
    ldr Q<p0_1>, [x30, #416]
    tbl V<p0_1>.16b, {V<s0>.16b, V<s1>.16b}, V<p0_1>.16b
    ldr Q<p1_1>, [x30, #432]
    tbl V<p1_1>.16b, {V<s1>.16b, V<s2>.16b}, V<p1_1>.16b
    orr V<p0_1>.16b, V<p0_1>.16b, V<p1_1>.16b
    ldr Q<p2_1>, [x30, #448]
    tbl V<p2_1>.16b, {V<L0>.16b, V<bmid>.16b, V<bhigh>.16b}, V<p2_1>.16b
    orr V<p0_1>.16b, V<p0_1>.16b, V<p2_1>.16b
    str Q<p0_1>, [x29, #16]
    ldr Q<p0_2>, [x30, #464]
    tbl V<p0_2>.16b, {V<s0>.16b, V<s1>.16b}, V<p0_2>.16b
    ldr Q<p1_2>, [x30, #480]
    tbl V<p1_2>.16b, {V<s1>.16b, V<s2>.16b}, V<p1_2>.16b
    orr V<p0_2>.16b, V<p0_2>.16b, V<p1_2>.16b
    ldr Q<p2_2>, [x30, #496]
    tbl V<p2_2>.16b, {V<L0>.16b, V<bmid>.16b, V<bhigh>.16b}, V<p2_2>.16b
    orr V<p0_2>.16b, V<p0_2>.16b, V<p2_2>.16b
    str Q<p0_2>, [x29, #32]
    ldr Q<p0_3>, [x30, #512]
    tbl V<p0_3>.16b, {V<s0>.16b, V<s1>.16b}, V<p0_3>.16b
    ldr Q<p1_3>, [x30, #528]
    tbl V<p1_3>.16b, {V<s1>.16b, V<s2>.16b}, V<p1_3>.16b
    orr V<p0_3>.16b, V<p0_3>.16b, V<p1_3>.16b
    ldr Q<p2_3>, [x30, #544]
    tbl V<p2_3>.16b, {V<L0>.16b, V<bmid>.16b, V<bhigh>.16b}, V<p2_3>.16b
    orr V<p0_3>.16b, V<p0_3>.16b, V<p2_3>.16b
    str Q<p0_3>, [x29, #48]
    ldr Q<carry>, [x30, #560]
    tbl V<carry>.16b, {V<s0>.16b, V<s1>.16b}, V<carry>.16b
    ldr Q<p1_4>, [x30, #576]
    tbl V<p1_4>.16b, {V<s1>.16b, V<s2>.16b}, V<p1_4>.16b
    orr V<carry>.16b, V<carry>.16b, V<p1_4>.16b
    ldr Q<p2_4>, [x30, #592]
    tbl V<p2_4>.16b, {V<L0>.16b, V<bmid>.16b, V<bhigh>.16b}, V<p2_4>.16b
    orr V<carry>.16b, V<carry>.16b, V<p2_4>.16b
    str Q<s3>, [x4, #0]
    str Q<s4>, [x4, #16]
    str Q<s5>, [x4, #32]
    str Q<s6>, [x4, #48]
    str Q<s7>, [x4, #64]
    str Q<s8>, [x4, #80]
    str Q<s9>, [x4, #96]
    str Q<s10>, [x4, #112]
    str Q<s11>, [x4, #128]
    str Q<s12>, [x4, #144]
    str Q<L0>, [x4, #160]
    str Q<L1>, [x4, #176]
    str Q<L2>, [x4, #192]
    str Q<L3>, [x4, #208]
    str Q<L4>, [x4, #224]
    str Q<H0>, [x4, #240]
    str Q<H1>, [x4, #256]
    str Q<b1>, [x4, #272]
    str Q<b2>, [x4, #288]
    str Q<b3>, [x4, #304]
    str Q<b4>, [x4, #320]
    str Q<b5>, [x4, #336]
    str Q<b6>, [x4, #352]
    str Q<b7>, [x4, #368]
    str Q<b8>, [x4, #384]
    str Q<carry>, [x4, #400]
gt864_p6d3_row0_slothy_end:
    ret

.global gt864_p6d3_row1
gt864_p6d3_row1:
// live-in: serialized frontier via x3, coefficient rows via x29, and fixed public tables via x30.
// live-out: exact next frontier via x4, or final canonical byte stream via the public output pointer.
// range: input coefficients are signed int16; normalized coefficients are 0..3456; packed lanes are bytes.
// reserved physical registers: x18 and sp; x29/x30 are intentionally fixed by the complete-function ABI.
gt864_p6d3_row1_slothy_start:
    ldr Q<s3>, [x3, #0]
    ldr Q<s4>, [x3, #16]
    ldr Q<s5>, [x3, #32]
    ldr Q<s6>, [x3, #48]
    ldr Q<s7>, [x3, #64]
    ldr Q<s8>, [x3, #80]
    ldr Q<s9>, [x3, #96]
    ldr Q<s10>, [x3, #112]
    ldr Q<s11>, [x3, #128]
    ldr Q<s12>, [x3, #144]
    ldr Q<L0>, [x3, #160]
    ldr Q<L1>, [x3, #176]
    ldr Q<L2>, [x3, #192]
    ldr Q<L3>, [x3, #208]
    ldr Q<L4>, [x3, #224]
    ldr Q<H0>, [x3, #240]
    ldr Q<H1>, [x3, #256]
    ldr Q<b1>, [x3, #272]
    ldr Q<b2>, [x3, #288]
    ldr Q<b3>, [x3, #304]
    ldr Q<b4>, [x3, #320]
    ldr Q<b5>, [x3, #336]
    ldr Q<b6>, [x3, #352]
    ldr Q<b7>, [x3, #368]
    ldr Q<b8>, [x3, #384]
    ldr Q<carry>, [x3, #400]
    ldr Q<modq>, [x30, #336]
    ldr Q<recip>, [x30, #352]
    sqrdmulh V<quotb3>.8h, V<b3>.8h, V<recip>.8h
    mls V<b3>.8h, V<quotb3>.8h, V<modq>.8h
    sshr V<quotb3>.8h, V<b3>.8h, #15
    and V<quotb3>.16b, V<quotb3>.16b, V<modq>.16b
    add V<b3>.8h, V<b3>.8h, V<quotb3>.8h
    eor V<modq>.16b, V<modq>.16b, V<modq>.16b
    sli V<modq>.8h, V<b3>.8h, #4
    xtn V<bmid>.8b, V<modq>.8h
    ushr V<bhighh>.8h, V<b3>.8h, #4
    xtn V<bhigh>.8b, V<bhighh>.8h
    ext V<alow>.16b, V<L1>.16b, V<L1>.16b, #8
    ext V<ahsrc>.16b, V<H0>.16b, V<H0>.16b, #12
    ldr Q<nibble>, [x30, #608]
    and V<ahlo>.16b, V<ahsrc>.16b, V<nibble>.16b
    ushr V<ahhi>.16b, V<ahsrc>.16b, #4
    zip1 V<ahi>.16b, V<ahlo>.16b, V<ahhi>.16b
    orr V<bmid>.8b, V<bmid>.8b, V<ahi>.8b
    ldr Q<p0_0>, [x30, #368]
    tbl V<p0_0>.16b, {V<s3>.16b, V<s4>.16b}, V<p0_0>.16b
    ldr Q<p1_0>, [x30, #384]
    tbl V<p1_0>.16b, {V<s4>.16b, V<s5>.16b}, V<p1_0>.16b
    orr V<p0_0>.16b, V<p0_0>.16b, V<p1_0>.16b
    ldr Q<p2_0>, [x30, #400]
    tbl V<p2_0>.16b, {V<alow>.16b, V<bmid>.16b, V<bhigh>.16b}, V<p2_0>.16b
    orr V<p0_0>.16b, V<p0_0>.16b, V<p2_0>.16b
    movi V<stream_0>.16b, #0
    mov V<stream_0>.d[0], V<carry>.d[0]
    mov V<stream_0>.d[1], V<p0_0>.d[0]
    str Q<stream_0>, [x29, #0]
    ldr Q<p0_1>, [x30, #416]
    tbl V<p0_1>.16b, {V<s3>.16b, V<s4>.16b}, V<p0_1>.16b
    ldr Q<p1_1>, [x30, #432]
    tbl V<p1_1>.16b, {V<s4>.16b, V<s5>.16b}, V<p1_1>.16b
    orr V<p0_1>.16b, V<p0_1>.16b, V<p1_1>.16b
    ldr Q<p2_1>, [x30, #448]
    tbl V<p2_1>.16b, {V<alow>.16b, V<bmid>.16b, V<bhigh>.16b}, V<p2_1>.16b
    orr V<p0_1>.16b, V<p0_1>.16b, V<p2_1>.16b
    movi V<stream_1>.16b, #0
    mov V<stream_1>.d[0], V<p0_0>.d[1]
    mov V<stream_1>.d[1], V<p0_1>.d[0]
    str Q<stream_1>, [x29, #16]
    ldr Q<p0_2>, [x30, #464]
    tbl V<p0_2>.16b, {V<s3>.16b, V<s4>.16b}, V<p0_2>.16b
    ldr Q<p1_2>, [x30, #480]
    tbl V<p1_2>.16b, {V<s4>.16b, V<s5>.16b}, V<p1_2>.16b
    orr V<p0_2>.16b, V<p0_2>.16b, V<p1_2>.16b
    ldr Q<p2_2>, [x30, #496]
    tbl V<p2_2>.16b, {V<alow>.16b, V<bmid>.16b, V<bhigh>.16b}, V<p2_2>.16b
    orr V<p0_2>.16b, V<p0_2>.16b, V<p2_2>.16b
    movi V<stream_2>.16b, #0
    mov V<stream_2>.d[0], V<p0_1>.d[1]
    mov V<stream_2>.d[1], V<p0_2>.d[0]
    str Q<stream_2>, [x29, #32]
    ldr Q<p0_3>, [x30, #512]
    tbl V<p0_3>.16b, {V<s3>.16b, V<s4>.16b}, V<p0_3>.16b
    ldr Q<p1_3>, [x30, #528]
    tbl V<p1_3>.16b, {V<s4>.16b, V<s5>.16b}, V<p1_3>.16b
    orr V<p0_3>.16b, V<p0_3>.16b, V<p1_3>.16b
    ldr Q<p2_3>, [x30, #544]
    tbl V<p2_3>.16b, {V<alow>.16b, V<bmid>.16b, V<bhigh>.16b}, V<p2_3>.16b
    orr V<p0_3>.16b, V<p0_3>.16b, V<p2_3>.16b
    movi V<stream_3>.16b, #0
    mov V<stream_3>.d[0], V<p0_2>.d[1]
    mov V<stream_3>.d[1], V<p0_3>.d[0]
    str Q<stream_3>, [x29, #48]
    ldr Q<p0_4>, [x30, #560]
    tbl V<p0_4>.16b, {V<s3>.16b, V<s4>.16b}, V<p0_4>.16b
    ldr Q<p1_4>, [x30, #576]
    tbl V<p1_4>.16b, {V<s4>.16b, V<s5>.16b}, V<p1_4>.16b
    orr V<p0_4>.16b, V<p0_4>.16b, V<p1_4>.16b
    ldr Q<p2_4>, [x30, #592]
    tbl V<p2_4>.16b, {V<alow>.16b, V<bmid>.16b, V<bhigh>.16b}, V<p2_4>.16b
    orr V<p0_4>.16b, V<p0_4>.16b, V<p2_4>.16b
    movi V<stream_4>.16b, #0
    mov V<stream_4>.d[0], V<p0_3>.d[1]
    mov V<stream_4>.d[1], V<p0_4>.d[0]
    str Q<stream_4>, [x29, #64]
    str Q<s6>, [x4, #0]
    str Q<s7>, [x4, #16]
    str Q<s8>, [x4, #32]
    str Q<s9>, [x4, #48]
    str Q<s10>, [x4, #64]
    str Q<s11>, [x4, #80]
    str Q<s12>, [x4, #96]
    str Q<L0>, [x4, #112]
    str Q<L1>, [x4, #128]
    str Q<L2>, [x4, #144]
    str Q<L3>, [x4, #160]
    str Q<L4>, [x4, #176]
    str Q<H0>, [x4, #192]
    str Q<H1>, [x4, #208]
    str Q<b1>, [x4, #224]
    str Q<b2>, [x4, #240]
    str Q<b4>, [x4, #256]
    str Q<b5>, [x4, #272]
    str Q<b6>, [x4, #288]
    str Q<b7>, [x4, #304]
    str Q<b8>, [x4, #320]
gt864_p6d3_row1_slothy_end:
    ret

.global gt864_p6d3_row2
gt864_p6d3_row2:
// live-in: serialized frontier via x3, coefficient rows via x29, and fixed public tables via x30.
// live-out: exact next frontier via x4, or final canonical byte stream via the public output pointer.
// range: input coefficients are signed int16; normalized coefficients are 0..3456; packed lanes are bytes.
// reserved physical registers: x18 and sp; x29/x30 are intentionally fixed by the complete-function ABI.
gt864_p6d3_row2_slothy_start:
    ldr Q<s6>, [x3, #0]
    ldr Q<s7>, [x3, #16]
    ldr Q<s8>, [x3, #32]
    ldr Q<s9>, [x3, #48]
    ldr Q<s10>, [x3, #64]
    ldr Q<s11>, [x3, #80]
    ldr Q<s12>, [x3, #96]
    ldr Q<L0>, [x3, #112]
    ldr Q<L1>, [x3, #128]
    ldr Q<L2>, [x3, #144]
    ldr Q<L3>, [x3, #160]
    ldr Q<L4>, [x3, #176]
    ldr Q<H0>, [x3, #192]
    ldr Q<H1>, [x3, #208]
    ldr Q<b1>, [x3, #224]
    ldr Q<b2>, [x3, #240]
    ldr Q<b4>, [x3, #256]
    ldr Q<b5>, [x3, #272]
    ldr Q<b6>, [x3, #288]
    ldr Q<b7>, [x3, #304]
    ldr Q<b8>, [x3, #320]
    ldr Q<modq>, [x30, #336]
    ldr Q<recip>, [x30, #352]
    sqrdmulh V<quotb6>.8h, V<b6>.8h, V<recip>.8h
    mls V<b6>.8h, V<quotb6>.8h, V<modq>.8h
    sshr V<quotb6>.8h, V<b6>.8h, #15
    and V<quotb6>.16b, V<quotb6>.16b, V<modq>.16b
    add V<b6>.8h, V<b6>.8h, V<quotb6>.8h
    eor V<modq>.16b, V<modq>.16b, V<modq>.16b
    sli V<modq>.8h, V<b6>.8h, #4
    xtn V<bmid>.8b, V<modq>.8h
    ushr V<bhighh>.8h, V<b6>.8h, #4
    xtn V<bhigh>.8b, V<bhighh>.8h
    ext V<ahsrc>.16b, V<H1>.16b, V<H1>.16b, #8
    ldr Q<nibble>, [x30, #608]
    and V<ahlo>.16b, V<ahsrc>.16b, V<nibble>.16b
    ushr V<ahhi>.16b, V<ahsrc>.16b, #4
    zip1 V<ahi>.16b, V<ahlo>.16b, V<ahhi>.16b
    orr V<bmid>.8b, V<bmid>.8b, V<ahi>.8b
    ldr Q<p0_0>, [x30, #368]
    tbl V<p0_0>.16b, {V<s6>.16b, V<s7>.16b}, V<p0_0>.16b
    ldr Q<p1_0>, [x30, #384]
    tbl V<p1_0>.16b, {V<s7>.16b, V<s8>.16b}, V<p1_0>.16b
    orr V<p0_0>.16b, V<p0_0>.16b, V<p1_0>.16b
    ldr Q<p2_0>, [x30, #400]
    tbl V<p2_0>.16b, {V<L3>.16b, V<bmid>.16b, V<bhigh>.16b}, V<p2_0>.16b
    orr V<p0_0>.16b, V<p0_0>.16b, V<p2_0>.16b
    str Q<p0_0>, [x29, #0]
    ldr Q<p0_1>, [x30, #416]
    tbl V<p0_1>.16b, {V<s6>.16b, V<s7>.16b}, V<p0_1>.16b
    ldr Q<p1_1>, [x30, #432]
    tbl V<p1_1>.16b, {V<s7>.16b, V<s8>.16b}, V<p1_1>.16b
    orr V<p0_1>.16b, V<p0_1>.16b, V<p1_1>.16b
    ldr Q<p2_1>, [x30, #448]
    tbl V<p2_1>.16b, {V<L3>.16b, V<bmid>.16b, V<bhigh>.16b}, V<p2_1>.16b
    orr V<p0_1>.16b, V<p0_1>.16b, V<p2_1>.16b
    str Q<p0_1>, [x29, #16]
    ldr Q<p0_2>, [x30, #464]
    tbl V<p0_2>.16b, {V<s6>.16b, V<s7>.16b}, V<p0_2>.16b
    ldr Q<p1_2>, [x30, #480]
    tbl V<p1_2>.16b, {V<s7>.16b, V<s8>.16b}, V<p1_2>.16b
    orr V<p0_2>.16b, V<p0_2>.16b, V<p1_2>.16b
    ldr Q<p2_2>, [x30, #496]
    tbl V<p2_2>.16b, {V<L3>.16b, V<bmid>.16b, V<bhigh>.16b}, V<p2_2>.16b
    orr V<p0_2>.16b, V<p0_2>.16b, V<p2_2>.16b
    str Q<p0_2>, [x29, #32]
    ldr Q<p0_3>, [x30, #512]
    tbl V<p0_3>.16b, {V<s6>.16b, V<s7>.16b}, V<p0_3>.16b
    ldr Q<p1_3>, [x30, #528]
    tbl V<p1_3>.16b, {V<s7>.16b, V<s8>.16b}, V<p1_3>.16b
    orr V<p0_3>.16b, V<p0_3>.16b, V<p1_3>.16b
    ldr Q<p2_3>, [x30, #544]
    tbl V<p2_3>.16b, {V<L3>.16b, V<bmid>.16b, V<bhigh>.16b}, V<p2_3>.16b
    orr V<p0_3>.16b, V<p0_3>.16b, V<p2_3>.16b
    str Q<p0_3>, [x29, #48]
    ldr Q<carry>, [x30, #560]
    tbl V<carry>.16b, {V<s6>.16b, V<s7>.16b}, V<carry>.16b
    ldr Q<p1_4>, [x30, #576]
    tbl V<p1_4>.16b, {V<s7>.16b, V<s8>.16b}, V<p1_4>.16b
    orr V<carry>.16b, V<carry>.16b, V<p1_4>.16b
    ldr Q<p2_4>, [x30, #592]
    tbl V<p2_4>.16b, {V<L3>.16b, V<bmid>.16b, V<bhigh>.16b}, V<p2_4>.16b
    orr V<carry>.16b, V<carry>.16b, V<p2_4>.16b
    str Q<s9>, [x4, #0]
    str Q<s10>, [x4, #16]
    str Q<s11>, [x4, #32]
    str Q<s12>, [x4, #48]
    str Q<L0>, [x4, #64]
    str Q<L1>, [x4, #80]
    str Q<L2>, [x4, #96]
    str Q<L3>, [x4, #112]
    str Q<L4>, [x4, #128]
    str Q<H0>, [x4, #144]
    str Q<H1>, [x4, #160]
    str Q<b1>, [x4, #176]
    str Q<b2>, [x4, #192]
    str Q<b4>, [x4, #208]
    str Q<b5>, [x4, #224]
    str Q<b7>, [x4, #240]
    str Q<b8>, [x4, #256]
    str Q<carry>, [x4, #272]
gt864_p6d3_row2_slothy_end:
    ret

.global gt864_p6d3_row3
gt864_p6d3_row3:
// live-in: serialized frontier via x3, coefficient rows via x29, and fixed public tables via x30.
// live-out: exact next frontier via x4, or final canonical byte stream via the public output pointer.
// range: input coefficients are signed int16; normalized coefficients are 0..3456; packed lanes are bytes.
// reserved physical registers: x18 and sp; x29/x30 are intentionally fixed by the complete-function ABI.
gt864_p6d3_row3_slothy_start:
    ldr Q<s9>, [x3, #0]
    ldr Q<s10>, [x3, #16]
    ldr Q<s11>, [x3, #32]
    ldr Q<s12>, [x3, #48]
    ldr Q<L0>, [x3, #64]
    ldr Q<L1>, [x3, #80]
    ldr Q<L2>, [x3, #96]
    ldr Q<L3>, [x3, #112]
    ldr Q<L4>, [x3, #128]
    ldr Q<H0>, [x3, #144]
    ldr Q<H1>, [x3, #160]
    ldr Q<b1>, [x3, #176]
    ldr Q<b2>, [x3, #192]
    ldr Q<b4>, [x3, #208]
    ldr Q<b5>, [x3, #224]
    ldr Q<b7>, [x3, #240]
    ldr Q<b8>, [x3, #256]
    ldr Q<carry>, [x3, #272]
    ldr Q<modq>, [x30, #336]
    ldr Q<recip>, [x30, #352]
    sqrdmulh V<quotb1>.8h, V<b1>.8h, V<recip>.8h
    mls V<b1>.8h, V<quotb1>.8h, V<modq>.8h
    sshr V<quotb1>.8h, V<b1>.8h, #15
    and V<quotb1>.16b, V<quotb1>.16b, V<modq>.16b
    add V<b1>.8h, V<b1>.8h, V<quotb1>.8h
    eor V<modq>.16b, V<modq>.16b, V<modq>.16b
    sli V<modq>.8h, V<b1>.8h, #4
    xtn V<bmid>.8b, V<modq>.8h
    ushr V<bhighh>.8h, V<b1>.8h, #4
    xtn V<bhigh>.8b, V<bhighh>.8h
    ext V<alow>.16b, V<L0>.16b, V<L0>.16b, #8
    ext V<ahsrc>.16b, V<H0>.16b, V<H0>.16b, #4
    ldr Q<nibble>, [x30, #608]
    and V<ahlo>.16b, V<ahsrc>.16b, V<nibble>.16b
    ushr V<ahhi>.16b, V<ahsrc>.16b, #4
    zip1 V<ahi>.16b, V<ahlo>.16b, V<ahhi>.16b
    orr V<bmid>.8b, V<bmid>.8b, V<ahi>.8b
    ldr Q<p0_0>, [x30, #368]
    tbl V<p0_0>.16b, {V<s9>.16b, V<s10>.16b}, V<p0_0>.16b
    ldr Q<p1_0>, [x30, #384]
    tbl V<p1_0>.16b, {V<s10>.16b, V<s11>.16b}, V<p1_0>.16b
    orr V<p0_0>.16b, V<p0_0>.16b, V<p1_0>.16b
    ldr Q<p2_0>, [x30, #400]
    tbl V<p2_0>.16b, {V<alow>.16b, V<bmid>.16b, V<bhigh>.16b}, V<p2_0>.16b
    orr V<p0_0>.16b, V<p0_0>.16b, V<p2_0>.16b
    movi V<stream_0>.16b, #0
    mov V<stream_0>.d[0], V<carry>.d[0]
    mov V<stream_0>.d[1], V<p0_0>.d[0]
    str Q<stream_0>, [x29, #0]
    ldr Q<p0_1>, [x30, #416]
    tbl V<p0_1>.16b, {V<s9>.16b, V<s10>.16b}, V<p0_1>.16b
    ldr Q<p1_1>, [x30, #432]
    tbl V<p1_1>.16b, {V<s10>.16b, V<s11>.16b}, V<p1_1>.16b
    orr V<p0_1>.16b, V<p0_1>.16b, V<p1_1>.16b
    ldr Q<p2_1>, [x30, #448]
    tbl V<p2_1>.16b, {V<alow>.16b, V<bmid>.16b, V<bhigh>.16b}, V<p2_1>.16b
    orr V<p0_1>.16b, V<p0_1>.16b, V<p2_1>.16b
    movi V<stream_1>.16b, #0
    mov V<stream_1>.d[0], V<p0_0>.d[1]
    mov V<stream_1>.d[1], V<p0_1>.d[0]
    str Q<stream_1>, [x29, #16]
    ldr Q<p0_2>, [x30, #464]
    tbl V<p0_2>.16b, {V<s9>.16b, V<s10>.16b}, V<p0_2>.16b
    ldr Q<p1_2>, [x30, #480]
    tbl V<p1_2>.16b, {V<s10>.16b, V<s11>.16b}, V<p1_2>.16b
    orr V<p0_2>.16b, V<p0_2>.16b, V<p1_2>.16b
    ldr Q<p2_2>, [x30, #496]
    tbl V<p2_2>.16b, {V<alow>.16b, V<bmid>.16b, V<bhigh>.16b}, V<p2_2>.16b
    orr V<p0_2>.16b, V<p0_2>.16b, V<p2_2>.16b
    movi V<stream_2>.16b, #0
    mov V<stream_2>.d[0], V<p0_1>.d[1]
    mov V<stream_2>.d[1], V<p0_2>.d[0]
    str Q<stream_2>, [x29, #32]
    ldr Q<p0_3>, [x30, #512]
    tbl V<p0_3>.16b, {V<s9>.16b, V<s10>.16b}, V<p0_3>.16b
    ldr Q<p1_3>, [x30, #528]
    tbl V<p1_3>.16b, {V<s10>.16b, V<s11>.16b}, V<p1_3>.16b
    orr V<p0_3>.16b, V<p0_3>.16b, V<p1_3>.16b
    ldr Q<p2_3>, [x30, #544]
    tbl V<p2_3>.16b, {V<alow>.16b, V<bmid>.16b, V<bhigh>.16b}, V<p2_3>.16b
    orr V<p0_3>.16b, V<p0_3>.16b, V<p2_3>.16b
    movi V<stream_3>.16b, #0
    mov V<stream_3>.d[0], V<p0_2>.d[1]
    mov V<stream_3>.d[1], V<p0_3>.d[0]
    str Q<stream_3>, [x29, #48]
    ldr Q<p0_4>, [x30, #560]
    tbl V<p0_4>.16b, {V<s9>.16b, V<s10>.16b}, V<p0_4>.16b
    ldr Q<p1_4>, [x30, #576]
    tbl V<p1_4>.16b, {V<s10>.16b, V<s11>.16b}, V<p1_4>.16b
    orr V<p0_4>.16b, V<p0_4>.16b, V<p1_4>.16b
    ldr Q<p2_4>, [x30, #592]
    tbl V<p2_4>.16b, {V<alow>.16b, V<bmid>.16b, V<bhigh>.16b}, V<p2_4>.16b
    orr V<p0_4>.16b, V<p0_4>.16b, V<p2_4>.16b
    movi V<stream_4>.16b, #0
    mov V<stream_4>.d[0], V<p0_3>.d[1]
    mov V<stream_4>.d[1], V<p0_4>.d[0]
    str Q<stream_4>, [x29, #64]
    str Q<s12>, [x4, #0]
    str Q<L1>, [x4, #16]
    str Q<L2>, [x4, #32]
    str Q<L3>, [x4, #48]
    str Q<L4>, [x4, #64]
    str Q<H0>, [x4, #80]
    str Q<H1>, [x4, #96]
    str Q<b2>, [x4, #112]
    str Q<b4>, [x4, #128]
    str Q<b5>, [x4, #144]
    str Q<b7>, [x4, #160]
    str Q<b8>, [x4, #176]
gt864_p6d3_row3_slothy_end:
    ret

.global gt864_p6d3_row4
gt864_p6d3_row4:
// live-in: serialized frontier via x3, coefficient rows via x29, and fixed public tables via x30.
// live-out: exact next frontier via x4, or final canonical byte stream via the public output pointer.
// range: input coefficients are signed int16; normalized coefficients are 0..3456; packed lanes are bytes.
// reserved physical registers: x18 and sp; x29/x30 are intentionally fixed by the complete-function ABI.
gt864_p6d3_row4_slothy_start:
    ldr Q<s12>, [x3, #0]
    ldr Q<L1>, [x3, #16]
    ldr Q<L2>, [x3, #32]
    ldr Q<L3>, [x3, #48]
    ldr Q<L4>, [x3, #64]
    ldr Q<H0>, [x3, #80]
    ldr Q<H1>, [x3, #96]
    ldr Q<b2>, [x3, #112]
    ldr Q<b4>, [x3, #128]
    ldr Q<b5>, [x3, #144]
    ldr Q<b7>, [x3, #160]
    ldr Q<b8>, [x3, #176]
    movi V<rowq1>.16b, #0
    mov V<rowq1>.d[0], x17
    mov V<rowq1>.d[1], x7
    movi V<rowq2>.16b, #0
    mov V<rowq2>.d[0], x9
    mov V<rowq2>.d[1], x16
    ldr Q<modq>, [x30, #336]
    ldr Q<recip>, [x30, #352]
    sqrdmulh V<quotb4>.8h, V<b4>.8h, V<recip>.8h
    mls V<b4>.8h, V<quotb4>.8h, V<modq>.8h
    sshr V<quotb4>.8h, V<b4>.8h, #15
    and V<quotb4>.16b, V<quotb4>.16b, V<modq>.16b
    add V<b4>.8h, V<b4>.8h, V<quotb4>.8h
    eor V<modq>.16b, V<modq>.16b, V<modq>.16b
    sli V<modq>.8h, V<b4>.8h, #4
    xtn V<bmid>.8b, V<modq>.8h
    ushr V<bhighh>.8h, V<b4>.8h, #4
    xtn V<bhigh>.8b, V<bhighh>.8h
    ldr Q<nibble>, [x30, #608]
    and V<ahlo>.16b, V<H1>.16b, V<nibble>.16b
    ushr V<ahhi>.16b, V<H1>.16b, #4
    zip1 V<ahi>.16b, V<ahlo>.16b, V<ahhi>.16b
    orr V<bmid>.8b, V<bmid>.8b, V<ahi>.8b
    ldr Q<p0_0>, [x30, #368]
    tbl V<p0_0>.16b, {V<s12>.16b, V<rowq1>.16b}, V<p0_0>.16b
    ldr Q<p1_0>, [x30, #384]
    tbl V<p1_0>.16b, {V<rowq1>.16b, V<rowq2>.16b}, V<p1_0>.16b
    orr V<p0_0>.16b, V<p0_0>.16b, V<p1_0>.16b
    ldr Q<p2_0>, [x30, #400]
    tbl V<p2_0>.16b, {V<L2>.16b, V<bmid>.16b, V<bhigh>.16b}, V<p2_0>.16b
    orr V<p0_0>.16b, V<p0_0>.16b, V<p2_0>.16b
    str Q<p0_0>, [x29, #0]
    ldr Q<p0_1>, [x30, #416]
    tbl V<p0_1>.16b, {V<s12>.16b, V<rowq1>.16b}, V<p0_1>.16b
    ldr Q<p1_1>, [x30, #432]
    tbl V<p1_1>.16b, {V<rowq1>.16b, V<rowq2>.16b}, V<p1_1>.16b
    orr V<p0_1>.16b, V<p0_1>.16b, V<p1_1>.16b
    ldr Q<p2_1>, [x30, #448]
    tbl V<p2_1>.16b, {V<L2>.16b, V<bmid>.16b, V<bhigh>.16b}, V<p2_1>.16b
    orr V<p0_1>.16b, V<p0_1>.16b, V<p2_1>.16b
    str Q<p0_1>, [x29, #16]
    ldr Q<p0_2>, [x30, #464]
    tbl V<p0_2>.16b, {V<s12>.16b, V<rowq1>.16b}, V<p0_2>.16b
    ldr Q<p1_2>, [x30, #480]
    tbl V<p1_2>.16b, {V<rowq1>.16b, V<rowq2>.16b}, V<p1_2>.16b
    orr V<p0_2>.16b, V<p0_2>.16b, V<p1_2>.16b
    ldr Q<p2_2>, [x30, #496]
    tbl V<p2_2>.16b, {V<L2>.16b, V<bmid>.16b, V<bhigh>.16b}, V<p2_2>.16b
    orr V<p0_2>.16b, V<p0_2>.16b, V<p2_2>.16b
    str Q<p0_2>, [x29, #32]
    ldr Q<p0_3>, [x30, #512]
    tbl V<p0_3>.16b, {V<s12>.16b, V<rowq1>.16b}, V<p0_3>.16b
    ldr Q<p1_3>, [x30, #528]
    tbl V<p1_3>.16b, {V<rowq1>.16b, V<rowq2>.16b}, V<p1_3>.16b
    orr V<p0_3>.16b, V<p0_3>.16b, V<p1_3>.16b
    ldr Q<p2_3>, [x30, #544]
    tbl V<p2_3>.16b, {V<L2>.16b, V<bmid>.16b, V<bhigh>.16b}, V<p2_3>.16b
    orr V<p0_3>.16b, V<p0_3>.16b, V<p2_3>.16b
    str Q<p0_3>, [x29, #48]
    ldr Q<carry>, [x30, #560]
    tbl V<carry>.16b, {V<s12>.16b, V<rowq1>.16b}, V<carry>.16b
    ldr Q<p1_4>, [x30, #576]
    tbl V<p1_4>.16b, {V<rowq1>.16b, V<rowq2>.16b}, V<p1_4>.16b
    orr V<carry>.16b, V<carry>.16b, V<p1_4>.16b
    ldr Q<p2_4>, [x30, #592]
    tbl V<p2_4>.16b, {V<L2>.16b, V<bmid>.16b, V<bhigh>.16b}, V<p2_4>.16b
    orr V<carry>.16b, V<carry>.16b, V<p2_4>.16b
    str Q<L1>, [x4, #0]
    str Q<L2>, [x4, #16]
    str Q<L3>, [x4, #32]
    str Q<L4>, [x4, #48]
    str Q<H0>, [x4, #64]
    str Q<H1>, [x4, #80]
    str Q<b2>, [x4, #96]
    str Q<b5>, [x4, #112]
    str Q<b7>, [x4, #128]
    str Q<b8>, [x4, #144]
    str Q<carry>, [x4, #160]
gt864_p6d3_row4_slothy_end:
    ret

.global gt864_p6d3_row5
gt864_p6d3_row5:
// live-in: serialized frontier via x3, coefficient rows via x29, and fixed public tables via x30.
// live-out: exact next frontier via x4, or final canonical byte stream via the public output pointer.
// range: input coefficients are signed int16; normalized coefficients are 0..3456; packed lanes are bytes.
// reserved physical registers: x18 and sp; x29/x30 are intentionally fixed by the complete-function ABI.
gt864_p6d3_row5_slothy_start:
    ldr Q<L1>, [x3, #0]
    ldr Q<L2>, [x3, #16]
    ldr Q<L3>, [x3, #32]
    ldr Q<L4>, [x3, #48]
    ldr Q<H0>, [x3, #64]
    ldr Q<H1>, [x3, #80]
    ldr Q<b2>, [x3, #96]
    ldr Q<b5>, [x3, #112]
    ldr Q<b7>, [x3, #128]
    ldr Q<b8>, [x3, #144]
    ldr Q<carry>, [x3, #160]
    movi V<rowq0>.16b, #0
    mov V<rowq0>.d[0], x14
    mov V<rowq0>.d[1], x5
    movi V<rowq1>.16b, #0
    mov V<rowq1>.d[0], x27
    mov V<rowq1>.d[1], x10
    movi V<rowq2>.16b, #0
    mov V<rowq2>.d[0], x1
    mov V<rowq2>.d[1], x13
    ldr Q<modq>, [x30, #336]
    ldr Q<recip>, [x30, #352]
    sqrdmulh V<quotb7>.8h, V<b7>.8h, V<recip>.8h
    mls V<b7>.8h, V<quotb7>.8h, V<modq>.8h
    sshr V<quotb7>.8h, V<b7>.8h, #15
    and V<quotb7>.16b, V<quotb7>.16b, V<modq>.16b
    add V<b7>.8h, V<b7>.8h, V<quotb7>.8h
    eor V<modq>.16b, V<modq>.16b, V<modq>.16b
    sli V<modq>.8h, V<b7>.8h, #4
    xtn V<bmid>.8b, V<modq>.8h
    ushr V<bhighh>.8h, V<b7>.8h, #4
    xtn V<bhigh>.8b, V<bhighh>.8h
    ext V<alow>.16b, V<L3>.16b, V<L3>.16b, #8
    ext V<ahsrc>.16b, V<H1>.16b, V<H1>.16b, #12
    ldr Q<nibble>, [x30, #608]
    and V<ahlo>.16b, V<ahsrc>.16b, V<nibble>.16b
    ushr V<ahhi>.16b, V<ahsrc>.16b, #4
    zip1 V<ahi>.16b, V<ahlo>.16b, V<ahhi>.16b
    orr V<bmid>.8b, V<bmid>.8b, V<ahi>.8b
    ldr Q<p0_0>, [x30, #368]
    tbl V<p0_0>.16b, {V<rowq0>.16b, V<rowq1>.16b}, V<p0_0>.16b
    ldr Q<p1_0>, [x30, #384]
    tbl V<p1_0>.16b, {V<rowq1>.16b, V<rowq2>.16b}, V<p1_0>.16b
    orr V<p0_0>.16b, V<p0_0>.16b, V<p1_0>.16b
    ldr Q<p2_0>, [x30, #400]
    tbl V<p2_0>.16b, {V<alow>.16b, V<bmid>.16b, V<bhigh>.16b}, V<p2_0>.16b
    orr V<p0_0>.16b, V<p0_0>.16b, V<p2_0>.16b
    movi V<stream_0>.16b, #0
    mov V<stream_0>.d[0], V<carry>.d[0]
    mov V<stream_0>.d[1], V<p0_0>.d[0]
    str Q<stream_0>, [x29, #0]
    ldr Q<p0_1>, [x30, #416]
    tbl V<p0_1>.16b, {V<rowq0>.16b, V<rowq1>.16b}, V<p0_1>.16b
    ldr Q<p1_1>, [x30, #432]
    tbl V<p1_1>.16b, {V<rowq1>.16b, V<rowq2>.16b}, V<p1_1>.16b
    orr V<p0_1>.16b, V<p0_1>.16b, V<p1_1>.16b
    ldr Q<p2_1>, [x30, #448]
    tbl V<p2_1>.16b, {V<alow>.16b, V<bmid>.16b, V<bhigh>.16b}, V<p2_1>.16b
    orr V<p0_1>.16b, V<p0_1>.16b, V<p2_1>.16b
    movi V<stream_1>.16b, #0
    mov V<stream_1>.d[0], V<p0_0>.d[1]
    mov V<stream_1>.d[1], V<p0_1>.d[0]
    str Q<stream_1>, [x29, #16]
    ldr Q<p0_2>, [x30, #464]
    tbl V<p0_2>.16b, {V<rowq0>.16b, V<rowq1>.16b}, V<p0_2>.16b
    ldr Q<p1_2>, [x30, #480]
    tbl V<p1_2>.16b, {V<rowq1>.16b, V<rowq2>.16b}, V<p1_2>.16b
    orr V<p0_2>.16b, V<p0_2>.16b, V<p1_2>.16b
    ldr Q<p2_2>, [x30, #496]
    tbl V<p2_2>.16b, {V<alow>.16b, V<bmid>.16b, V<bhigh>.16b}, V<p2_2>.16b
    orr V<p0_2>.16b, V<p0_2>.16b, V<p2_2>.16b
    movi V<stream_2>.16b, #0
    mov V<stream_2>.d[0], V<p0_1>.d[1]
    mov V<stream_2>.d[1], V<p0_2>.d[0]
    str Q<stream_2>, [x29, #32]
    ldr Q<p0_3>, [x30, #512]
    tbl V<p0_3>.16b, {V<rowq0>.16b, V<rowq1>.16b}, V<p0_3>.16b
    ldr Q<p1_3>, [x30, #528]
    tbl V<p1_3>.16b, {V<rowq1>.16b, V<rowq2>.16b}, V<p1_3>.16b
    orr V<p0_3>.16b, V<p0_3>.16b, V<p1_3>.16b
    ldr Q<p2_3>, [x30, #544]
    tbl V<p2_3>.16b, {V<alow>.16b, V<bmid>.16b, V<bhigh>.16b}, V<p2_3>.16b
    orr V<p0_3>.16b, V<p0_3>.16b, V<p2_3>.16b
    movi V<stream_3>.16b, #0
    mov V<stream_3>.d[0], V<p0_2>.d[1]
    mov V<stream_3>.d[1], V<p0_3>.d[0]
    str Q<stream_3>, [x29, #48]
    ldr Q<p0_4>, [x30, #560]
    tbl V<p0_4>.16b, {V<rowq0>.16b, V<rowq1>.16b}, V<p0_4>.16b
    ldr Q<p1_4>, [x30, #576]
    tbl V<p1_4>.16b, {V<rowq1>.16b, V<rowq2>.16b}, V<p1_4>.16b
    orr V<p0_4>.16b, V<p0_4>.16b, V<p1_4>.16b
    ldr Q<p2_4>, [x30, #592]
    tbl V<p2_4>.16b, {V<alow>.16b, V<bmid>.16b, V<bhigh>.16b}, V<p2_4>.16b
    orr V<p0_4>.16b, V<p0_4>.16b, V<p2_4>.16b
    movi V<stream_4>.16b, #0
    mov V<stream_4>.d[0], V<p0_3>.d[1]
    mov V<stream_4>.d[1], V<p0_4>.d[0]
    str Q<stream_4>, [x29, #64]
    str Q<L1>, [x4, #0]
    str Q<L2>, [x4, #16]
    str Q<L4>, [x4, #32]
    str Q<H0>, [x4, #48]
    str Q<H1>, [x4, #64]
    str Q<b2>, [x4, #80]
    str Q<b5>, [x4, #96]
    str Q<b8>, [x4, #112]
gt864_p6d3_row5_slothy_end:
    ret

.global gt864_p6d3_row6
gt864_p6d3_row6:
// live-in: serialized frontier via x3, coefficient rows via x29, and fixed public tables via x30.
// live-out: exact next frontier via x4, or final canonical byte stream via the public output pointer.
// range: input coefficients are signed int16; normalized coefficients are 0..3456; packed lanes are bytes.
// reserved physical registers: x18 and sp; x29/x30 are intentionally fixed by the complete-function ABI.
gt864_p6d3_row6_slothy_start:
    ldr Q<L1>, [x3, #0]
    ldr Q<L2>, [x3, #16]
    ldr Q<L4>, [x3, #32]
    ldr Q<H0>, [x3, #48]
    ldr Q<H1>, [x3, #64]
    ldr Q<b2>, [x3, #80]
    ldr Q<b5>, [x3, #96]
    ldr Q<b8>, [x3, #112]
    movi V<rowq0>.16b, #0
    mov V<rowq0>.d[0], x2
    mov V<rowq0>.d[1], x19
    movi V<rowq1>.16b, #0
    mov V<rowq1>.d[0], x20
    mov V<rowq1>.d[1], x28
    movi V<rowq2>.16b, #0
    mov V<rowq2>.d[0], x24
    mov V<rowq2>.d[1], x21
    ldr Q<modq>, [x30, #336]
    ldr Q<recip>, [x30, #352]
    sqrdmulh V<quotb2>.8h, V<b2>.8h, V<recip>.8h
    mls V<b2>.8h, V<quotb2>.8h, V<modq>.8h
    sshr V<quotb2>.8h, V<b2>.8h, #15
    and V<quotb2>.16b, V<quotb2>.16b, V<modq>.16b
    add V<b2>.8h, V<b2>.8h, V<quotb2>.8h
    eor V<modq>.16b, V<modq>.16b, V<modq>.16b
    sli V<modq>.8h, V<b2>.8h, #4
    xtn V<bmid>.8b, V<modq>.8h
    ushr V<bhighh>.8h, V<b2>.8h, #4
    xtn V<bhigh>.8b, V<bhighh>.8h
    ext V<ahsrc>.16b, V<H0>.16b, V<H0>.16b, #8
    ldr Q<nibble>, [x30, #608]
    and V<ahlo>.16b, V<ahsrc>.16b, V<nibble>.16b
    ushr V<ahhi>.16b, V<ahsrc>.16b, #4
    zip1 V<ahi>.16b, V<ahlo>.16b, V<ahhi>.16b
    orr V<bmid>.8b, V<bmid>.8b, V<ahi>.8b
    ldr Q<p0_0>, [x30, #368]
    tbl V<p0_0>.16b, {V<rowq0>.16b, V<rowq1>.16b}, V<p0_0>.16b
    ldr Q<p1_0>, [x30, #384]
    tbl V<p1_0>.16b, {V<rowq1>.16b, V<rowq2>.16b}, V<p1_0>.16b
    orr V<p0_0>.16b, V<p0_0>.16b, V<p1_0>.16b
    ldr Q<p2_0>, [x30, #400]
    tbl V<p2_0>.16b, {V<L1>.16b, V<bmid>.16b, V<bhigh>.16b}, V<p2_0>.16b
    orr V<p0_0>.16b, V<p0_0>.16b, V<p2_0>.16b
    str Q<p0_0>, [x29, #0]
    ldr Q<p0_1>, [x30, #416]
    tbl V<p0_1>.16b, {V<rowq0>.16b, V<rowq1>.16b}, V<p0_1>.16b
    ldr Q<p1_1>, [x30, #432]
    tbl V<p1_1>.16b, {V<rowq1>.16b, V<rowq2>.16b}, V<p1_1>.16b
    orr V<p0_1>.16b, V<p0_1>.16b, V<p1_1>.16b
    ldr Q<p2_1>, [x30, #448]
    tbl V<p2_1>.16b, {V<L1>.16b, V<bmid>.16b, V<bhigh>.16b}, V<p2_1>.16b
    orr V<p0_1>.16b, V<p0_1>.16b, V<p2_1>.16b
    str Q<p0_1>, [x29, #16]
    ldr Q<p0_2>, [x30, #464]
    tbl V<p0_2>.16b, {V<rowq0>.16b, V<rowq1>.16b}, V<p0_2>.16b
    ldr Q<p1_2>, [x30, #480]
    tbl V<p1_2>.16b, {V<rowq1>.16b, V<rowq2>.16b}, V<p1_2>.16b
    orr V<p0_2>.16b, V<p0_2>.16b, V<p1_2>.16b
    ldr Q<p2_2>, [x30, #496]
    tbl V<p2_2>.16b, {V<L1>.16b, V<bmid>.16b, V<bhigh>.16b}, V<p2_2>.16b
    orr V<p0_2>.16b, V<p0_2>.16b, V<p2_2>.16b
    str Q<p0_2>, [x29, #32]
    ldr Q<p0_3>, [x30, #512]
    tbl V<p0_3>.16b, {V<rowq0>.16b, V<rowq1>.16b}, V<p0_3>.16b
    ldr Q<p1_3>, [x30, #528]
    tbl V<p1_3>.16b, {V<rowq1>.16b, V<rowq2>.16b}, V<p1_3>.16b
    orr V<p0_3>.16b, V<p0_3>.16b, V<p1_3>.16b
    ldr Q<p2_3>, [x30, #544]
    tbl V<p2_3>.16b, {V<L1>.16b, V<bmid>.16b, V<bhigh>.16b}, V<p2_3>.16b
    orr V<p0_3>.16b, V<p0_3>.16b, V<p2_3>.16b
    str Q<p0_3>, [x29, #48]
    ldr Q<carry>, [x30, #560]
    tbl V<carry>.16b, {V<rowq0>.16b, V<rowq1>.16b}, V<carry>.16b
    ldr Q<p1_4>, [x30, #576]
    tbl V<p1_4>.16b, {V<rowq1>.16b, V<rowq2>.16b}, V<p1_4>.16b
    orr V<carry>.16b, V<carry>.16b, V<p1_4>.16b
    ldr Q<p2_4>, [x30, #592]
    tbl V<p2_4>.16b, {V<L1>.16b, V<bmid>.16b, V<bhigh>.16b}, V<p2_4>.16b
    orr V<carry>.16b, V<carry>.16b, V<p2_4>.16b
    str Q<L2>, [x4, #0]
    str Q<L4>, [x4, #16]
    str Q<H1>, [x4, #32]
    str Q<b5>, [x4, #48]
    str Q<b8>, [x4, #64]
    str Q<carry>, [x4, #80]
gt864_p6d3_row6_slothy_end:
    ret

.global gt864_p6d3_row7
gt864_p6d3_row7:
// live-in: serialized frontier via x3, coefficient rows via x29, and fixed public tables via x30.
// live-out: exact next frontier via x4, or final canonical byte stream via the public output pointer.
// range: input coefficients are signed int16; normalized coefficients are 0..3456; packed lanes are bytes.
// reserved physical registers: x18 and sp; x29/x30 are intentionally fixed by the complete-function ABI.
gt864_p6d3_row7_slothy_start:
    ldr Q<L2>, [x3, #0]
    ldr Q<L4>, [x3, #16]
    ldr Q<H1>, [x3, #32]
    ldr Q<b5>, [x3, #48]
    ldr Q<b8>, [x3, #64]
    ldr Q<carry>, [x3, #80]
    movi V<rowq0>.16b, #0
    mov V<rowq0>.d[0], x15
    mov V<rowq0>.d[1], x26
    movi V<rowq1>.16b, #0
    mov V<rowq1>.d[0], x12
    mov V<rowq1>.d[1], x23
    movi V<rowq2>.16b, #0
    mov V<rowq2>.d[0], x0
    mov V<rowq2>.d[1], x8
    ldr Q<modq>, [x30, #336]
    ldr Q<recip>, [x30, #352]
    sqrdmulh V<quotb5>.8h, V<b5>.8h, V<recip>.8h
    mls V<b5>.8h, V<quotb5>.8h, V<modq>.8h
    sshr V<quotb5>.8h, V<b5>.8h, #15
    and V<quotb5>.16b, V<quotb5>.16b, V<modq>.16b
    add V<b5>.8h, V<b5>.8h, V<quotb5>.8h
    eor V<modq>.16b, V<modq>.16b, V<modq>.16b
    sli V<modq>.8h, V<b5>.8h, #4
    xtn V<bmid>.8b, V<modq>.8h
    ushr V<bhighh>.8h, V<b5>.8h, #4
    xtn V<bhigh>.8b, V<bhighh>.8h
    ext V<alow>.16b, V<L2>.16b, V<L2>.16b, #8
    ext V<ahsrc>.16b, V<H1>.16b, V<H1>.16b, #4
    ldr Q<nibble>, [x30, #608]
    and V<ahlo>.16b, V<ahsrc>.16b, V<nibble>.16b
    ushr V<ahhi>.16b, V<ahsrc>.16b, #4
    zip1 V<ahi>.16b, V<ahlo>.16b, V<ahhi>.16b
    orr V<bmid>.8b, V<bmid>.8b, V<ahi>.8b
    ldr Q<p0_0>, [x30, #368]
    tbl V<p0_0>.16b, {V<rowq0>.16b, V<rowq1>.16b}, V<p0_0>.16b
    ldr Q<p1_0>, [x30, #384]
    tbl V<p1_0>.16b, {V<rowq1>.16b, V<rowq2>.16b}, V<p1_0>.16b
    orr V<p0_0>.16b, V<p0_0>.16b, V<p1_0>.16b
    ldr Q<p2_0>, [x30, #400]
    tbl V<p2_0>.16b, {V<alow>.16b, V<bmid>.16b, V<bhigh>.16b}, V<p2_0>.16b
    orr V<p0_0>.16b, V<p0_0>.16b, V<p2_0>.16b
    movi V<stream_0>.16b, #0
    mov V<stream_0>.d[0], V<carry>.d[0]
    mov V<stream_0>.d[1], V<p0_0>.d[0]
    str Q<stream_0>, [x29, #0]
    ldr Q<p0_1>, [x30, #416]
    tbl V<p0_1>.16b, {V<rowq0>.16b, V<rowq1>.16b}, V<p0_1>.16b
    ldr Q<p1_1>, [x30, #432]
    tbl V<p1_1>.16b, {V<rowq1>.16b, V<rowq2>.16b}, V<p1_1>.16b
    orr V<p0_1>.16b, V<p0_1>.16b, V<p1_1>.16b
    ldr Q<p2_1>, [x30, #448]
    tbl V<p2_1>.16b, {V<alow>.16b, V<bmid>.16b, V<bhigh>.16b}, V<p2_1>.16b
    orr V<p0_1>.16b, V<p0_1>.16b, V<p2_1>.16b
    movi V<stream_1>.16b, #0
    mov V<stream_1>.d[0], V<p0_0>.d[1]
    mov V<stream_1>.d[1], V<p0_1>.d[0]
    str Q<stream_1>, [x29, #16]
    ldr Q<p0_2>, [x30, #464]
    tbl V<p0_2>.16b, {V<rowq0>.16b, V<rowq1>.16b}, V<p0_2>.16b
    ldr Q<p1_2>, [x30, #480]
    tbl V<p1_2>.16b, {V<rowq1>.16b, V<rowq2>.16b}, V<p1_2>.16b
    orr V<p0_2>.16b, V<p0_2>.16b, V<p1_2>.16b
    ldr Q<p2_2>, [x30, #496]
    tbl V<p2_2>.16b, {V<alow>.16b, V<bmid>.16b, V<bhigh>.16b}, V<p2_2>.16b
    orr V<p0_2>.16b, V<p0_2>.16b, V<p2_2>.16b
    movi V<stream_2>.16b, #0
    mov V<stream_2>.d[0], V<p0_1>.d[1]
    mov V<stream_2>.d[1], V<p0_2>.d[0]
    str Q<stream_2>, [x29, #32]
    ldr Q<p0_3>, [x30, #512]
    tbl V<p0_3>.16b, {V<rowq0>.16b, V<rowq1>.16b}, V<p0_3>.16b
    ldr Q<p1_3>, [x30, #528]
    tbl V<p1_3>.16b, {V<rowq1>.16b, V<rowq2>.16b}, V<p1_3>.16b
    orr V<p0_3>.16b, V<p0_3>.16b, V<p1_3>.16b
    ldr Q<p2_3>, [x30, #544]
    tbl V<p2_3>.16b, {V<alow>.16b, V<bmid>.16b, V<bhigh>.16b}, V<p2_3>.16b
    orr V<p0_3>.16b, V<p0_3>.16b, V<p2_3>.16b
    movi V<stream_3>.16b, #0
    mov V<stream_3>.d[0], V<p0_2>.d[1]
    mov V<stream_3>.d[1], V<p0_3>.d[0]
    str Q<stream_3>, [x29, #48]
    ldr Q<p0_4>, [x30, #560]
    tbl V<p0_4>.16b, {V<rowq0>.16b, V<rowq1>.16b}, V<p0_4>.16b
    ldr Q<p1_4>, [x30, #576]
    tbl V<p1_4>.16b, {V<rowq1>.16b, V<rowq2>.16b}, V<p1_4>.16b
    orr V<p0_4>.16b, V<p0_4>.16b, V<p1_4>.16b
    ldr Q<p2_4>, [x30, #592]
    tbl V<p2_4>.16b, {V<alow>.16b, V<bmid>.16b, V<bhigh>.16b}, V<p2_4>.16b
    orr V<p0_4>.16b, V<p0_4>.16b, V<p2_4>.16b
    movi V<stream_4>.16b, #0
    mov V<stream_4>.d[0], V<p0_3>.d[1]
    mov V<stream_4>.d[1], V<p0_4>.d[0]
    str Q<stream_4>, [x29, #64]
    str Q<L4>, [x4, #0]
    str Q<b8>, [x4, #16]
gt864_p6d3_row7_slothy_end:
    ret

.global gt864_p6d3_row8
gt864_p6d3_row8:
// live-in: serialized frontier via x3, coefficient rows via x29, and fixed public tables via x30.
// live-out: exact next frontier via x4, or final canonical byte stream via the public output pointer.
// range: input coefficients are signed int16; normalized coefficients are 0..3456; packed lanes are bytes.
// reserved physical registers: x18 and sp; x29/x30 are intentionally fixed by the complete-function ABI.
gt864_p6d3_row8_slothy_start:
    ldr Q<L4>, [x3, #0]
    ldr Q<b8>, [x3, #16]
    movi V<rowq0>.16b, #0
    mov V<rowq0>.d[0], x11
    mov V<rowq0>.d[1], x4
    movi V<rowq1>.16b, #0
    mov V<rowq1>.d[0], x25
    mov V<rowq1>.d[1], x22
    movi V<rowq2>.16b, #0
    mov V<rowq2>.d[0], x6
    mov V<rowq2>.d[1], x3
    ldr Q<modq>, [x30, #336]
    ldr Q<recip>, [x30, #352]
    sqrdmulh V<quotb8>.8h, V<b8>.8h, V<recip>.8h
    mls V<b8>.8h, V<quotb8>.8h, V<modq>.8h
    sshr V<quotb8>.8h, V<b8>.8h, #15
    and V<quotb8>.16b, V<quotb8>.16b, V<modq>.16b
    add V<b8>.8h, V<b8>.8h, V<quotb8>.8h
    eor V<modq>.16b, V<modq>.16b, V<modq>.16b
    sli V<modq>.8h, V<b8>.8h, #4
    xtn V<bmid>.8b, V<modq>.8h
    ushr V<bhighh>.8h, V<b8>.8h, #4
    xtn V<bhigh>.8b, V<bhighh>.8h
    ext V<ahsrc>.16b, V<L4>.16b, V<L4>.16b, #8
    ldr Q<nibble>, [x30, #608]
    and V<ahlo>.16b, V<ahsrc>.16b, V<nibble>.16b
    ushr V<ahhi>.16b, V<ahsrc>.16b, #4
    zip1 V<ahi>.16b, V<ahlo>.16b, V<ahhi>.16b
    orr V<bmid>.8b, V<bmid>.8b, V<ahi>.8b
    ldr Q<p0_0>, [x30, #368]
    tbl V<p0_0>.16b, {V<rowq0>.16b, V<rowq1>.16b}, V<p0_0>.16b
    ldr Q<p1_0>, [x30, #384]
    tbl V<p1_0>.16b, {V<rowq1>.16b, V<rowq2>.16b}, V<p1_0>.16b
    orr V<p0_0>.16b, V<p0_0>.16b, V<p1_0>.16b
    ldr Q<p2_0>, [x30, #400]
    tbl V<p2_0>.16b, {V<L4>.16b, V<bmid>.16b, V<bhigh>.16b}, V<p2_0>.16b
    orr V<p0_0>.16b, V<p0_0>.16b, V<p2_0>.16b
    str Q<p0_0>, [x29, #0]
    ldr Q<p0_1>, [x30, #416]
    tbl V<p0_1>.16b, {V<rowq0>.16b, V<rowq1>.16b}, V<p0_1>.16b
    ldr Q<p1_1>, [x30, #432]
    tbl V<p1_1>.16b, {V<rowq1>.16b, V<rowq2>.16b}, V<p1_1>.16b
    orr V<p0_1>.16b, V<p0_1>.16b, V<p1_1>.16b
    ldr Q<p2_1>, [x30, #448]
    tbl V<p2_1>.16b, {V<L4>.16b, V<bmid>.16b, V<bhigh>.16b}, V<p2_1>.16b
    orr V<p0_1>.16b, V<p0_1>.16b, V<p2_1>.16b
    str Q<p0_1>, [x29, #16]
    ldr Q<p0_2>, [x30, #464]
    tbl V<p0_2>.16b, {V<rowq0>.16b, V<rowq1>.16b}, V<p0_2>.16b
    ldr Q<p1_2>, [x30, #480]
    tbl V<p1_2>.16b, {V<rowq1>.16b, V<rowq2>.16b}, V<p1_2>.16b
    orr V<p0_2>.16b, V<p0_2>.16b, V<p1_2>.16b
    ldr Q<p2_2>, [x30, #496]
    tbl V<p2_2>.16b, {V<L4>.16b, V<bmid>.16b, V<bhigh>.16b}, V<p2_2>.16b
    orr V<p0_2>.16b, V<p0_2>.16b, V<p2_2>.16b
    str Q<p0_2>, [x29, #32]
    ldr Q<p0_3>, [x30, #512]
    tbl V<p0_3>.16b, {V<rowq0>.16b, V<rowq1>.16b}, V<p0_3>.16b
    ldr Q<p1_3>, [x30, #528]
    tbl V<p1_3>.16b, {V<rowq1>.16b, V<rowq2>.16b}, V<p1_3>.16b
    orr V<p0_3>.16b, V<p0_3>.16b, V<p1_3>.16b
    ldr Q<p2_3>, [x30, #544]
    tbl V<p2_3>.16b, {V<L4>.16b, V<bmid>.16b, V<bhigh>.16b}, V<p2_3>.16b
    orr V<p0_3>.16b, V<p0_3>.16b, V<p2_3>.16b
    str Q<p0_3>, [x29, #48]
    ldr Q<p0_4>, [x30, #560]
    tbl V<p0_4>.16b, {V<rowq0>.16b, V<rowq1>.16b}, V<p0_4>.16b
    ldr Q<p1_4>, [x30, #576]
    tbl V<p1_4>.16b, {V<rowq1>.16b, V<rowq2>.16b}, V<p1_4>.16b
    orr V<p0_4>.16b, V<p0_4>.16b, V<p1_4>.16b
    ldr Q<p2_4>, [x30, #592]
    tbl V<p2_4>.16b, {V<L4>.16b, V<bmid>.16b, V<bhigh>.16b}, V<p2_4>.16b
    orr V<p0_4>.16b, V<p0_4>.16b, V<p2_4>.16b
    str D<p0_4>, [x29, #64]
gt864_p6d3_row8_slothy_end:
    ret
