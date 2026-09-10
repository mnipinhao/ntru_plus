.text
.global pair_merge_small
pair_merge_small:
// live-in: x0-x4,x6,x7,x9; memory live-out: 648 final bytes.
// range: see kernel-contract.yml; constants public; reserved registers: x18-x30.
// Internal ABI; public caller must preserve d8-d15.
pair_merge_small_slothy_start:
    ldr Q<aj0>, [x1, #384]
    ldr Q<aj1>, [x1, #336]
    ext V<aj1>.16b, V<aj1>.16b, V<aj1>.16b, #14
    ldr Q<aj2>, [x1, #288]
    ext V<aj2>.16b, V<aj2>.16b, V<aj2>.16b, #12
    ldr Q<aj3>, [x1, #240]
    ext V<aj3>.16b, V<aj3>.16b, V<aj3>.16b, #10
    ldr Q<aj4>, [x1, #192]
    ext V<aj4>.16b, V<aj4>.16b, V<aj4>.16b, #8
    ldr Q<aj5>, [x1, #144]
    ext V<aj5>.16b, V<aj5>.16b, V<aj5>.16b, #6
    ldr Q<aj6>, [x1, #96]
    ext V<aj6>.16b, V<aj6>.16b, V<aj6>.16b, #4
    ldr Q<aj7>, [x1, #48]
    ext V<aj7>.16b, V<aj7>.16b, V<aj7>.16b, #2
    ldr Q<aninth>, [x1]
    trn1 V<au0>.8h, V<aj0>.8h, V<aj1>.8h
    trn2 V<au1>.8h, V<aj0>.8h, V<aj1>.8h
    trn1 V<au2>.8h, V<aj2>.8h, V<aj3>.8h
    trn2 V<au3>.8h, V<aj2>.8h, V<aj3>.8h
    trn1 V<au4>.8h, V<aj4>.8h, V<aj5>.8h
    trn2 V<au5>.8h, V<aj4>.8h, V<aj5>.8h
    trn1 V<au6>.8h, V<aj6>.8h, V<aj7>.8h
    trn2 V<au7>.8h, V<aj6>.8h, V<aj7>.8h
    trn1 V<az0>.4s, V<au0>.4s, V<au2>.4s
    trn1 V<az1>.4s, V<au1>.4s, V<au3>.4s
    trn2 V<az2>.4s, V<au0>.4s, V<au2>.4s
    trn2 V<az3>.4s, V<au1>.4s, V<au3>.4s
    trn1 V<az4>.4s, V<au4>.4s, V<au6>.4s
    trn1 V<az5>.4s, V<au5>.4s, V<au7>.4s
    trn2 V<az6>.4s, V<au4>.4s, V<au6>.4s
    trn2 V<az7>.4s, V<au5>.4s, V<au7>.4s
    trn1 V<at0>.2d, V<az0>.2d, V<az4>.2d
    trn2 V<at4>.2d, V<az0>.2d, V<az4>.2d
    trn1 V<at1>.2d, V<az1>.2d, V<az5>.2d
    trn2 V<at5>.2d, V<az1>.2d, V<az5>.2d
    trn1 V<at2>.2d, V<az2>.2d, V<az6>.2d
    trn2 V<at6>.2d, V<az2>.2d, V<az6>.2d
    trn1 V<at3>.2d, V<az3>.2d, V<az7>.2d
    trn2 V<at7>.2d, V<az3>.2d, V<az7>.2d
    ldr Q<bj0>, [x2, #384]
    ldr Q<bj1>, [x2, #336]
    ext V<bj1>.16b, V<bj1>.16b, V<bj1>.16b, #14
    ldr Q<bj2>, [x2, #288]
    ext V<bj2>.16b, V<bj2>.16b, V<bj2>.16b, #12
    ldr Q<bj3>, [x2, #240]
    ext V<bj3>.16b, V<bj3>.16b, V<bj3>.16b, #10
    ldr Q<bj4>, [x2, #192]
    ext V<bj4>.16b, V<bj4>.16b, V<bj4>.16b, #8
    ldr Q<bj5>, [x2, #144]
    ext V<bj5>.16b, V<bj5>.16b, V<bj5>.16b, #6
    ldr Q<bj6>, [x2, #96]
    ext V<bj6>.16b, V<bj6>.16b, V<bj6>.16b, #4
    ldr Q<bj7>, [x2, #48]
    ext V<bj7>.16b, V<bj7>.16b, V<bj7>.16b, #2
    ldr Q<bninth>, [x2]
    trn1 V<bu0>.8h, V<bj0>.8h, V<bj1>.8h
    trn2 V<bu1>.8h, V<bj0>.8h, V<bj1>.8h
    trn1 V<bu2>.8h, V<bj2>.8h, V<bj3>.8h
    trn2 V<bu3>.8h, V<bj2>.8h, V<bj3>.8h
    trn1 V<bu4>.8h, V<bj4>.8h, V<bj5>.8h
    trn2 V<bu5>.8h, V<bj4>.8h, V<bj5>.8h
    trn1 V<bu6>.8h, V<bj6>.8h, V<bj7>.8h
    trn2 V<bu7>.8h, V<bj6>.8h, V<bj7>.8h
    trn1 V<bz0>.4s, V<bu0>.4s, V<bu2>.4s
    trn1 V<bz1>.4s, V<bu1>.4s, V<bu3>.4s
    trn2 V<bz2>.4s, V<bu0>.4s, V<bu2>.4s
    trn2 V<bz3>.4s, V<bu1>.4s, V<bu3>.4s
    trn1 V<bz4>.4s, V<bu4>.4s, V<bu6>.4s
    trn1 V<bz5>.4s, V<bu5>.4s, V<bu7>.4s
    trn2 V<bz6>.4s, V<bu4>.4s, V<bu6>.4s
    trn2 V<bz7>.4s, V<bu5>.4s, V<bu7>.4s
    trn1 V<bt0>.2d, V<bz0>.2d, V<bz4>.2d
    trn2 V<bt4>.2d, V<bz0>.2d, V<bz4>.2d
    trn1 V<bt1>.2d, V<bz1>.2d, V<bz5>.2d
    trn2 V<bt5>.2d, V<bz1>.2d, V<bz5>.2d
    trn1 V<bt2>.2d, V<bz2>.2d, V<bz6>.2d
    trn2 V<bt6>.2d, V<bz2>.2d, V<bz6>.2d
    trn1 V<bt3>.2d, V<bz3>.2d, V<bz7>.2d
    trn2 V<bt7>.2d, V<bz3>.2d, V<bz7>.2d
    mov w8, #3457
    dup V<q>.8h, w8
    // ROW 0: create only this pair; t-1 dies after this row when applicable
    ldr Q<idx0>, [x4, #0]
    orr V<arow0>.16b, V<at0>.16b, V<at0>.16b
    ins V<arow0>.h[0], V<aninth>.h[0]
    tbl V<arow0>.16b, {V<arow0>.16b}, V<idx0>.16b
    sshr V<asign0>.8h, V<arow0>.8h, #15
    and V<asign0>.16b, V<asign0>.16b, V<q>.16b
    add V<arow0>.8h, V<arow0>.8h, V<asign0>.8h
    orr V<brow0>.16b, V<bt0>.16b, V<bt0>.16b
    ins V<brow0>.h[0], V<bninth>.h[0]
    tbl V<brow0>.16b, {V<brow0>.16b}, V<idx0>.16b
    sshr V<bsign0>.8h, V<brow0>.8h, #15
    and V<bsign0>.16b, V<bsign0>.16b, V<q>.16b
    add V<brow0>.8h, V<brow0>.8h, V<bsign0>.8h
    xtn V<lo0>.8b, V<arow0>.8h
    ushr V<mix0>.8h, V<arow0>.8h, #8
    sli V<mix0>.8h, V<brow0>.8h, #4
    xtn V<mid0>.8b, V<mix0>.8h
    ushr V<brow0>.8h, V<brow0>.8h, #4
    xtn V<hi0>.8b, V<brow0>.8h
    add x10, x6, #0
    ldr Q<m0_p0lo>, [x10]
    add x10, x10, #16
    ldr D<m0_p0hi>, [x10]
    add x10, x7, #0
    ldr Q<m0_p1lo>, [x10]
    add x10, x10, #16
    ldr D<m0_p1hi>, [x10]
    add x11, x0, #0
    ldr Q<m0_idx0>, [x9, #0]
    tbl V<m0_part0>.16b, {V<m0_p0lo>.16b, V<m0_p0hi>.16b}, V<m0_idx0>.16b
    ldr Q<m0_idx1>, [x9, #16]
    tbl V<m0_part1>.16b, {V<m0_p1lo>.16b, V<m0_p1hi>.16b}, V<m0_idx1>.16b
    ldr Q<m0_idx2>, [x9, #32]
    tbl V<m0_part2>.16b, {V<lo0>.16b, V<mid0>.16b, V<hi0>.16b}, V<m0_idx2>.16b
    orr V<m0_out0>.16b, V<m0_part0>.16b, V<m0_part1>.16b
    orr V<m0_out0>.16b, V<m0_out0>.16b, V<m0_part2>.16b
    str Q<m0_out0>, [x11, #0]
    ldr Q<m0_idx3>, [x9, #48]
    tbl V<m0_part3>.16b, {V<m0_p0lo>.16b, V<m0_p0hi>.16b}, V<m0_idx3>.16b
    ldr Q<m0_idx4>, [x9, #64]
    tbl V<m0_part4>.16b, {V<m0_p1lo>.16b, V<m0_p1hi>.16b}, V<m0_idx4>.16b
    ldr Q<m0_idx5>, [x9, #80]
    tbl V<m0_part5>.16b, {V<lo0>.16b, V<mid0>.16b, V<hi0>.16b}, V<m0_idx5>.16b
    orr V<m0_out1>.16b, V<m0_part3>.16b, V<m0_part4>.16b
    orr V<m0_out1>.16b, V<m0_out1>.16b, V<m0_part5>.16b
    str Q<m0_out1>, [x11, #16]
    ldr Q<m0_idx6>, [x9, #96]
    tbl V<m0_part6>.16b, {V<m0_p0lo>.16b, V<m0_p0hi>.16b}, V<m0_idx6>.16b
    ldr Q<m0_idx7>, [x9, #112]
    tbl V<m0_part7>.16b, {V<m0_p1lo>.16b, V<m0_p1hi>.16b}, V<m0_idx7>.16b
    ldr Q<m0_idx8>, [x9, #128]
    tbl V<m0_part8>.16b, {V<lo0>.16b, V<mid0>.16b, V<hi0>.16b}, V<m0_idx8>.16b
    orr V<m0_out2>.16b, V<m0_part6>.16b, V<m0_part7>.16b
    orr V<m0_out2>.16b, V<m0_out2>.16b, V<m0_part8>.16b
    str Q<m0_out2>, [x11, #32]
    ldr Q<m0_idx9>, [x9, #144]
    tbl V<m0_part9>.16b, {V<m0_p0lo>.16b, V<m0_p0hi>.16b}, V<m0_idx9>.16b
    ldr Q<m0_idx10>, [x9, #160]
    tbl V<m0_part10>.16b, {V<m0_p1lo>.16b, V<m0_p1hi>.16b}, V<m0_idx10>.16b
    ldr Q<m0_idx11>, [x9, #176]
    tbl V<m0_part11>.16b, {V<lo0>.16b, V<mid0>.16b, V<hi0>.16b}, V<m0_idx11>.16b
    orr V<m0_out3>.16b, V<m0_part9>.16b, V<m0_part10>.16b
    orr V<m0_out3>.16b, V<m0_out3>.16b, V<m0_part11>.16b
    str Q<m0_out3>, [x11, #48]
    ldr Q<m0_idx12>, [x9, #192]
    tbl V<m0_part12>.16b, {V<m0_p0lo>.16b, V<m0_p0hi>.16b}, V<m0_idx12>.16b
    ldr Q<m0_idx13>, [x9, #208]
    tbl V<m0_part13>.16b, {V<m0_p1lo>.16b, V<m0_p1hi>.16b}, V<m0_idx13>.16b
    ldr Q<m0_idx14>, [x9, #224]
    tbl V<m0_part14>.16b, {V<lo0>.16b, V<mid0>.16b, V<hi0>.16b}, V<m0_idx14>.16b
    orr V<m0_out4>.16b, V<m0_part12>.16b, V<m0_part13>.16b
    orr V<m0_out4>.16b, V<m0_out4>.16b, V<m0_part14>.16b
    str D<m0_out4>, [x11, #64]
    // ROW 1: create only this pair; t0 dies after this row when applicable
    ldr Q<idx1>, [x4, #16]
    ldr Q<mask1>, [x3, #0]
    and V<arow1>.16b, V<at0>.16b, V<mask1>.16b
    bic V<aother1>.16b, V<at1>.16b, V<mask1>.16b
    orr V<arow1>.16b, V<arow1>.16b, V<aother1>.16b
    ins V<arow1>.h[1], V<aninth>.h[1]
    tbl V<arow1>.16b, {V<arow1>.16b}, V<idx1>.16b
    sshr V<asign1>.8h, V<arow1>.8h, #15
    and V<asign1>.16b, V<asign1>.16b, V<q>.16b
    add V<arow1>.8h, V<arow1>.8h, V<asign1>.8h
    and V<brow1>.16b, V<bt0>.16b, V<mask1>.16b
    bic V<bother1>.16b, V<bt1>.16b, V<mask1>.16b
    orr V<brow1>.16b, V<brow1>.16b, V<bother1>.16b
    ins V<brow1>.h[1], V<bninth>.h[1]
    tbl V<brow1>.16b, {V<brow1>.16b}, V<idx1>.16b
    sshr V<bsign1>.8h, V<brow1>.8h, #15
    and V<bsign1>.16b, V<bsign1>.16b, V<q>.16b
    add V<brow1>.8h, V<brow1>.8h, V<bsign1>.8h
    xtn V<lo1>.8b, V<arow1>.8h
    ushr V<mix1>.8h, V<arow1>.8h, #8
    sli V<mix1>.8h, V<brow1>.8h, #4
    xtn V<mid1>.8b, V<mix1>.8h
    ushr V<brow1>.8h, V<brow1>.8h, #4
    xtn V<hi1>.8b, V<brow1>.8h
    add x10, x6, #72
    ldr Q<m3_p0lo>, [x10]
    add x10, x10, #16
    ldr D<m3_p0hi>, [x10]
    add x10, x7, #72
    ldr Q<m3_p1lo>, [x10]
    add x10, x10, #16
    ldr D<m3_p1hi>, [x10]
    add x11, x0, #216
    ldr Q<m3_idx0>, [x9, #0]
    tbl V<m3_part0>.16b, {V<m3_p0lo>.16b, V<m3_p0hi>.16b}, V<m3_idx0>.16b
    ldr Q<m3_idx1>, [x9, #16]
    tbl V<m3_part1>.16b, {V<m3_p1lo>.16b, V<m3_p1hi>.16b}, V<m3_idx1>.16b
    ldr Q<m3_idx2>, [x9, #32]
    tbl V<m3_part2>.16b, {V<lo1>.16b, V<mid1>.16b, V<hi1>.16b}, V<m3_idx2>.16b
    orr V<m3_out0>.16b, V<m3_part0>.16b, V<m3_part1>.16b
    orr V<m3_out0>.16b, V<m3_out0>.16b, V<m3_part2>.16b
    str Q<m3_out0>, [x11, #0]
    ldr Q<m3_idx3>, [x9, #48]
    tbl V<m3_part3>.16b, {V<m3_p0lo>.16b, V<m3_p0hi>.16b}, V<m3_idx3>.16b
    ldr Q<m3_idx4>, [x9, #64]
    tbl V<m3_part4>.16b, {V<m3_p1lo>.16b, V<m3_p1hi>.16b}, V<m3_idx4>.16b
    ldr Q<m3_idx5>, [x9, #80]
    tbl V<m3_part5>.16b, {V<lo1>.16b, V<mid1>.16b, V<hi1>.16b}, V<m3_idx5>.16b
    orr V<m3_out1>.16b, V<m3_part3>.16b, V<m3_part4>.16b
    orr V<m3_out1>.16b, V<m3_out1>.16b, V<m3_part5>.16b
    str Q<m3_out1>, [x11, #16]
    ldr Q<m3_idx6>, [x9, #96]
    tbl V<m3_part6>.16b, {V<m3_p0lo>.16b, V<m3_p0hi>.16b}, V<m3_idx6>.16b
    ldr Q<m3_idx7>, [x9, #112]
    tbl V<m3_part7>.16b, {V<m3_p1lo>.16b, V<m3_p1hi>.16b}, V<m3_idx7>.16b
    ldr Q<m3_idx8>, [x9, #128]
    tbl V<m3_part8>.16b, {V<lo1>.16b, V<mid1>.16b, V<hi1>.16b}, V<m3_idx8>.16b
    orr V<m3_out2>.16b, V<m3_part6>.16b, V<m3_part7>.16b
    orr V<m3_out2>.16b, V<m3_out2>.16b, V<m3_part8>.16b
    str Q<m3_out2>, [x11, #32]
    ldr Q<m3_idx9>, [x9, #144]
    tbl V<m3_part9>.16b, {V<m3_p0lo>.16b, V<m3_p0hi>.16b}, V<m3_idx9>.16b
    ldr Q<m3_idx10>, [x9, #160]
    tbl V<m3_part10>.16b, {V<m3_p1lo>.16b, V<m3_p1hi>.16b}, V<m3_idx10>.16b
    ldr Q<m3_idx11>, [x9, #176]
    tbl V<m3_part11>.16b, {V<lo1>.16b, V<mid1>.16b, V<hi1>.16b}, V<m3_idx11>.16b
    orr V<m3_out3>.16b, V<m3_part9>.16b, V<m3_part10>.16b
    orr V<m3_out3>.16b, V<m3_out3>.16b, V<m3_part11>.16b
    str Q<m3_out3>, [x11, #48]
    ldr Q<m3_idx12>, [x9, #192]
    tbl V<m3_part12>.16b, {V<m3_p0lo>.16b, V<m3_p0hi>.16b}, V<m3_idx12>.16b
    ldr Q<m3_idx13>, [x9, #208]
    tbl V<m3_part13>.16b, {V<m3_p1lo>.16b, V<m3_p1hi>.16b}, V<m3_idx13>.16b
    ldr Q<m3_idx14>, [x9, #224]
    tbl V<m3_part14>.16b, {V<lo1>.16b, V<mid1>.16b, V<hi1>.16b}, V<m3_idx14>.16b
    orr V<m3_out4>.16b, V<m3_part12>.16b, V<m3_part13>.16b
    orr V<m3_out4>.16b, V<m3_out4>.16b, V<m3_part14>.16b
    str D<m3_out4>, [x11, #64]
    // ROW 2: create only this pair; t1 dies after this row when applicable
    ldr Q<idx2>, [x4, #32]
    ldr Q<mask2>, [x3, #16]
    and V<arow2>.16b, V<at1>.16b, V<mask2>.16b
    bic V<aother2>.16b, V<at2>.16b, V<mask2>.16b
    orr V<arow2>.16b, V<arow2>.16b, V<aother2>.16b
    ins V<arow2>.h[2], V<aninth>.h[2]
    tbl V<arow2>.16b, {V<arow2>.16b}, V<idx2>.16b
    sshr V<asign2>.8h, V<arow2>.8h, #15
    and V<asign2>.16b, V<asign2>.16b, V<q>.16b
    add V<arow2>.8h, V<arow2>.8h, V<asign2>.8h
    and V<brow2>.16b, V<bt1>.16b, V<mask2>.16b
    bic V<bother2>.16b, V<bt2>.16b, V<mask2>.16b
    orr V<brow2>.16b, V<brow2>.16b, V<bother2>.16b
    ins V<brow2>.h[2], V<bninth>.h[2]
    tbl V<brow2>.16b, {V<brow2>.16b}, V<idx2>.16b
    sshr V<bsign2>.8h, V<brow2>.8h, #15
    and V<bsign2>.16b, V<bsign2>.16b, V<q>.16b
    add V<brow2>.8h, V<brow2>.8h, V<bsign2>.8h
    xtn V<lo2>.8b, V<arow2>.8h
    ushr V<mix2>.8h, V<arow2>.8h, #8
    sli V<mix2>.8h, V<brow2>.8h, #4
    xtn V<mid2>.8b, V<mix2>.8h
    ushr V<brow2>.8h, V<brow2>.8h, #4
    xtn V<hi2>.8b, V<brow2>.8h
    add x10, x6, #144
    ldr Q<m6_p0lo>, [x10]
    add x10, x10, #16
    ldr D<m6_p0hi>, [x10]
    add x10, x7, #144
    ldr Q<m6_p1lo>, [x10]
    add x10, x10, #16
    ldr D<m6_p1hi>, [x10]
    add x11, x0, #432
    ldr Q<m6_idx0>, [x9, #0]
    tbl V<m6_part0>.16b, {V<m6_p0lo>.16b, V<m6_p0hi>.16b}, V<m6_idx0>.16b
    ldr Q<m6_idx1>, [x9, #16]
    tbl V<m6_part1>.16b, {V<m6_p1lo>.16b, V<m6_p1hi>.16b}, V<m6_idx1>.16b
    ldr Q<m6_idx2>, [x9, #32]
    tbl V<m6_part2>.16b, {V<lo2>.16b, V<mid2>.16b, V<hi2>.16b}, V<m6_idx2>.16b
    orr V<m6_out0>.16b, V<m6_part0>.16b, V<m6_part1>.16b
    orr V<m6_out0>.16b, V<m6_out0>.16b, V<m6_part2>.16b
    str Q<m6_out0>, [x11, #0]
    ldr Q<m6_idx3>, [x9, #48]
    tbl V<m6_part3>.16b, {V<m6_p0lo>.16b, V<m6_p0hi>.16b}, V<m6_idx3>.16b
    ldr Q<m6_idx4>, [x9, #64]
    tbl V<m6_part4>.16b, {V<m6_p1lo>.16b, V<m6_p1hi>.16b}, V<m6_idx4>.16b
    ldr Q<m6_idx5>, [x9, #80]
    tbl V<m6_part5>.16b, {V<lo2>.16b, V<mid2>.16b, V<hi2>.16b}, V<m6_idx5>.16b
    orr V<m6_out1>.16b, V<m6_part3>.16b, V<m6_part4>.16b
    orr V<m6_out1>.16b, V<m6_out1>.16b, V<m6_part5>.16b
    str Q<m6_out1>, [x11, #16]
    ldr Q<m6_idx6>, [x9, #96]
    tbl V<m6_part6>.16b, {V<m6_p0lo>.16b, V<m6_p0hi>.16b}, V<m6_idx6>.16b
    ldr Q<m6_idx7>, [x9, #112]
    tbl V<m6_part7>.16b, {V<m6_p1lo>.16b, V<m6_p1hi>.16b}, V<m6_idx7>.16b
    ldr Q<m6_idx8>, [x9, #128]
    tbl V<m6_part8>.16b, {V<lo2>.16b, V<mid2>.16b, V<hi2>.16b}, V<m6_idx8>.16b
    orr V<m6_out2>.16b, V<m6_part6>.16b, V<m6_part7>.16b
    orr V<m6_out2>.16b, V<m6_out2>.16b, V<m6_part8>.16b
    str Q<m6_out2>, [x11, #32]
    ldr Q<m6_idx9>, [x9, #144]
    tbl V<m6_part9>.16b, {V<m6_p0lo>.16b, V<m6_p0hi>.16b}, V<m6_idx9>.16b
    ldr Q<m6_idx10>, [x9, #160]
    tbl V<m6_part10>.16b, {V<m6_p1lo>.16b, V<m6_p1hi>.16b}, V<m6_idx10>.16b
    ldr Q<m6_idx11>, [x9, #176]
    tbl V<m6_part11>.16b, {V<lo2>.16b, V<mid2>.16b, V<hi2>.16b}, V<m6_idx11>.16b
    orr V<m6_out3>.16b, V<m6_part9>.16b, V<m6_part10>.16b
    orr V<m6_out3>.16b, V<m6_out3>.16b, V<m6_part11>.16b
    str Q<m6_out3>, [x11, #48]
    ldr Q<m6_idx12>, [x9, #192]
    tbl V<m6_part12>.16b, {V<m6_p0lo>.16b, V<m6_p0hi>.16b}, V<m6_idx12>.16b
    ldr Q<m6_idx13>, [x9, #208]
    tbl V<m6_part13>.16b, {V<m6_p1lo>.16b, V<m6_p1hi>.16b}, V<m6_idx13>.16b
    ldr Q<m6_idx14>, [x9, #224]
    tbl V<m6_part14>.16b, {V<lo2>.16b, V<mid2>.16b, V<hi2>.16b}, V<m6_idx14>.16b
    orr V<m6_out4>.16b, V<m6_part12>.16b, V<m6_part13>.16b
    orr V<m6_out4>.16b, V<m6_out4>.16b, V<m6_part14>.16b
    str D<m6_out4>, [x11, #64]
    // ROW 3: create only this pair; t2 dies after this row when applicable
    ldr Q<idx3>, [x4, #48]
    ldr Q<mask3>, [x3, #32]
    and V<arow3>.16b, V<at2>.16b, V<mask3>.16b
    bic V<aother3>.16b, V<at3>.16b, V<mask3>.16b
    orr V<arow3>.16b, V<arow3>.16b, V<aother3>.16b
    ins V<arow3>.h[3], V<aninth>.h[3]
    tbl V<arow3>.16b, {V<arow3>.16b}, V<idx3>.16b
    sshr V<asign3>.8h, V<arow3>.8h, #15
    and V<asign3>.16b, V<asign3>.16b, V<q>.16b
    add V<arow3>.8h, V<arow3>.8h, V<asign3>.8h
    and V<brow3>.16b, V<bt2>.16b, V<mask3>.16b
    bic V<bother3>.16b, V<bt3>.16b, V<mask3>.16b
    orr V<brow3>.16b, V<brow3>.16b, V<bother3>.16b
    ins V<brow3>.h[3], V<bninth>.h[3]
    tbl V<brow3>.16b, {V<brow3>.16b}, V<idx3>.16b
    sshr V<bsign3>.8h, V<brow3>.8h, #15
    and V<bsign3>.16b, V<bsign3>.16b, V<q>.16b
    add V<brow3>.8h, V<brow3>.8h, V<bsign3>.8h
    xtn V<lo3>.8b, V<arow3>.8h
    ushr V<mix3>.8h, V<arow3>.8h, #8
    sli V<mix3>.8h, V<brow3>.8h, #4
    xtn V<mid3>.8b, V<mix3>.8h
    ushr V<brow3>.8h, V<brow3>.8h, #4
    xtn V<hi3>.8b, V<brow3>.8h
    add x10, x6, #24
    ldr Q<m1_p0lo>, [x10]
    add x10, x10, #16
    ldr D<m1_p0hi>, [x10]
    add x10, x7, #24
    ldr Q<m1_p1lo>, [x10]
    add x10, x10, #16
    ldr D<m1_p1hi>, [x10]
    add x11, x0, #72
    ldr Q<m1_idx0>, [x9, #0]
    tbl V<m1_part0>.16b, {V<m1_p0lo>.16b, V<m1_p0hi>.16b}, V<m1_idx0>.16b
    ldr Q<m1_idx1>, [x9, #16]
    tbl V<m1_part1>.16b, {V<m1_p1lo>.16b, V<m1_p1hi>.16b}, V<m1_idx1>.16b
    ldr Q<m1_idx2>, [x9, #32]
    tbl V<m1_part2>.16b, {V<lo3>.16b, V<mid3>.16b, V<hi3>.16b}, V<m1_idx2>.16b
    orr V<m1_out0>.16b, V<m1_part0>.16b, V<m1_part1>.16b
    orr V<m1_out0>.16b, V<m1_out0>.16b, V<m1_part2>.16b
    str Q<m1_out0>, [x11, #0]
    ldr Q<m1_idx3>, [x9, #48]
    tbl V<m1_part3>.16b, {V<m1_p0lo>.16b, V<m1_p0hi>.16b}, V<m1_idx3>.16b
    ldr Q<m1_idx4>, [x9, #64]
    tbl V<m1_part4>.16b, {V<m1_p1lo>.16b, V<m1_p1hi>.16b}, V<m1_idx4>.16b
    ldr Q<m1_idx5>, [x9, #80]
    tbl V<m1_part5>.16b, {V<lo3>.16b, V<mid3>.16b, V<hi3>.16b}, V<m1_idx5>.16b
    orr V<m1_out1>.16b, V<m1_part3>.16b, V<m1_part4>.16b
    orr V<m1_out1>.16b, V<m1_out1>.16b, V<m1_part5>.16b
    str Q<m1_out1>, [x11, #16]
    ldr Q<m1_idx6>, [x9, #96]
    tbl V<m1_part6>.16b, {V<m1_p0lo>.16b, V<m1_p0hi>.16b}, V<m1_idx6>.16b
    ldr Q<m1_idx7>, [x9, #112]
    tbl V<m1_part7>.16b, {V<m1_p1lo>.16b, V<m1_p1hi>.16b}, V<m1_idx7>.16b
    ldr Q<m1_idx8>, [x9, #128]
    tbl V<m1_part8>.16b, {V<lo3>.16b, V<mid3>.16b, V<hi3>.16b}, V<m1_idx8>.16b
    orr V<m1_out2>.16b, V<m1_part6>.16b, V<m1_part7>.16b
    orr V<m1_out2>.16b, V<m1_out2>.16b, V<m1_part8>.16b
    str Q<m1_out2>, [x11, #32]
    ldr Q<m1_idx9>, [x9, #144]
    tbl V<m1_part9>.16b, {V<m1_p0lo>.16b, V<m1_p0hi>.16b}, V<m1_idx9>.16b
    ldr Q<m1_idx10>, [x9, #160]
    tbl V<m1_part10>.16b, {V<m1_p1lo>.16b, V<m1_p1hi>.16b}, V<m1_idx10>.16b
    ldr Q<m1_idx11>, [x9, #176]
    tbl V<m1_part11>.16b, {V<lo3>.16b, V<mid3>.16b, V<hi3>.16b}, V<m1_idx11>.16b
    orr V<m1_out3>.16b, V<m1_part9>.16b, V<m1_part10>.16b
    orr V<m1_out3>.16b, V<m1_out3>.16b, V<m1_part11>.16b
    str Q<m1_out3>, [x11, #48]
    ldr Q<m1_idx12>, [x9, #192]
    tbl V<m1_part12>.16b, {V<m1_p0lo>.16b, V<m1_p0hi>.16b}, V<m1_idx12>.16b
    ldr Q<m1_idx13>, [x9, #208]
    tbl V<m1_part13>.16b, {V<m1_p1lo>.16b, V<m1_p1hi>.16b}, V<m1_idx13>.16b
    ldr Q<m1_idx14>, [x9, #224]
    tbl V<m1_part14>.16b, {V<lo3>.16b, V<mid3>.16b, V<hi3>.16b}, V<m1_idx14>.16b
    orr V<m1_out4>.16b, V<m1_part12>.16b, V<m1_part13>.16b
    orr V<m1_out4>.16b, V<m1_out4>.16b, V<m1_part14>.16b
    str D<m1_out4>, [x11, #64]
    // ROW 4: create only this pair; t3 dies after this row when applicable
    ldr Q<idx4>, [x4, #64]
    ldr Q<mask4>, [x3, #48]
    and V<arow4>.16b, V<at3>.16b, V<mask4>.16b
    bic V<aother4>.16b, V<at4>.16b, V<mask4>.16b
    orr V<arow4>.16b, V<arow4>.16b, V<aother4>.16b
    ins V<arow4>.h[4], V<aninth>.h[4]
    tbl V<arow4>.16b, {V<arow4>.16b}, V<idx4>.16b
    sshr V<asign4>.8h, V<arow4>.8h, #15
    and V<asign4>.16b, V<asign4>.16b, V<q>.16b
    add V<arow4>.8h, V<arow4>.8h, V<asign4>.8h
    and V<brow4>.16b, V<bt3>.16b, V<mask4>.16b
    bic V<bother4>.16b, V<bt4>.16b, V<mask4>.16b
    orr V<brow4>.16b, V<brow4>.16b, V<bother4>.16b
    ins V<brow4>.h[4], V<bninth>.h[4]
    tbl V<brow4>.16b, {V<brow4>.16b}, V<idx4>.16b
    sshr V<bsign4>.8h, V<brow4>.8h, #15
    and V<bsign4>.16b, V<bsign4>.16b, V<q>.16b
    add V<brow4>.8h, V<brow4>.8h, V<bsign4>.8h
    xtn V<lo4>.8b, V<arow4>.8h
    ushr V<mix4>.8h, V<arow4>.8h, #8
    sli V<mix4>.8h, V<brow4>.8h, #4
    xtn V<mid4>.8b, V<mix4>.8h
    ushr V<brow4>.8h, V<brow4>.8h, #4
    xtn V<hi4>.8b, V<brow4>.8h
    add x10, x6, #96
    ldr Q<m4_p0lo>, [x10]
    add x10, x10, #16
    ldr D<m4_p0hi>, [x10]
    add x10, x7, #96
    ldr Q<m4_p1lo>, [x10]
    add x10, x10, #16
    ldr D<m4_p1hi>, [x10]
    add x11, x0, #288
    ldr Q<m4_idx0>, [x9, #0]
    tbl V<m4_part0>.16b, {V<m4_p0lo>.16b, V<m4_p0hi>.16b}, V<m4_idx0>.16b
    ldr Q<m4_idx1>, [x9, #16]
    tbl V<m4_part1>.16b, {V<m4_p1lo>.16b, V<m4_p1hi>.16b}, V<m4_idx1>.16b
    ldr Q<m4_idx2>, [x9, #32]
    tbl V<m4_part2>.16b, {V<lo4>.16b, V<mid4>.16b, V<hi4>.16b}, V<m4_idx2>.16b
    orr V<m4_out0>.16b, V<m4_part0>.16b, V<m4_part1>.16b
    orr V<m4_out0>.16b, V<m4_out0>.16b, V<m4_part2>.16b
    str Q<m4_out0>, [x11, #0]
    ldr Q<m4_idx3>, [x9, #48]
    tbl V<m4_part3>.16b, {V<m4_p0lo>.16b, V<m4_p0hi>.16b}, V<m4_idx3>.16b
    ldr Q<m4_idx4>, [x9, #64]
    tbl V<m4_part4>.16b, {V<m4_p1lo>.16b, V<m4_p1hi>.16b}, V<m4_idx4>.16b
    ldr Q<m4_idx5>, [x9, #80]
    tbl V<m4_part5>.16b, {V<lo4>.16b, V<mid4>.16b, V<hi4>.16b}, V<m4_idx5>.16b
    orr V<m4_out1>.16b, V<m4_part3>.16b, V<m4_part4>.16b
    orr V<m4_out1>.16b, V<m4_out1>.16b, V<m4_part5>.16b
    str Q<m4_out1>, [x11, #16]
    ldr Q<m4_idx6>, [x9, #96]
    tbl V<m4_part6>.16b, {V<m4_p0lo>.16b, V<m4_p0hi>.16b}, V<m4_idx6>.16b
    ldr Q<m4_idx7>, [x9, #112]
    tbl V<m4_part7>.16b, {V<m4_p1lo>.16b, V<m4_p1hi>.16b}, V<m4_idx7>.16b
    ldr Q<m4_idx8>, [x9, #128]
    tbl V<m4_part8>.16b, {V<lo4>.16b, V<mid4>.16b, V<hi4>.16b}, V<m4_idx8>.16b
    orr V<m4_out2>.16b, V<m4_part6>.16b, V<m4_part7>.16b
    orr V<m4_out2>.16b, V<m4_out2>.16b, V<m4_part8>.16b
    str Q<m4_out2>, [x11, #32]
    ldr Q<m4_idx9>, [x9, #144]
    tbl V<m4_part9>.16b, {V<m4_p0lo>.16b, V<m4_p0hi>.16b}, V<m4_idx9>.16b
    ldr Q<m4_idx10>, [x9, #160]
    tbl V<m4_part10>.16b, {V<m4_p1lo>.16b, V<m4_p1hi>.16b}, V<m4_idx10>.16b
    ldr Q<m4_idx11>, [x9, #176]
    tbl V<m4_part11>.16b, {V<lo4>.16b, V<mid4>.16b, V<hi4>.16b}, V<m4_idx11>.16b
    orr V<m4_out3>.16b, V<m4_part9>.16b, V<m4_part10>.16b
    orr V<m4_out3>.16b, V<m4_out3>.16b, V<m4_part11>.16b
    str Q<m4_out3>, [x11, #48]
    ldr Q<m4_idx12>, [x9, #192]
    tbl V<m4_part12>.16b, {V<m4_p0lo>.16b, V<m4_p0hi>.16b}, V<m4_idx12>.16b
    ldr Q<m4_idx13>, [x9, #208]
    tbl V<m4_part13>.16b, {V<m4_p1lo>.16b, V<m4_p1hi>.16b}, V<m4_idx13>.16b
    ldr Q<m4_idx14>, [x9, #224]
    tbl V<m4_part14>.16b, {V<lo4>.16b, V<mid4>.16b, V<hi4>.16b}, V<m4_idx14>.16b
    orr V<m4_out4>.16b, V<m4_part12>.16b, V<m4_part13>.16b
    orr V<m4_out4>.16b, V<m4_out4>.16b, V<m4_part14>.16b
    str D<m4_out4>, [x11, #64]
    // ROW 5: create only this pair; t4 dies after this row when applicable
    ldr Q<idx5>, [x4, #80]
    ldr Q<mask5>, [x3, #64]
    and V<arow5>.16b, V<at4>.16b, V<mask5>.16b
    bic V<aother5>.16b, V<at5>.16b, V<mask5>.16b
    orr V<arow5>.16b, V<arow5>.16b, V<aother5>.16b
    ins V<arow5>.h[5], V<aninth>.h[5]
    tbl V<arow5>.16b, {V<arow5>.16b}, V<idx5>.16b
    sshr V<asign5>.8h, V<arow5>.8h, #15
    and V<asign5>.16b, V<asign5>.16b, V<q>.16b
    add V<arow5>.8h, V<arow5>.8h, V<asign5>.8h
    and V<brow5>.16b, V<bt4>.16b, V<mask5>.16b
    bic V<bother5>.16b, V<bt5>.16b, V<mask5>.16b
    orr V<brow5>.16b, V<brow5>.16b, V<bother5>.16b
    ins V<brow5>.h[5], V<bninth>.h[5]
    tbl V<brow5>.16b, {V<brow5>.16b}, V<idx5>.16b
    sshr V<bsign5>.8h, V<brow5>.8h, #15
    and V<bsign5>.16b, V<bsign5>.16b, V<q>.16b
    add V<brow5>.8h, V<brow5>.8h, V<bsign5>.8h
    xtn V<lo5>.8b, V<arow5>.8h
    ushr V<mix5>.8h, V<arow5>.8h, #8
    sli V<mix5>.8h, V<brow5>.8h, #4
    xtn V<mid5>.8b, V<mix5>.8h
    ushr V<brow5>.8h, V<brow5>.8h, #4
    xtn V<hi5>.8b, V<brow5>.8h
    add x10, x6, #168
    ldr Q<m7_p0lo>, [x10]
    add x10, x10, #16
    ldr D<m7_p0hi>, [x10]
    add x10, x7, #168
    ldr Q<m7_p1lo>, [x10]
    add x10, x10, #16
    ldr D<m7_p1hi>, [x10]
    add x11, x0, #504
    ldr Q<m7_idx0>, [x9, #0]
    tbl V<m7_part0>.16b, {V<m7_p0lo>.16b, V<m7_p0hi>.16b}, V<m7_idx0>.16b
    ldr Q<m7_idx1>, [x9, #16]
    tbl V<m7_part1>.16b, {V<m7_p1lo>.16b, V<m7_p1hi>.16b}, V<m7_idx1>.16b
    ldr Q<m7_idx2>, [x9, #32]
    tbl V<m7_part2>.16b, {V<lo5>.16b, V<mid5>.16b, V<hi5>.16b}, V<m7_idx2>.16b
    orr V<m7_out0>.16b, V<m7_part0>.16b, V<m7_part1>.16b
    orr V<m7_out0>.16b, V<m7_out0>.16b, V<m7_part2>.16b
    str Q<m7_out0>, [x11, #0]
    ldr Q<m7_idx3>, [x9, #48]
    tbl V<m7_part3>.16b, {V<m7_p0lo>.16b, V<m7_p0hi>.16b}, V<m7_idx3>.16b
    ldr Q<m7_idx4>, [x9, #64]
    tbl V<m7_part4>.16b, {V<m7_p1lo>.16b, V<m7_p1hi>.16b}, V<m7_idx4>.16b
    ldr Q<m7_idx5>, [x9, #80]
    tbl V<m7_part5>.16b, {V<lo5>.16b, V<mid5>.16b, V<hi5>.16b}, V<m7_idx5>.16b
    orr V<m7_out1>.16b, V<m7_part3>.16b, V<m7_part4>.16b
    orr V<m7_out1>.16b, V<m7_out1>.16b, V<m7_part5>.16b
    str Q<m7_out1>, [x11, #16]
    ldr Q<m7_idx6>, [x9, #96]
    tbl V<m7_part6>.16b, {V<m7_p0lo>.16b, V<m7_p0hi>.16b}, V<m7_idx6>.16b
    ldr Q<m7_idx7>, [x9, #112]
    tbl V<m7_part7>.16b, {V<m7_p1lo>.16b, V<m7_p1hi>.16b}, V<m7_idx7>.16b
    ldr Q<m7_idx8>, [x9, #128]
    tbl V<m7_part8>.16b, {V<lo5>.16b, V<mid5>.16b, V<hi5>.16b}, V<m7_idx8>.16b
    orr V<m7_out2>.16b, V<m7_part6>.16b, V<m7_part7>.16b
    orr V<m7_out2>.16b, V<m7_out2>.16b, V<m7_part8>.16b
    str Q<m7_out2>, [x11, #32]
    ldr Q<m7_idx9>, [x9, #144]
    tbl V<m7_part9>.16b, {V<m7_p0lo>.16b, V<m7_p0hi>.16b}, V<m7_idx9>.16b
    ldr Q<m7_idx10>, [x9, #160]
    tbl V<m7_part10>.16b, {V<m7_p1lo>.16b, V<m7_p1hi>.16b}, V<m7_idx10>.16b
    ldr Q<m7_idx11>, [x9, #176]
    tbl V<m7_part11>.16b, {V<lo5>.16b, V<mid5>.16b, V<hi5>.16b}, V<m7_idx11>.16b
    orr V<m7_out3>.16b, V<m7_part9>.16b, V<m7_part10>.16b
    orr V<m7_out3>.16b, V<m7_out3>.16b, V<m7_part11>.16b
    str Q<m7_out3>, [x11, #48]
    ldr Q<m7_idx12>, [x9, #192]
    tbl V<m7_part12>.16b, {V<m7_p0lo>.16b, V<m7_p0hi>.16b}, V<m7_idx12>.16b
    ldr Q<m7_idx13>, [x9, #208]
    tbl V<m7_part13>.16b, {V<m7_p1lo>.16b, V<m7_p1hi>.16b}, V<m7_idx13>.16b
    ldr Q<m7_idx14>, [x9, #224]
    tbl V<m7_part14>.16b, {V<lo5>.16b, V<mid5>.16b, V<hi5>.16b}, V<m7_idx14>.16b
    orr V<m7_out4>.16b, V<m7_part12>.16b, V<m7_part13>.16b
    orr V<m7_out4>.16b, V<m7_out4>.16b, V<m7_part14>.16b
    str D<m7_out4>, [x11, #64]
    // ROW 6: create only this pair; t5 dies after this row when applicable
    ldr Q<idx6>, [x4, #96]
    ldr Q<mask6>, [x3, #80]
    and V<arow6>.16b, V<at5>.16b, V<mask6>.16b
    bic V<aother6>.16b, V<at6>.16b, V<mask6>.16b
    orr V<arow6>.16b, V<arow6>.16b, V<aother6>.16b
    ins V<arow6>.h[6], V<aninth>.h[6]
    tbl V<arow6>.16b, {V<arow6>.16b}, V<idx6>.16b
    sshr V<asign6>.8h, V<arow6>.8h, #15
    and V<asign6>.16b, V<asign6>.16b, V<q>.16b
    add V<arow6>.8h, V<arow6>.8h, V<asign6>.8h
    and V<brow6>.16b, V<bt5>.16b, V<mask6>.16b
    bic V<bother6>.16b, V<bt6>.16b, V<mask6>.16b
    orr V<brow6>.16b, V<brow6>.16b, V<bother6>.16b
    ins V<brow6>.h[6], V<bninth>.h[6]
    tbl V<brow6>.16b, {V<brow6>.16b}, V<idx6>.16b
    sshr V<bsign6>.8h, V<brow6>.8h, #15
    and V<bsign6>.16b, V<bsign6>.16b, V<q>.16b
    add V<brow6>.8h, V<brow6>.8h, V<bsign6>.8h
    xtn V<lo6>.8b, V<arow6>.8h
    ushr V<mix6>.8h, V<arow6>.8h, #8
    sli V<mix6>.8h, V<brow6>.8h, #4
    xtn V<mid6>.8b, V<mix6>.8h
    ushr V<brow6>.8h, V<brow6>.8h, #4
    xtn V<hi6>.8b, V<brow6>.8h
    add x10, x6, #48
    ldr Q<m2_p0lo>, [x10]
    add x10, x10, #16
    ldr D<m2_p0hi>, [x10]
    add x10, x7, #48
    ldr Q<m2_p1lo>, [x10]
    add x10, x10, #16
    ldr D<m2_p1hi>, [x10]
    add x11, x0, #144
    ldr Q<m2_idx0>, [x9, #0]
    tbl V<m2_part0>.16b, {V<m2_p0lo>.16b, V<m2_p0hi>.16b}, V<m2_idx0>.16b
    ldr Q<m2_idx1>, [x9, #16]
    tbl V<m2_part1>.16b, {V<m2_p1lo>.16b, V<m2_p1hi>.16b}, V<m2_idx1>.16b
    ldr Q<m2_idx2>, [x9, #32]
    tbl V<m2_part2>.16b, {V<lo6>.16b, V<mid6>.16b, V<hi6>.16b}, V<m2_idx2>.16b
    orr V<m2_out0>.16b, V<m2_part0>.16b, V<m2_part1>.16b
    orr V<m2_out0>.16b, V<m2_out0>.16b, V<m2_part2>.16b
    str Q<m2_out0>, [x11, #0]
    ldr Q<m2_idx3>, [x9, #48]
    tbl V<m2_part3>.16b, {V<m2_p0lo>.16b, V<m2_p0hi>.16b}, V<m2_idx3>.16b
    ldr Q<m2_idx4>, [x9, #64]
    tbl V<m2_part4>.16b, {V<m2_p1lo>.16b, V<m2_p1hi>.16b}, V<m2_idx4>.16b
    ldr Q<m2_idx5>, [x9, #80]
    tbl V<m2_part5>.16b, {V<lo6>.16b, V<mid6>.16b, V<hi6>.16b}, V<m2_idx5>.16b
    orr V<m2_out1>.16b, V<m2_part3>.16b, V<m2_part4>.16b
    orr V<m2_out1>.16b, V<m2_out1>.16b, V<m2_part5>.16b
    str Q<m2_out1>, [x11, #16]
    ldr Q<m2_idx6>, [x9, #96]
    tbl V<m2_part6>.16b, {V<m2_p0lo>.16b, V<m2_p0hi>.16b}, V<m2_idx6>.16b
    ldr Q<m2_idx7>, [x9, #112]
    tbl V<m2_part7>.16b, {V<m2_p1lo>.16b, V<m2_p1hi>.16b}, V<m2_idx7>.16b
    ldr Q<m2_idx8>, [x9, #128]
    tbl V<m2_part8>.16b, {V<lo6>.16b, V<mid6>.16b, V<hi6>.16b}, V<m2_idx8>.16b
    orr V<m2_out2>.16b, V<m2_part6>.16b, V<m2_part7>.16b
    orr V<m2_out2>.16b, V<m2_out2>.16b, V<m2_part8>.16b
    str Q<m2_out2>, [x11, #32]
    ldr Q<m2_idx9>, [x9, #144]
    tbl V<m2_part9>.16b, {V<m2_p0lo>.16b, V<m2_p0hi>.16b}, V<m2_idx9>.16b
    ldr Q<m2_idx10>, [x9, #160]
    tbl V<m2_part10>.16b, {V<m2_p1lo>.16b, V<m2_p1hi>.16b}, V<m2_idx10>.16b
    ldr Q<m2_idx11>, [x9, #176]
    tbl V<m2_part11>.16b, {V<lo6>.16b, V<mid6>.16b, V<hi6>.16b}, V<m2_idx11>.16b
    orr V<m2_out3>.16b, V<m2_part9>.16b, V<m2_part10>.16b
    orr V<m2_out3>.16b, V<m2_out3>.16b, V<m2_part11>.16b
    str Q<m2_out3>, [x11, #48]
    ldr Q<m2_idx12>, [x9, #192]
    tbl V<m2_part12>.16b, {V<m2_p0lo>.16b, V<m2_p0hi>.16b}, V<m2_idx12>.16b
    ldr Q<m2_idx13>, [x9, #208]
    tbl V<m2_part13>.16b, {V<m2_p1lo>.16b, V<m2_p1hi>.16b}, V<m2_idx13>.16b
    ldr Q<m2_idx14>, [x9, #224]
    tbl V<m2_part14>.16b, {V<lo6>.16b, V<mid6>.16b, V<hi6>.16b}, V<m2_idx14>.16b
    orr V<m2_out4>.16b, V<m2_part12>.16b, V<m2_part13>.16b
    orr V<m2_out4>.16b, V<m2_out4>.16b, V<m2_part14>.16b
    str D<m2_out4>, [x11, #64]
    // ROW 7: create only this pair; t6 dies after this row when applicable
    ldr Q<idx7>, [x4, #112]
    orr V<arow7>.16b, V<at6>.16b, V<at6>.16b
    ins V<arow7>.h[7], V<aninth>.h[7]
    tbl V<arow7>.16b, {V<arow7>.16b}, V<idx7>.16b
    sshr V<asign7>.8h, V<arow7>.8h, #15
    and V<asign7>.16b, V<asign7>.16b, V<q>.16b
    add V<arow7>.8h, V<arow7>.8h, V<asign7>.8h
    orr V<brow7>.16b, V<bt6>.16b, V<bt6>.16b
    ins V<brow7>.h[7], V<bninth>.h[7]
    tbl V<brow7>.16b, {V<brow7>.16b}, V<idx7>.16b
    sshr V<bsign7>.8h, V<brow7>.8h, #15
    and V<bsign7>.16b, V<bsign7>.16b, V<q>.16b
    add V<brow7>.8h, V<brow7>.8h, V<bsign7>.8h
    xtn V<lo7>.8b, V<arow7>.8h
    ushr V<mix7>.8h, V<arow7>.8h, #8
    sli V<mix7>.8h, V<brow7>.8h, #4
    xtn V<mid7>.8b, V<mix7>.8h
    ushr V<brow7>.8h, V<brow7>.8h, #4
    xtn V<hi7>.8b, V<brow7>.8h
    add x10, x6, #120
    ldr Q<m5_p0lo>, [x10]
    add x10, x10, #16
    ldr D<m5_p0hi>, [x10]
    add x10, x7, #120
    ldr Q<m5_p1lo>, [x10]
    add x10, x10, #16
    ldr D<m5_p1hi>, [x10]
    add x11, x0, #360
    ldr Q<m5_idx0>, [x9, #0]
    tbl V<m5_part0>.16b, {V<m5_p0lo>.16b, V<m5_p0hi>.16b}, V<m5_idx0>.16b
    ldr Q<m5_idx1>, [x9, #16]
    tbl V<m5_part1>.16b, {V<m5_p1lo>.16b, V<m5_p1hi>.16b}, V<m5_idx1>.16b
    ldr Q<m5_idx2>, [x9, #32]
    tbl V<m5_part2>.16b, {V<lo7>.16b, V<mid7>.16b, V<hi7>.16b}, V<m5_idx2>.16b
    orr V<m5_out0>.16b, V<m5_part0>.16b, V<m5_part1>.16b
    orr V<m5_out0>.16b, V<m5_out0>.16b, V<m5_part2>.16b
    str Q<m5_out0>, [x11, #0]
    ldr Q<m5_idx3>, [x9, #48]
    tbl V<m5_part3>.16b, {V<m5_p0lo>.16b, V<m5_p0hi>.16b}, V<m5_idx3>.16b
    ldr Q<m5_idx4>, [x9, #64]
    tbl V<m5_part4>.16b, {V<m5_p1lo>.16b, V<m5_p1hi>.16b}, V<m5_idx4>.16b
    ldr Q<m5_idx5>, [x9, #80]
    tbl V<m5_part5>.16b, {V<lo7>.16b, V<mid7>.16b, V<hi7>.16b}, V<m5_idx5>.16b
    orr V<m5_out1>.16b, V<m5_part3>.16b, V<m5_part4>.16b
    orr V<m5_out1>.16b, V<m5_out1>.16b, V<m5_part5>.16b
    str Q<m5_out1>, [x11, #16]
    ldr Q<m5_idx6>, [x9, #96]
    tbl V<m5_part6>.16b, {V<m5_p0lo>.16b, V<m5_p0hi>.16b}, V<m5_idx6>.16b
    ldr Q<m5_idx7>, [x9, #112]
    tbl V<m5_part7>.16b, {V<m5_p1lo>.16b, V<m5_p1hi>.16b}, V<m5_idx7>.16b
    ldr Q<m5_idx8>, [x9, #128]
    tbl V<m5_part8>.16b, {V<lo7>.16b, V<mid7>.16b, V<hi7>.16b}, V<m5_idx8>.16b
    orr V<m5_out2>.16b, V<m5_part6>.16b, V<m5_part7>.16b
    orr V<m5_out2>.16b, V<m5_out2>.16b, V<m5_part8>.16b
    str Q<m5_out2>, [x11, #32]
    ldr Q<m5_idx9>, [x9, #144]
    tbl V<m5_part9>.16b, {V<m5_p0lo>.16b, V<m5_p0hi>.16b}, V<m5_idx9>.16b
    ldr Q<m5_idx10>, [x9, #160]
    tbl V<m5_part10>.16b, {V<m5_p1lo>.16b, V<m5_p1hi>.16b}, V<m5_idx10>.16b
    ldr Q<m5_idx11>, [x9, #176]
    tbl V<m5_part11>.16b, {V<lo7>.16b, V<mid7>.16b, V<hi7>.16b}, V<m5_idx11>.16b
    orr V<m5_out3>.16b, V<m5_part9>.16b, V<m5_part10>.16b
    orr V<m5_out3>.16b, V<m5_out3>.16b, V<m5_part11>.16b
    str Q<m5_out3>, [x11, #48]
    ldr Q<m5_idx12>, [x9, #192]
    tbl V<m5_part12>.16b, {V<m5_p0lo>.16b, V<m5_p0hi>.16b}, V<m5_idx12>.16b
    ldr Q<m5_idx13>, [x9, #208]
    tbl V<m5_part13>.16b, {V<m5_p1lo>.16b, V<m5_p1hi>.16b}, V<m5_idx13>.16b
    ldr Q<m5_idx14>, [x9, #224]
    tbl V<m5_part14>.16b, {V<lo7>.16b, V<mid7>.16b, V<hi7>.16b}, V<m5_idx14>.16b
    orr V<m5_out4>.16b, V<m5_part12>.16b, V<m5_part13>.16b
    orr V<m5_out4>.16b, V<m5_out4>.16b, V<m5_part14>.16b
    str D<m5_out4>, [x11, #64]
    // ROW 8: create only this pair; t7 dies after this row when applicable
    ldr Q<idx8>, [x4, #128]
    orr V<arow8>.16b, V<at7>.16b, V<at7>.16b
    tbl V<arow8>.16b, {V<arow8>.16b}, V<idx8>.16b
    sshr V<asign8>.8h, V<arow8>.8h, #15
    and V<asign8>.16b, V<asign8>.16b, V<q>.16b
    add V<arow8>.8h, V<arow8>.8h, V<asign8>.8h
    orr V<brow8>.16b, V<bt7>.16b, V<bt7>.16b
    tbl V<brow8>.16b, {V<brow8>.16b}, V<idx8>.16b
    sshr V<bsign8>.8h, V<brow8>.8h, #15
    and V<bsign8>.16b, V<bsign8>.16b, V<q>.16b
    add V<brow8>.8h, V<brow8>.8h, V<bsign8>.8h
    xtn V<lo8>.8b, V<arow8>.8h
    ushr V<mix8>.8h, V<arow8>.8h, #8
    sli V<mix8>.8h, V<brow8>.8h, #4
    xtn V<mid8>.8b, V<mix8>.8h
    ushr V<brow8>.8h, V<brow8>.8h, #4
    xtn V<hi8>.8b, V<brow8>.8h
    add x10, x6, #192
    ldr Q<m8_p0lo>, [x10]
    add x10, x10, #16
    ldr D<m8_p0hi>, [x10]
    add x10, x7, #192
    ldr Q<m8_p1lo>, [x10]
    add x10, x10, #16
    ldr D<m8_p1hi>, [x10]
    add x11, x0, #576
    ldr Q<m8_idx0>, [x9, #0]
    tbl V<m8_part0>.16b, {V<m8_p0lo>.16b, V<m8_p0hi>.16b}, V<m8_idx0>.16b
    ldr Q<m8_idx1>, [x9, #16]
    tbl V<m8_part1>.16b, {V<m8_p1lo>.16b, V<m8_p1hi>.16b}, V<m8_idx1>.16b
    ldr Q<m8_idx2>, [x9, #32]
    tbl V<m8_part2>.16b, {V<lo8>.16b, V<mid8>.16b, V<hi8>.16b}, V<m8_idx2>.16b
    orr V<m8_out0>.16b, V<m8_part0>.16b, V<m8_part1>.16b
    orr V<m8_out0>.16b, V<m8_out0>.16b, V<m8_part2>.16b
    str Q<m8_out0>, [x11, #0]
    ldr Q<m8_idx3>, [x9, #48]
    tbl V<m8_part3>.16b, {V<m8_p0lo>.16b, V<m8_p0hi>.16b}, V<m8_idx3>.16b
    ldr Q<m8_idx4>, [x9, #64]
    tbl V<m8_part4>.16b, {V<m8_p1lo>.16b, V<m8_p1hi>.16b}, V<m8_idx4>.16b
    ldr Q<m8_idx5>, [x9, #80]
    tbl V<m8_part5>.16b, {V<lo8>.16b, V<mid8>.16b, V<hi8>.16b}, V<m8_idx5>.16b
    orr V<m8_out1>.16b, V<m8_part3>.16b, V<m8_part4>.16b
    orr V<m8_out1>.16b, V<m8_out1>.16b, V<m8_part5>.16b
    str Q<m8_out1>, [x11, #16]
    ldr Q<m8_idx6>, [x9, #96]
    tbl V<m8_part6>.16b, {V<m8_p0lo>.16b, V<m8_p0hi>.16b}, V<m8_idx6>.16b
    ldr Q<m8_idx7>, [x9, #112]
    tbl V<m8_part7>.16b, {V<m8_p1lo>.16b, V<m8_p1hi>.16b}, V<m8_idx7>.16b
    ldr Q<m8_idx8>, [x9, #128]
    tbl V<m8_part8>.16b, {V<lo8>.16b, V<mid8>.16b, V<hi8>.16b}, V<m8_idx8>.16b
    orr V<m8_out2>.16b, V<m8_part6>.16b, V<m8_part7>.16b
    orr V<m8_out2>.16b, V<m8_out2>.16b, V<m8_part8>.16b
    str Q<m8_out2>, [x11, #32]
    ldr Q<m8_idx9>, [x9, #144]
    tbl V<m8_part9>.16b, {V<m8_p0lo>.16b, V<m8_p0hi>.16b}, V<m8_idx9>.16b
    ldr Q<m8_idx10>, [x9, #160]
    tbl V<m8_part10>.16b, {V<m8_p1lo>.16b, V<m8_p1hi>.16b}, V<m8_idx10>.16b
    ldr Q<m8_idx11>, [x9, #176]
    tbl V<m8_part11>.16b, {V<lo8>.16b, V<mid8>.16b, V<hi8>.16b}, V<m8_idx11>.16b
    orr V<m8_out3>.16b, V<m8_part9>.16b, V<m8_part10>.16b
    orr V<m8_out3>.16b, V<m8_out3>.16b, V<m8_part11>.16b
    str Q<m8_out3>, [x11, #48]
    ldr Q<m8_idx12>, [x9, #192]
    tbl V<m8_part12>.16b, {V<m8_p0lo>.16b, V<m8_p0hi>.16b}, V<m8_idx12>.16b
    ldr Q<m8_idx13>, [x9, #208]
    tbl V<m8_part13>.16b, {V<m8_p1lo>.16b, V<m8_p1hi>.16b}, V<m8_idx13>.16b
    ldr Q<m8_idx14>, [x9, #224]
    tbl V<m8_part14>.16b, {V<lo8>.16b, V<mid8>.16b, V<hi8>.16b}, V<m8_idx14>.16b
    orr V<m8_out4>.16b, V<m8_part12>.16b, V<m8_part13>.16b
    orr V<m8_out4>.16b, V<m8_out4>.16b, V<m8_part14>.16b
    str D<m8_out4>, [x11, #64]
pair_merge_small_slothy_end:
    ret
