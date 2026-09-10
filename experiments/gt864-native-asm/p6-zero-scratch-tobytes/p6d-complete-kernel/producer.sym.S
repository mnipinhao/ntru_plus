.text
.global gt864_p6d_pair0
gt864_p6d_pair0:
// synthetic allocation region; x29 coefficient base, x30 combined-table base, sp live-out sink.
gt864_p6d_pair0_start:
    ldr Q<aj0>, [x29, #384]
    ldr Q<aj1>, [x29, #336]
    ext V<aj1>.16b, V<aj1>.16b, V<aj1>.16b, #14
    ldr Q<aj2>, [x29, #288]
    ext V<aj2>.16b, V<aj2>.16b, V<aj2>.16b, #12
    ldr Q<aj3>, [x29, #240]
    ext V<aj3>.16b, V<aj3>.16b, V<aj3>.16b, #10
    ldr Q<aj4>, [x29, #192]
    ext V<aj4>.16b, V<aj4>.16b, V<aj4>.16b, #8
    ldr Q<aj5>, [x29, #144]
    ext V<aj5>.16b, V<aj5>.16b, V<aj5>.16b, #6
    ldr Q<aj6>, [x29, #96]
    ext V<aj6>.16b, V<aj6>.16b, V<aj6>.16b, #4
    ldr Q<aj7>, [x29, #48]
    ext V<aj7>.16b, V<aj7>.16b, V<aj7>.16b, #2
    ldr Q<aninth>, [x29, #0]
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
    ldr Q<bj0>, [x29, #400]
    ldr Q<bj1>, [x29, #352]
    ext V<bj1>.16b, V<bj1>.16b, V<bj1>.16b, #14
    ldr Q<bj2>, [x29, #304]
    ext V<bj2>.16b, V<bj2>.16b, V<bj2>.16b, #12
    ldr Q<bj3>, [x29, #256]
    ext V<bj3>.16b, V<bj3>.16b, V<bj3>.16b, #10
    ldr Q<bj4>, [x29, #208]
    ext V<bj4>.16b, V<bj4>.16b, V<bj4>.16b, #8
    ldr Q<bj5>, [x29, #160]
    ext V<bj5>.16b, V<bj5>.16b, V<bj5>.16b, #6
    ldr Q<bj6>, [x29, #112]
    ext V<bj6>.16b, V<bj6>.16b, V<bj6>.16b, #4
    ldr Q<bj7>, [x29, #64]
    ext V<bj7>.16b, V<bj7>.16b, V<bj7>.16b, #2
    ldr Q<bninth>, [x29, #16]
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
    ldr Q<q>, [x30, #336]
    ldr Q<recip>, [x30, #352]
    // ROW 0: create only this pair; t-1 dies after this row when applicable
    ldr Q<idx0>, [x30, #160]
    orr V<arow0>.16b, V<at0>.16b, V<at0>.16b
    ins V<arow0>.h[0], V<aninth>.h[0]
    tbl V<arow0>.16b, {V<arow0>.16b}, V<idx0>.16b
    sqrdmulh V<aquot0>.8h, V<arow0>.8h, V<recip>.8h
    mls V<arow0>.8h, V<aquot0>.8h, V<q>.8h
    sshr V<asign0>.8h, V<arow0>.8h, #15
    and V<asign0>.16b, V<asign0>.16b, V<q>.16b
    add V<arow0>.8h, V<arow0>.8h, V<asign0>.8h
    orr V<brow0>.16b, V<bt0>.16b, V<bt0>.16b
    ins V<brow0>.h[0], V<bninth>.h[0]
    tbl V<brow0>.16b, {V<brow0>.16b}, V<idx0>.16b
    sqrdmulh V<bquot0>.8h, V<brow0>.8h, V<recip>.8h
    mls V<brow0>.8h, V<bquot0>.8h, V<q>.8h
    sshr V<bsign0>.8h, V<brow0>.8h, #15
    and V<bsign0>.16b, V<bsign0>.16b, V<q>.16b
    add V<brow0>.8h, V<brow0>.8h, V<bsign0>.8h
    xtn V<lo0>.8b, V<arow0>.8h
    ushr V<mix0>.8h, V<arow0>.8h, #8
    sli V<mix0>.8h, V<brow0>.8h, #4
    xtn V<mid0>.8b, V<mix0>.8h
    ushr V<brow0>.8h, V<brow0>.8h, #4
    xtn V<hi0>.8b, V<brow0>.8h
    ldr Q<p0idx0_0>, [x30, #304]
    tbl V<p0stream0_0>.16b, {V<lo0>.16b, V<mid0>.16b, V<hi0>.16b}, V<p0idx0_0>.16b
    ldr Q<p0idx1_0>, [x30, #320]
    tbl V<p0stream1_0>.16b, {V<lo0>.16b, V<mid0>.16b, V<hi0>.16b}, V<p0idx1_0>.16b
    umov X<p0d0>, V<p0stream0_0>.d[0]
    umov X<p0d1>, V<p0stream0_0>.d[1]
    umov X<p0d2>, V<p0stream1_0>.d[0]
    // ROW 1: create only this pair; t0 dies after this row when applicable
    ldr Q<idx1>, [x30, #176]
    ldr Q<mask1>, [x30, #0]
    and V<arow1>.16b, V<at0>.16b, V<mask1>.16b
    bic V<aother1>.16b, V<at1>.16b, V<mask1>.16b
    orr V<arow1>.16b, V<arow1>.16b, V<aother1>.16b
    ins V<arow1>.h[1], V<aninth>.h[1]
    tbl V<arow1>.16b, {V<arow1>.16b}, V<idx1>.16b
    sqrdmulh V<aquot1>.8h, V<arow1>.8h, V<recip>.8h
    mls V<arow1>.8h, V<aquot1>.8h, V<q>.8h
    sshr V<asign1>.8h, V<arow1>.8h, #15
    and V<asign1>.16b, V<asign1>.16b, V<q>.16b
    add V<arow1>.8h, V<arow1>.8h, V<asign1>.8h
    and V<brow1>.16b, V<bt0>.16b, V<mask1>.16b
    bic V<bother1>.16b, V<bt1>.16b, V<mask1>.16b
    orr V<brow1>.16b, V<brow1>.16b, V<bother1>.16b
    ins V<brow1>.h[1], V<bninth>.h[1]
    tbl V<brow1>.16b, {V<brow1>.16b}, V<idx1>.16b
    sqrdmulh V<bquot1>.8h, V<brow1>.8h, V<recip>.8h
    mls V<brow1>.8h, V<bquot1>.8h, V<q>.8h
    sshr V<bsign1>.8h, V<brow1>.8h, #15
    and V<bsign1>.16b, V<bsign1>.16b, V<q>.16b
    add V<brow1>.8h, V<brow1>.8h, V<bsign1>.8h
    xtn V<lo1>.8b, V<arow1>.8h
    ushr V<mix1>.8h, V<arow1>.8h, #8
    sli V<mix1>.8h, V<brow1>.8h, #4
    xtn V<mid1>.8b, V<mix1>.8h
    ushr V<brow1>.8h, V<brow1>.8h, #4
    xtn V<hi1>.8b, V<brow1>.8h
    ldr Q<p0idx0_1>, [x30, #304]
    tbl V<p0stream0_1>.16b, {V<lo1>.16b, V<mid1>.16b, V<hi1>.16b}, V<p0idx0_1>.16b
    ldr Q<p0idx1_1>, [x30, #320]
    tbl V<p0stream1_1>.16b, {V<lo1>.16b, V<mid1>.16b, V<hi1>.16b}, V<p0idx1_1>.16b
    umov X<p0d9>, V<p0stream0_1>.d[0]
    umov X<p0d10>, V<p0stream0_1>.d[1]
    umov X<p0d11>, V<p0stream1_1>.d[0]
    // ROW 2: create only this pair; t1 dies after this row when applicable
    ldr Q<idx2>, [x30, #192]
    ldr Q<mask2>, [x30, #16]
    and V<arow2>.16b, V<at1>.16b, V<mask2>.16b
    bic V<aother2>.16b, V<at2>.16b, V<mask2>.16b
    orr V<arow2>.16b, V<arow2>.16b, V<aother2>.16b
    ins V<arow2>.h[2], V<aninth>.h[2]
    tbl V<arow2>.16b, {V<arow2>.16b}, V<idx2>.16b
    sqrdmulh V<aquot2>.8h, V<arow2>.8h, V<recip>.8h
    mls V<arow2>.8h, V<aquot2>.8h, V<q>.8h
    sshr V<asign2>.8h, V<arow2>.8h, #15
    and V<asign2>.16b, V<asign2>.16b, V<q>.16b
    add V<arow2>.8h, V<arow2>.8h, V<asign2>.8h
    and V<brow2>.16b, V<bt1>.16b, V<mask2>.16b
    bic V<bother2>.16b, V<bt2>.16b, V<mask2>.16b
    orr V<brow2>.16b, V<brow2>.16b, V<bother2>.16b
    ins V<brow2>.h[2], V<bninth>.h[2]
    tbl V<brow2>.16b, {V<brow2>.16b}, V<idx2>.16b
    sqrdmulh V<bquot2>.8h, V<brow2>.8h, V<recip>.8h
    mls V<brow2>.8h, V<bquot2>.8h, V<q>.8h
    sshr V<bsign2>.8h, V<brow2>.8h, #15
    and V<bsign2>.16b, V<bsign2>.16b, V<q>.16b
    add V<brow2>.8h, V<brow2>.8h, V<bsign2>.8h
    xtn V<lo2>.8b, V<arow2>.8h
    ushr V<mix2>.8h, V<arow2>.8h, #8
    sli V<mix2>.8h, V<brow2>.8h, #4
    xtn V<mid2>.8b, V<mix2>.8h
    ushr V<brow2>.8h, V<brow2>.8h, #4
    xtn V<hi2>.8b, V<brow2>.8h
    ldr Q<p0idx0_2>, [x30, #304]
    tbl V<p0stream0_2>.16b, {V<lo2>.16b, V<mid2>.16b, V<hi2>.16b}, V<p0idx0_2>.16b
    ldr Q<p0idx1_2>, [x30, #320]
    tbl V<p0stream1_2>.16b, {V<lo2>.16b, V<mid2>.16b, V<hi2>.16b}, V<p0idx1_2>.16b
    umov X<p0d18>, V<p0stream0_2>.d[0]
    umov X<p0d19>, V<p0stream0_2>.d[1]
    umov X<p0d20>, V<p0stream1_2>.d[0]
    // ROW 3: create only this pair; t2 dies after this row when applicable
    ldr Q<idx3>, [x30, #208]
    ldr Q<mask3>, [x30, #32]
    and V<arow3>.16b, V<at2>.16b, V<mask3>.16b
    bic V<aother3>.16b, V<at3>.16b, V<mask3>.16b
    orr V<arow3>.16b, V<arow3>.16b, V<aother3>.16b
    ins V<arow3>.h[3], V<aninth>.h[3]
    tbl V<arow3>.16b, {V<arow3>.16b}, V<idx3>.16b
    sqrdmulh V<aquot3>.8h, V<arow3>.8h, V<recip>.8h
    mls V<arow3>.8h, V<aquot3>.8h, V<q>.8h
    sshr V<asign3>.8h, V<arow3>.8h, #15
    and V<asign3>.16b, V<asign3>.16b, V<q>.16b
    add V<arow3>.8h, V<arow3>.8h, V<asign3>.8h
    and V<brow3>.16b, V<bt2>.16b, V<mask3>.16b
    bic V<bother3>.16b, V<bt3>.16b, V<mask3>.16b
    orr V<brow3>.16b, V<brow3>.16b, V<bother3>.16b
    ins V<brow3>.h[3], V<bninth>.h[3]
    tbl V<brow3>.16b, {V<brow3>.16b}, V<idx3>.16b
    sqrdmulh V<bquot3>.8h, V<brow3>.8h, V<recip>.8h
    mls V<brow3>.8h, V<bquot3>.8h, V<q>.8h
    sshr V<bsign3>.8h, V<brow3>.8h, #15
    and V<bsign3>.16b, V<bsign3>.16b, V<q>.16b
    add V<brow3>.8h, V<brow3>.8h, V<bsign3>.8h
    xtn V<lo3>.8b, V<arow3>.8h
    ushr V<mix3>.8h, V<arow3>.8h, #8
    sli V<mix3>.8h, V<brow3>.8h, #4
    xtn V<mid3>.8b, V<mix3>.8h
    ushr V<brow3>.8h, V<brow3>.8h, #4
    xtn V<hi3>.8b, V<brow3>.8h
    ldr Q<p0idx0_3>, [x30, #304]
    tbl V<p0stream0_3>.16b, {V<lo3>.16b, V<mid3>.16b, V<hi3>.16b}, V<p0idx0_3>.16b
    ldr Q<p0idx1_3>, [x30, #320]
    tbl V<p0stream1_3>.16b, {V<lo3>.16b, V<mid3>.16b, V<hi3>.16b}, V<p0idx1_3>.16b
    umov X<p0d3>, V<p0stream0_3>.d[0]
    umov X<p0d4>, V<p0stream0_3>.d[1]
    umov X<p0d5>, V<p0stream1_3>.d[0]
    // ROW 4: create only this pair; t3 dies after this row when applicable
    ldr Q<idx4>, [x30, #224]
    ldr Q<mask4>, [x30, #48]
    and V<arow4>.16b, V<at3>.16b, V<mask4>.16b
    bic V<aother4>.16b, V<at4>.16b, V<mask4>.16b
    orr V<arow4>.16b, V<arow4>.16b, V<aother4>.16b
    ins V<arow4>.h[4], V<aninth>.h[4]
    tbl V<arow4>.16b, {V<arow4>.16b}, V<idx4>.16b
    sqrdmulh V<aquot4>.8h, V<arow4>.8h, V<recip>.8h
    mls V<arow4>.8h, V<aquot4>.8h, V<q>.8h
    sshr V<asign4>.8h, V<arow4>.8h, #15
    and V<asign4>.16b, V<asign4>.16b, V<q>.16b
    add V<arow4>.8h, V<arow4>.8h, V<asign4>.8h
    and V<brow4>.16b, V<bt3>.16b, V<mask4>.16b
    bic V<bother4>.16b, V<bt4>.16b, V<mask4>.16b
    orr V<brow4>.16b, V<brow4>.16b, V<bother4>.16b
    ins V<brow4>.h[4], V<bninth>.h[4]
    tbl V<brow4>.16b, {V<brow4>.16b}, V<idx4>.16b
    sqrdmulh V<bquot4>.8h, V<brow4>.8h, V<recip>.8h
    mls V<brow4>.8h, V<bquot4>.8h, V<q>.8h
    sshr V<bsign4>.8h, V<brow4>.8h, #15
    and V<bsign4>.16b, V<bsign4>.16b, V<q>.16b
    add V<brow4>.8h, V<brow4>.8h, V<bsign4>.8h
    xtn V<lo4>.8b, V<arow4>.8h
    ushr V<mix4>.8h, V<arow4>.8h, #8
    sli V<mix4>.8h, V<brow4>.8h, #4
    xtn V<mid4>.8b, V<mix4>.8h
    ushr V<brow4>.8h, V<brow4>.8h, #4
    xtn V<hi4>.8b, V<brow4>.8h
    ldr Q<p0idx0_4>, [x30, #304]
    tbl V<p0stream0_4>.16b, {V<lo4>.16b, V<mid4>.16b, V<hi4>.16b}, V<p0idx0_4>.16b
    ldr Q<p0idx1_4>, [x30, #320]
    tbl V<p0stream1_4>.16b, {V<lo4>.16b, V<mid4>.16b, V<hi4>.16b}, V<p0idx1_4>.16b
    umov X<p0d12>, V<p0stream0_4>.d[0]
    umov X<p0d13>, V<p0stream0_4>.d[1]
    umov X<p0d14>, V<p0stream1_4>.d[0]
    // ROW 5: create only this pair; t4 dies after this row when applicable
    ldr Q<idx5>, [x30, #240]
    ldr Q<mask5>, [x30, #64]
    and V<arow5>.16b, V<at4>.16b, V<mask5>.16b
    bic V<aother5>.16b, V<at5>.16b, V<mask5>.16b
    orr V<arow5>.16b, V<arow5>.16b, V<aother5>.16b
    ins V<arow5>.h[5], V<aninth>.h[5]
    tbl V<arow5>.16b, {V<arow5>.16b}, V<idx5>.16b
    sqrdmulh V<aquot5>.8h, V<arow5>.8h, V<recip>.8h
    mls V<arow5>.8h, V<aquot5>.8h, V<q>.8h
    sshr V<asign5>.8h, V<arow5>.8h, #15
    and V<asign5>.16b, V<asign5>.16b, V<q>.16b
    add V<arow5>.8h, V<arow5>.8h, V<asign5>.8h
    and V<brow5>.16b, V<bt4>.16b, V<mask5>.16b
    bic V<bother5>.16b, V<bt5>.16b, V<mask5>.16b
    orr V<brow5>.16b, V<brow5>.16b, V<bother5>.16b
    ins V<brow5>.h[5], V<bninth>.h[5]
    tbl V<brow5>.16b, {V<brow5>.16b}, V<idx5>.16b
    sqrdmulh V<bquot5>.8h, V<brow5>.8h, V<recip>.8h
    mls V<brow5>.8h, V<bquot5>.8h, V<q>.8h
    sshr V<bsign5>.8h, V<brow5>.8h, #15
    and V<bsign5>.16b, V<bsign5>.16b, V<q>.16b
    add V<brow5>.8h, V<brow5>.8h, V<bsign5>.8h
    xtn V<lo5>.8b, V<arow5>.8h
    ushr V<mix5>.8h, V<arow5>.8h, #8
    sli V<mix5>.8h, V<brow5>.8h, #4
    xtn V<mid5>.8b, V<mix5>.8h
    ushr V<brow5>.8h, V<brow5>.8h, #4
    xtn V<hi5>.8b, V<brow5>.8h
    ldr Q<p0idx0_5>, [x30, #304]
    tbl V<p0stream0_5>.16b, {V<lo5>.16b, V<mid5>.16b, V<hi5>.16b}, V<p0idx0_5>.16b
    ldr Q<p0idx1_5>, [x30, #320]
    tbl V<p0stream1_5>.16b, {V<lo5>.16b, V<mid5>.16b, V<hi5>.16b}, V<p0idx1_5>.16b
    umov X<p0d21>, V<p0stream0_5>.d[0]
    umov X<p0d22>, V<p0stream0_5>.d[1]
    umov X<p0d23>, V<p0stream1_5>.d[0]
    // ROW 6: create only this pair; t5 dies after this row when applicable
    ldr Q<idx6>, [x30, #256]
    ldr Q<mask6>, [x30, #80]
    and V<arow6>.16b, V<at5>.16b, V<mask6>.16b
    bic V<aother6>.16b, V<at6>.16b, V<mask6>.16b
    orr V<arow6>.16b, V<arow6>.16b, V<aother6>.16b
    ins V<arow6>.h[6], V<aninth>.h[6]
    tbl V<arow6>.16b, {V<arow6>.16b}, V<idx6>.16b
    sqrdmulh V<aquot6>.8h, V<arow6>.8h, V<recip>.8h
    mls V<arow6>.8h, V<aquot6>.8h, V<q>.8h
    sshr V<asign6>.8h, V<arow6>.8h, #15
    and V<asign6>.16b, V<asign6>.16b, V<q>.16b
    add V<arow6>.8h, V<arow6>.8h, V<asign6>.8h
    and V<brow6>.16b, V<bt5>.16b, V<mask6>.16b
    bic V<bother6>.16b, V<bt6>.16b, V<mask6>.16b
    orr V<brow6>.16b, V<brow6>.16b, V<bother6>.16b
    ins V<brow6>.h[6], V<bninth>.h[6]
    tbl V<brow6>.16b, {V<brow6>.16b}, V<idx6>.16b
    sqrdmulh V<bquot6>.8h, V<brow6>.8h, V<recip>.8h
    mls V<brow6>.8h, V<bquot6>.8h, V<q>.8h
    sshr V<bsign6>.8h, V<brow6>.8h, #15
    and V<bsign6>.16b, V<bsign6>.16b, V<q>.16b
    add V<brow6>.8h, V<brow6>.8h, V<bsign6>.8h
    xtn V<lo6>.8b, V<arow6>.8h
    ushr V<mix6>.8h, V<arow6>.8h, #8
    sli V<mix6>.8h, V<brow6>.8h, #4
    xtn V<mid6>.8b, V<mix6>.8h
    ushr V<brow6>.8h, V<brow6>.8h, #4
    xtn V<hi6>.8b, V<brow6>.8h
    ldr Q<p0idx0_6>, [x30, #304]
    tbl V<p0stream0_6>.16b, {V<lo6>.16b, V<mid6>.16b, V<hi6>.16b}, V<p0idx0_6>.16b
    ldr Q<p0idx1_6>, [x30, #320]
    tbl V<p0stream1_6>.16b, {V<lo6>.16b, V<mid6>.16b, V<hi6>.16b}, V<p0idx1_6>.16b
    umov X<p0d6>, V<p0stream0_6>.d[0]
    umov X<p0d7>, V<p0stream0_6>.d[1]
    umov X<p0d8>, V<p0stream1_6>.d[0]
    // ROW 7: create only this pair; t6 dies after this row when applicable
    ldr Q<idx7>, [x30, #272]
    orr V<arow7>.16b, V<at6>.16b, V<at6>.16b
    ins V<arow7>.h[7], V<aninth>.h[7]
    tbl V<arow7>.16b, {V<arow7>.16b}, V<idx7>.16b
    sqrdmulh V<aquot7>.8h, V<arow7>.8h, V<recip>.8h
    mls V<arow7>.8h, V<aquot7>.8h, V<q>.8h
    sshr V<asign7>.8h, V<arow7>.8h, #15
    and V<asign7>.16b, V<asign7>.16b, V<q>.16b
    add V<arow7>.8h, V<arow7>.8h, V<asign7>.8h
    orr V<brow7>.16b, V<bt6>.16b, V<bt6>.16b
    ins V<brow7>.h[7], V<bninth>.h[7]
    tbl V<brow7>.16b, {V<brow7>.16b}, V<idx7>.16b
    sqrdmulh V<bquot7>.8h, V<brow7>.8h, V<recip>.8h
    mls V<brow7>.8h, V<bquot7>.8h, V<q>.8h
    sshr V<bsign7>.8h, V<brow7>.8h, #15
    and V<bsign7>.16b, V<bsign7>.16b, V<q>.16b
    add V<brow7>.8h, V<brow7>.8h, V<bsign7>.8h
    xtn V<lo7>.8b, V<arow7>.8h
    ushr V<mix7>.8h, V<arow7>.8h, #8
    sli V<mix7>.8h, V<brow7>.8h, #4
    xtn V<mid7>.8b, V<mix7>.8h
    ushr V<brow7>.8h, V<brow7>.8h, #4
    xtn V<hi7>.8b, V<brow7>.8h
    ldr Q<p0idx0_7>, [x30, #304]
    tbl V<p0stream0_7>.16b, {V<lo7>.16b, V<mid7>.16b, V<hi7>.16b}, V<p0idx0_7>.16b
    ldr Q<p0idx1_7>, [x30, #320]
    tbl V<p0stream1_7>.16b, {V<lo7>.16b, V<mid7>.16b, V<hi7>.16b}, V<p0idx1_7>.16b
    umov X<p0d15>, V<p0stream0_7>.d[0]
    umov X<p0d16>, V<p0stream0_7>.d[1]
    umov X<p0d17>, V<p0stream1_7>.d[0]
    // ROW 8: create only this pair; t7 dies after this row when applicable
    ldr Q<idx8>, [x30, #288]
    orr V<arow8>.16b, V<at7>.16b, V<at7>.16b
    tbl V<arow8>.16b, {V<arow8>.16b}, V<idx8>.16b
    sqrdmulh V<aquot8>.8h, V<arow8>.8h, V<recip>.8h
    mls V<arow8>.8h, V<aquot8>.8h, V<q>.8h
    sshr V<asign8>.8h, V<arow8>.8h, #15
    and V<asign8>.16b, V<asign8>.16b, V<q>.16b
    add V<arow8>.8h, V<arow8>.8h, V<asign8>.8h
    orr V<brow8>.16b, V<bt7>.16b, V<bt7>.16b
    tbl V<brow8>.16b, {V<brow8>.16b}, V<idx8>.16b
    sqrdmulh V<bquot8>.8h, V<brow8>.8h, V<recip>.8h
    mls V<brow8>.8h, V<bquot8>.8h, V<q>.8h
    sshr V<bsign8>.8h, V<brow8>.8h, #15
    and V<bsign8>.16b, V<bsign8>.16b, V<q>.16b
    add V<brow8>.8h, V<brow8>.8h, V<bsign8>.8h
    xtn V<lo8>.8b, V<arow8>.8h
    ushr V<mix8>.8h, V<arow8>.8h, #8
    sli V<mix8>.8h, V<brow8>.8h, #4
    xtn V<mid8>.8b, V<mix8>.8h
    ushr V<brow8>.8h, V<brow8>.8h, #4
    xtn V<hi8>.8b, V<brow8>.8h
    ldr Q<p0idx0_8>, [x30, #304]
    tbl V<p0stream0_8>.16b, {V<lo8>.16b, V<mid8>.16b, V<hi8>.16b}, V<p0idx0_8>.16b
    ldr Q<p0idx1_8>, [x30, #320]
    tbl V<p0stream1_8>.16b, {V<lo8>.16b, V<mid8>.16b, V<hi8>.16b}, V<p0idx1_8>.16b
    umov X<p0d24>, V<p0stream0_8>.d[0]
    umov X<p0d25>, V<p0stream0_8>.d[1]
    umov X<p0d26>, V<p0stream1_8>.d[0]
    str X<p0d0>, [sp, #0]
    str X<p0d1>, [sp, #8]
    str X<p0d2>, [sp, #16]
    str X<p0d3>, [sp, #24]
    str X<p0d4>, [sp, #32]
    str X<p0d5>, [sp, #40]
    str X<p0d6>, [sp, #48]
    str X<p0d7>, [sp, #56]
    str X<p0d8>, [sp, #64]
    str X<p0d9>, [sp, #72]
    str X<p0d10>, [sp, #80]
    str X<p0d11>, [sp, #88]
    str X<p0d12>, [sp, #96]
    str X<p0d13>, [sp, #104]
    str X<p0d14>, [sp, #112]
    str X<p0d15>, [sp, #120]
    str X<p0d16>, [sp, #128]
    str X<p0d17>, [sp, #136]
    str X<p0d18>, [sp, #144]
    str X<p0d19>, [sp, #152]
    str X<p0d20>, [sp, #160]
    str X<p0d21>, [sp, #168]
    str X<p0d22>, [sp, #176]
    str X<p0d23>, [sp, #184]
    str X<p0d24>, [sp, #192]
    str X<p0d25>, [sp, #200]
    str X<p0d26>, [sp, #208]
gt864_p6d_pair0_end:
    ret
.global gt864_p6d_pair1
gt864_p6d_pair1:
// synthetic allocation region; exact 13-Q plus 28-GPR saved-state frontier.
gt864_p6d_pair1_start:
    ldr X<p0d0>, [sp, #0]
    ldr X<p0d1>, [sp, #8]
    ldr X<p0d2>, [sp, #16]
    ldr X<p0d3>, [sp, #24]
    ldr X<p0d4>, [sp, #32]
    ldr X<p0d5>, [sp, #40]
    ldr X<p0d6>, [sp, #48]
    ldr X<p0d7>, [sp, #56]
    ldr X<p0d8>, [sp, #64]
    ldr X<p0d9>, [sp, #72]
    ldr X<p0d10>, [sp, #80]
    ldr X<p0d11>, [sp, #88]
    ldr X<p0d12>, [sp, #96]
    ldr X<p0d13>, [sp, #104]
    ldr X<p0d14>, [sp, #112]
    ldr X<p0d15>, [sp, #120]
    ldr X<p0d16>, [sp, #128]
    ldr X<p0d17>, [sp, #136]
    ldr X<p0d18>, [sp, #144]
    ldr X<p0d19>, [sp, #152]
    ldr X<p0d20>, [sp, #160]
    ldr X<p0d21>, [sp, #168]
    ldr X<p0d22>, [sp, #176]
    ldr X<p0d23>, [sp, #184]
    ldr X<p0d24>, [sp, #192]
    ldr X<p0d25>, [sp, #200]
    ldr X<p0d26>, [sp, #208]
    ldr Q<aj0>, [x29, #416]
    ldr Q<aj1>, [x29, #368]
    ext V<aj1>.16b, V<aj1>.16b, V<aj1>.16b, #14
    ldr Q<aj2>, [x29, #320]
    ext V<aj2>.16b, V<aj2>.16b, V<aj2>.16b, #12
    ldr Q<aj3>, [x29, #272]
    ext V<aj3>.16b, V<aj3>.16b, V<aj3>.16b, #10
    ldr Q<aj4>, [x29, #224]
    ext V<aj4>.16b, V<aj4>.16b, V<aj4>.16b, #8
    ldr Q<aj5>, [x29, #176]
    ext V<aj5>.16b, V<aj5>.16b, V<aj5>.16b, #6
    ldr Q<aj6>, [x29, #128]
    ext V<aj6>.16b, V<aj6>.16b, V<aj6>.16b, #4
    ldr Q<aj7>, [x29, #80]
    ext V<aj7>.16b, V<aj7>.16b, V<aj7>.16b, #2
    ldr Q<aninth>, [x29, #32]
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
    ldr Q<bj0>, [x29, #816]
    ldr Q<bj1>, [x29, #768]
    ext V<bj1>.16b, V<bj1>.16b, V<bj1>.16b, #14
    ldr Q<bj2>, [x29, #720]
    ext V<bj2>.16b, V<bj2>.16b, V<bj2>.16b, #12
    ldr Q<bj3>, [x29, #672]
    ext V<bj3>.16b, V<bj3>.16b, V<bj3>.16b, #10
    ldr Q<bj4>, [x29, #624]
    ext V<bj4>.16b, V<bj4>.16b, V<bj4>.16b, #8
    ldr Q<bj5>, [x29, #576]
    ext V<bj5>.16b, V<bj5>.16b, V<bj5>.16b, #6
    ldr Q<bj6>, [x29, #528]
    ext V<bj6>.16b, V<bj6>.16b, V<bj6>.16b, #4
    ldr Q<bj7>, [x29, #480]
    ext V<bj7>.16b, V<bj7>.16b, V<bj7>.16b, #2
    ldr Q<bninth>, [x29, #432]
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
    ldr Q<q>, [x30, #336]
    ldr Q<recip>, [x30, #352]
    // ROW 0: create only this pair; t-1 dies after this row when applicable
    ldr Q<idx0>, [x30, #160]
    orr V<arow0>.16b, V<at0>.16b, V<at0>.16b
    ins V<arow0>.h[0], V<aninth>.h[0]
    tbl V<arow0>.16b, {V<arow0>.16b}, V<idx0>.16b
    sqrdmulh V<aquot0>.8h, V<arow0>.8h, V<recip>.8h
    mls V<arow0>.8h, V<aquot0>.8h, V<q>.8h
    sshr V<asign0>.8h, V<arow0>.8h, #15
    and V<asign0>.16b, V<asign0>.16b, V<q>.16b
    add V<arow0>.8h, V<arow0>.8h, V<asign0>.8h
    orr V<brow0>.16b, V<bt0>.16b, V<bt0>.16b
    ins V<brow0>.h[0], V<bninth>.h[0]
    tbl V<brow0>.16b, {V<brow0>.16b}, V<idx0>.16b
    sqrdmulh V<bquot0>.8h, V<brow0>.8h, V<recip>.8h
    mls V<brow0>.8h, V<bquot0>.8h, V<q>.8h
    sshr V<bsign0>.8h, V<brow0>.8h, #15
    and V<bsign0>.16b, V<bsign0>.16b, V<q>.16b
    add V<brow0>.8h, V<brow0>.8h, V<bsign0>.8h
    xtn V<lo0>.8b, V<arow0>.8h
    ushr V<mix0>.8h, V<arow0>.8h, #8
    sli V<mix0>.8h, V<brow0>.8h, #4
    xtn V<mid0>.8b, V<mix0>.8h
    ushr V<brow0>.8h, V<brow0>.8h, #4
    xtn V<hi0>.8b, V<brow0>.8h
    ldr Q<p1idx0_0>, [x30, #304]
    tbl V<p1stream0_0>.16b, {V<lo0>.16b, V<mid0>.16b, V<hi0>.16b}, V<p1idx0_0>.16b
    ldr Q<p1idx1_0>, [x30, #320]
    tbl V<p1stream1_0>.16b, {V<lo0>.16b, V<mid0>.16b, V<hi0>.16b}, V<p1idx1_0>.16b
    movi V<saved0>.16b, #0
    mov V<saved0>.d[0], X<p0d0>
    mov V<saved0>.d[1], X<p0d1>
    movi V<saved1>.16b, #0
    mov V<saved1>.d[0], X<p0d2>
    mov V<saved1>.d[1], V<p1stream0_0>.d[0]
    movi V<saved2>.16b, #0
    mov V<saved2>.d[0], V<p1stream0_0>.d[1]
    mov V<saved2>.d[1], V<p1stream1_0>.d[0]
    // ROW 1: create only this pair; t0 dies after this row when applicable
    ldr Q<idx1>, [x30, #176]
    ldr Q<mask1>, [x30, #0]
    and V<arow1>.16b, V<at0>.16b, V<mask1>.16b
    bic V<aother1>.16b, V<at1>.16b, V<mask1>.16b
    orr V<arow1>.16b, V<arow1>.16b, V<aother1>.16b
    ins V<arow1>.h[1], V<aninth>.h[1]
    tbl V<arow1>.16b, {V<arow1>.16b}, V<idx1>.16b
    sqrdmulh V<aquot1>.8h, V<arow1>.8h, V<recip>.8h
    mls V<arow1>.8h, V<aquot1>.8h, V<q>.8h
    sshr V<asign1>.8h, V<arow1>.8h, #15
    and V<asign1>.16b, V<asign1>.16b, V<q>.16b
    add V<arow1>.8h, V<arow1>.8h, V<asign1>.8h
    and V<brow1>.16b, V<bt0>.16b, V<mask1>.16b
    bic V<bother1>.16b, V<bt1>.16b, V<mask1>.16b
    orr V<brow1>.16b, V<brow1>.16b, V<bother1>.16b
    ins V<brow1>.h[1], V<bninth>.h[1]
    tbl V<brow1>.16b, {V<brow1>.16b}, V<idx1>.16b
    sqrdmulh V<bquot1>.8h, V<brow1>.8h, V<recip>.8h
    mls V<brow1>.8h, V<bquot1>.8h, V<q>.8h
    sshr V<bsign1>.8h, V<brow1>.8h, #15
    and V<bsign1>.16b, V<bsign1>.16b, V<q>.16b
    add V<brow1>.8h, V<brow1>.8h, V<bsign1>.8h
    xtn V<lo1>.8b, V<arow1>.8h
    ushr V<mix1>.8h, V<arow1>.8h, #8
    sli V<mix1>.8h, V<brow1>.8h, #4
    xtn V<mid1>.8b, V<mix1>.8h
    ushr V<brow1>.8h, V<brow1>.8h, #4
    xtn V<hi1>.8b, V<brow1>.8h
    ldr Q<p1idx0_1>, [x30, #304]
    tbl V<p1stream0_1>.16b, {V<lo1>.16b, V<mid1>.16b, V<hi1>.16b}, V<p1idx0_1>.16b
    ldr Q<p1idx1_1>, [x30, #320]
    tbl V<p1stream1_1>.16b, {V<lo1>.16b, V<mid1>.16b, V<hi1>.16b}, V<p1idx1_1>.16b
    movi V<saved9>.16b, #0
    mov V<saved9>.d[0], X<p0d9>
    mov V<saved9>.d[1], X<p0d10>
    movi V<saved10>.16b, #0
    mov V<saved10>.d[0], X<p0d11>
    mov V<saved10>.d[1], V<p1stream0_1>.d[0]
    movi V<saved11>.16b, #0
    mov V<saved11>.d[0], V<p1stream0_1>.d[1]
    mov V<saved11>.d[1], V<p1stream1_1>.d[0]
    // ROW 2: create only this pair; t1 dies after this row when applicable
    ldr Q<idx2>, [x30, #192]
    ldr Q<mask2>, [x30, #16]
    and V<arow2>.16b, V<at1>.16b, V<mask2>.16b
    bic V<aother2>.16b, V<at2>.16b, V<mask2>.16b
    orr V<arow2>.16b, V<arow2>.16b, V<aother2>.16b
    ins V<arow2>.h[2], V<aninth>.h[2]
    tbl V<arow2>.16b, {V<arow2>.16b}, V<idx2>.16b
    sqrdmulh V<aquot2>.8h, V<arow2>.8h, V<recip>.8h
    mls V<arow2>.8h, V<aquot2>.8h, V<q>.8h
    sshr V<asign2>.8h, V<arow2>.8h, #15
    and V<asign2>.16b, V<asign2>.16b, V<q>.16b
    add V<arow2>.8h, V<arow2>.8h, V<asign2>.8h
    and V<brow2>.16b, V<bt1>.16b, V<mask2>.16b
    bic V<bother2>.16b, V<bt2>.16b, V<mask2>.16b
    orr V<brow2>.16b, V<brow2>.16b, V<bother2>.16b
    ins V<brow2>.h[2], V<bninth>.h[2]
    tbl V<brow2>.16b, {V<brow2>.16b}, V<idx2>.16b
    sqrdmulh V<bquot2>.8h, V<brow2>.8h, V<recip>.8h
    mls V<brow2>.8h, V<bquot2>.8h, V<q>.8h
    sshr V<bsign2>.8h, V<brow2>.8h, #15
    and V<bsign2>.16b, V<bsign2>.16b, V<q>.16b
    add V<brow2>.8h, V<brow2>.8h, V<bsign2>.8h
    xtn V<lo2>.8b, V<arow2>.8h
    ushr V<mix2>.8h, V<arow2>.8h, #8
    sli V<mix2>.8h, V<brow2>.8h, #4
    xtn V<mid2>.8b, V<mix2>.8h
    ushr V<brow2>.8h, V<brow2>.8h, #4
    xtn V<hi2>.8b, V<brow2>.8h
    ldr Q<p1idx0_2>, [x30, #304]
    tbl V<p1stream0_2>.16b, {V<lo2>.16b, V<mid2>.16b, V<hi2>.16b}, V<p1idx0_2>.16b
    ldr Q<p1idx1_2>, [x30, #320]
    tbl V<p1stream1_2>.16b, {V<lo2>.16b, V<mid2>.16b, V<hi2>.16b}, V<p1idx1_2>.16b
    umov X<p1d18>, V<p1stream0_2>.d[0]
    umov X<p1d19>, V<p1stream0_2>.d[1]
    umov X<p1d20>, V<p1stream1_2>.d[0]
    // ROW 3: create only this pair; t2 dies after this row when applicable
    ldr Q<idx3>, [x30, #208]
    ldr Q<mask3>, [x30, #32]
    and V<arow3>.16b, V<at2>.16b, V<mask3>.16b
    bic V<aother3>.16b, V<at3>.16b, V<mask3>.16b
    orr V<arow3>.16b, V<arow3>.16b, V<aother3>.16b
    ins V<arow3>.h[3], V<aninth>.h[3]
    tbl V<arow3>.16b, {V<arow3>.16b}, V<idx3>.16b
    sqrdmulh V<aquot3>.8h, V<arow3>.8h, V<recip>.8h
    mls V<arow3>.8h, V<aquot3>.8h, V<q>.8h
    sshr V<asign3>.8h, V<arow3>.8h, #15
    and V<asign3>.16b, V<asign3>.16b, V<q>.16b
    add V<arow3>.8h, V<arow3>.8h, V<asign3>.8h
    and V<brow3>.16b, V<bt2>.16b, V<mask3>.16b
    bic V<bother3>.16b, V<bt3>.16b, V<mask3>.16b
    orr V<brow3>.16b, V<brow3>.16b, V<bother3>.16b
    ins V<brow3>.h[3], V<bninth>.h[3]
    tbl V<brow3>.16b, {V<brow3>.16b}, V<idx3>.16b
    sqrdmulh V<bquot3>.8h, V<brow3>.8h, V<recip>.8h
    mls V<brow3>.8h, V<bquot3>.8h, V<q>.8h
    sshr V<bsign3>.8h, V<brow3>.8h, #15
    and V<bsign3>.16b, V<bsign3>.16b, V<q>.16b
    add V<brow3>.8h, V<brow3>.8h, V<bsign3>.8h
    xtn V<lo3>.8b, V<arow3>.8h
    ushr V<mix3>.8h, V<arow3>.8h, #8
    sli V<mix3>.8h, V<brow3>.8h, #4
    xtn V<mid3>.8b, V<mix3>.8h
    ushr V<brow3>.8h, V<brow3>.8h, #4
    xtn V<hi3>.8b, V<brow3>.8h
    ldr Q<p1idx0_3>, [x30, #304]
    tbl V<p1stream0_3>.16b, {V<lo3>.16b, V<mid3>.16b, V<hi3>.16b}, V<p1idx0_3>.16b
    ldr Q<p1idx1_3>, [x30, #320]
    tbl V<p1stream1_3>.16b, {V<lo3>.16b, V<mid3>.16b, V<hi3>.16b}, V<p1idx1_3>.16b
    movi V<saved3>.16b, #0
    mov V<saved3>.d[0], X<p0d3>
    mov V<saved3>.d[1], X<p0d4>
    movi V<saved4>.16b, #0
    mov V<saved4>.d[0], X<p0d5>
    mov V<saved4>.d[1], V<p1stream0_3>.d[0]
    movi V<saved5>.16b, #0
    mov V<saved5>.d[0], V<p1stream0_3>.d[1]
    mov V<saved5>.d[1], V<p1stream1_3>.d[0]
    // ROW 4: create only this pair; t3 dies after this row when applicable
    ldr Q<idx4>, [x30, #224]
    ldr Q<mask4>, [x30, #48]
    and V<arow4>.16b, V<at3>.16b, V<mask4>.16b
    bic V<aother4>.16b, V<at4>.16b, V<mask4>.16b
    orr V<arow4>.16b, V<arow4>.16b, V<aother4>.16b
    ins V<arow4>.h[4], V<aninth>.h[4]
    tbl V<arow4>.16b, {V<arow4>.16b}, V<idx4>.16b
    sqrdmulh V<aquot4>.8h, V<arow4>.8h, V<recip>.8h
    mls V<arow4>.8h, V<aquot4>.8h, V<q>.8h
    sshr V<asign4>.8h, V<arow4>.8h, #15
    and V<asign4>.16b, V<asign4>.16b, V<q>.16b
    add V<arow4>.8h, V<arow4>.8h, V<asign4>.8h
    and V<brow4>.16b, V<bt3>.16b, V<mask4>.16b
    bic V<bother4>.16b, V<bt4>.16b, V<mask4>.16b
    orr V<brow4>.16b, V<brow4>.16b, V<bother4>.16b
    ins V<brow4>.h[4], V<bninth>.h[4]
    tbl V<brow4>.16b, {V<brow4>.16b}, V<idx4>.16b
    sqrdmulh V<bquot4>.8h, V<brow4>.8h, V<recip>.8h
    mls V<brow4>.8h, V<bquot4>.8h, V<q>.8h
    sshr V<bsign4>.8h, V<brow4>.8h, #15
    and V<bsign4>.16b, V<bsign4>.16b, V<q>.16b
    add V<brow4>.8h, V<brow4>.8h, V<bsign4>.8h
    xtn V<lo4>.8b, V<arow4>.8h
    ushr V<mix4>.8h, V<arow4>.8h, #8
    sli V<mix4>.8h, V<brow4>.8h, #4
    xtn V<mid4>.8b, V<mix4>.8h
    ushr V<brow4>.8h, V<brow4>.8h, #4
    xtn V<hi4>.8b, V<brow4>.8h
    ldr Q<p1idx0_4>, [x30, #304]
    tbl V<p1stream0_4>.16b, {V<lo4>.16b, V<mid4>.16b, V<hi4>.16b}, V<p1idx0_4>.16b
    ldr Q<p1idx1_4>, [x30, #320]
    tbl V<p1stream1_4>.16b, {V<lo4>.16b, V<mid4>.16b, V<hi4>.16b}, V<p1idx1_4>.16b
    movi V<saved12>.16b, #0
    mov V<saved12>.d[0], X<p0d12>
    mov V<saved12>.d[1], X<p0d13>
    umov X<p1d12>, V<p1stream0_4>.d[0]
    umov X<p1d13>, V<p1stream0_4>.d[1]
    umov X<p1d14>, V<p1stream1_4>.d[0]
    // ROW 5: create only this pair; t4 dies after this row when applicable
    ldr Q<idx5>, [x30, #240]
    ldr Q<mask5>, [x30, #64]
    and V<arow5>.16b, V<at4>.16b, V<mask5>.16b
    bic V<aother5>.16b, V<at5>.16b, V<mask5>.16b
    orr V<arow5>.16b, V<arow5>.16b, V<aother5>.16b
    ins V<arow5>.h[5], V<aninth>.h[5]
    tbl V<arow5>.16b, {V<arow5>.16b}, V<idx5>.16b
    sqrdmulh V<aquot5>.8h, V<arow5>.8h, V<recip>.8h
    mls V<arow5>.8h, V<aquot5>.8h, V<q>.8h
    sshr V<asign5>.8h, V<arow5>.8h, #15
    and V<asign5>.16b, V<asign5>.16b, V<q>.16b
    add V<arow5>.8h, V<arow5>.8h, V<asign5>.8h
    and V<brow5>.16b, V<bt4>.16b, V<mask5>.16b
    bic V<bother5>.16b, V<bt5>.16b, V<mask5>.16b
    orr V<brow5>.16b, V<brow5>.16b, V<bother5>.16b
    ins V<brow5>.h[5], V<bninth>.h[5]
    tbl V<brow5>.16b, {V<brow5>.16b}, V<idx5>.16b
    sqrdmulh V<bquot5>.8h, V<brow5>.8h, V<recip>.8h
    mls V<brow5>.8h, V<bquot5>.8h, V<q>.8h
    sshr V<bsign5>.8h, V<brow5>.8h, #15
    and V<bsign5>.16b, V<bsign5>.16b, V<q>.16b
    add V<brow5>.8h, V<brow5>.8h, V<bsign5>.8h
    xtn V<lo5>.8b, V<arow5>.8h
    ushr V<mix5>.8h, V<arow5>.8h, #8
    sli V<mix5>.8h, V<brow5>.8h, #4
    xtn V<mid5>.8b, V<mix5>.8h
    ushr V<brow5>.8h, V<brow5>.8h, #4
    xtn V<hi5>.8b, V<brow5>.8h
    ldr Q<p1idx0_5>, [x30, #304]
    tbl V<p1stream0_5>.16b, {V<lo5>.16b, V<mid5>.16b, V<hi5>.16b}, V<p1idx0_5>.16b
    ldr Q<p1idx1_5>, [x30, #320]
    tbl V<p1stream1_5>.16b, {V<lo5>.16b, V<mid5>.16b, V<hi5>.16b}, V<p1idx1_5>.16b
    umov X<p1d21>, V<p1stream0_5>.d[0]
    umov X<p1d22>, V<p1stream0_5>.d[1]
    umov X<p1d23>, V<p1stream1_5>.d[0]
    // ROW 6: create only this pair; t5 dies after this row when applicable
    ldr Q<idx6>, [x30, #256]
    ldr Q<mask6>, [x30, #80]
    and V<arow6>.16b, V<at5>.16b, V<mask6>.16b
    bic V<aother6>.16b, V<at6>.16b, V<mask6>.16b
    orr V<arow6>.16b, V<arow6>.16b, V<aother6>.16b
    ins V<arow6>.h[6], V<aninth>.h[6]
    tbl V<arow6>.16b, {V<arow6>.16b}, V<idx6>.16b
    sqrdmulh V<aquot6>.8h, V<arow6>.8h, V<recip>.8h
    mls V<arow6>.8h, V<aquot6>.8h, V<q>.8h
    sshr V<asign6>.8h, V<arow6>.8h, #15
    and V<asign6>.16b, V<asign6>.16b, V<q>.16b
    add V<arow6>.8h, V<arow6>.8h, V<asign6>.8h
    and V<brow6>.16b, V<bt5>.16b, V<mask6>.16b
    bic V<bother6>.16b, V<bt6>.16b, V<mask6>.16b
    orr V<brow6>.16b, V<brow6>.16b, V<bother6>.16b
    ins V<brow6>.h[6], V<bninth>.h[6]
    tbl V<brow6>.16b, {V<brow6>.16b}, V<idx6>.16b
    sqrdmulh V<bquot6>.8h, V<brow6>.8h, V<recip>.8h
    mls V<brow6>.8h, V<bquot6>.8h, V<q>.8h
    sshr V<bsign6>.8h, V<brow6>.8h, #15
    and V<bsign6>.16b, V<bsign6>.16b, V<q>.16b
    add V<brow6>.8h, V<brow6>.8h, V<bsign6>.8h
    xtn V<lo6>.8b, V<arow6>.8h
    ushr V<mix6>.8h, V<arow6>.8h, #8
    sli V<mix6>.8h, V<brow6>.8h, #4
    xtn V<mid6>.8b, V<mix6>.8h
    ushr V<brow6>.8h, V<brow6>.8h, #4
    xtn V<hi6>.8b, V<brow6>.8h
    ldr Q<p1idx0_6>, [x30, #304]
    tbl V<p1stream0_6>.16b, {V<lo6>.16b, V<mid6>.16b, V<hi6>.16b}, V<p1idx0_6>.16b
    ldr Q<p1idx1_6>, [x30, #320]
    tbl V<p1stream1_6>.16b, {V<lo6>.16b, V<mid6>.16b, V<hi6>.16b}, V<p1idx1_6>.16b
    movi V<saved6>.16b, #0
    mov V<saved6>.d[0], X<p0d6>
    mov V<saved6>.d[1], X<p0d7>
    movi V<saved7>.16b, #0
    mov V<saved7>.d[0], X<p0d8>
    mov V<saved7>.d[1], V<p1stream0_6>.d[0]
    movi V<saved8>.16b, #0
    mov V<saved8>.d[0], V<p1stream0_6>.d[1]
    mov V<saved8>.d[1], V<p1stream1_6>.d[0]
    // ROW 7: create only this pair; t6 dies after this row when applicable
    ldr Q<idx7>, [x30, #272]
    orr V<arow7>.16b, V<at6>.16b, V<at6>.16b
    ins V<arow7>.h[7], V<aninth>.h[7]
    tbl V<arow7>.16b, {V<arow7>.16b}, V<idx7>.16b
    sqrdmulh V<aquot7>.8h, V<arow7>.8h, V<recip>.8h
    mls V<arow7>.8h, V<aquot7>.8h, V<q>.8h
    sshr V<asign7>.8h, V<arow7>.8h, #15
    and V<asign7>.16b, V<asign7>.16b, V<q>.16b
    add V<arow7>.8h, V<arow7>.8h, V<asign7>.8h
    orr V<brow7>.16b, V<bt6>.16b, V<bt6>.16b
    ins V<brow7>.h[7], V<bninth>.h[7]
    tbl V<brow7>.16b, {V<brow7>.16b}, V<idx7>.16b
    sqrdmulh V<bquot7>.8h, V<brow7>.8h, V<recip>.8h
    mls V<brow7>.8h, V<bquot7>.8h, V<q>.8h
    sshr V<bsign7>.8h, V<brow7>.8h, #15
    and V<bsign7>.16b, V<bsign7>.16b, V<q>.16b
    add V<brow7>.8h, V<brow7>.8h, V<bsign7>.8h
    xtn V<lo7>.8b, V<arow7>.8h
    ushr V<mix7>.8h, V<arow7>.8h, #8
    sli V<mix7>.8h, V<brow7>.8h, #4
    xtn V<mid7>.8b, V<mix7>.8h
    ushr V<brow7>.8h, V<brow7>.8h, #4
    xtn V<hi7>.8b, V<brow7>.8h
    ldr Q<p1idx0_7>, [x30, #304]
    tbl V<p1stream0_7>.16b, {V<lo7>.16b, V<mid7>.16b, V<hi7>.16b}, V<p1idx0_7>.16b
    ldr Q<p1idx1_7>, [x30, #320]
    tbl V<p1stream1_7>.16b, {V<lo7>.16b, V<mid7>.16b, V<hi7>.16b}, V<p1idx1_7>.16b
    umov X<p1d15>, V<p1stream0_7>.d[0]
    umov X<p1d16>, V<p1stream0_7>.d[1]
    umov X<p1d17>, V<p1stream1_7>.d[0]
    // ROW 8: create only this pair; t7 dies after this row when applicable
    ldr Q<idx8>, [x30, #288]
    orr V<arow8>.16b, V<at7>.16b, V<at7>.16b
    tbl V<arow8>.16b, {V<arow8>.16b}, V<idx8>.16b
    sqrdmulh V<aquot8>.8h, V<arow8>.8h, V<recip>.8h
    mls V<arow8>.8h, V<aquot8>.8h, V<q>.8h
    sshr V<asign8>.8h, V<arow8>.8h, #15
    and V<asign8>.16b, V<asign8>.16b, V<q>.16b
    add V<arow8>.8h, V<arow8>.8h, V<asign8>.8h
    orr V<brow8>.16b, V<bt7>.16b, V<bt7>.16b
    tbl V<brow8>.16b, {V<brow8>.16b}, V<idx8>.16b
    sqrdmulh V<bquot8>.8h, V<brow8>.8h, V<recip>.8h
    mls V<brow8>.8h, V<bquot8>.8h, V<q>.8h
    sshr V<bsign8>.8h, V<brow8>.8h, #15
    and V<bsign8>.16b, V<bsign8>.16b, V<q>.16b
    add V<brow8>.8h, V<brow8>.8h, V<bsign8>.8h
    xtn V<lo8>.8b, V<arow8>.8h
    ushr V<mix8>.8h, V<arow8>.8h, #8
    sli V<mix8>.8h, V<brow8>.8h, #4
    xtn V<mid8>.8b, V<mix8>.8h
    ushr V<brow8>.8h, V<brow8>.8h, #4
    xtn V<hi8>.8b, V<brow8>.8h
    ldr Q<p1idx0_8>, [x30, #304]
    tbl V<p1stream0_8>.16b, {V<lo8>.16b, V<mid8>.16b, V<hi8>.16b}, V<p1idx0_8>.16b
    ldr Q<p1idx1_8>, [x30, #320]
    tbl V<p1stream1_8>.16b, {V<lo8>.16b, V<mid8>.16b, V<hi8>.16b}, V<p1idx1_8>.16b
    umov X<p1d24>, V<p1stream0_8>.d[0]
    umov X<p1d25>, V<p1stream0_8>.d[1]
    umov X<p1d26>, V<p1stream1_8>.d[0]
    str Q<saved0>, [sp, #0]
    str Q<saved1>, [sp, #16]
    str Q<saved2>, [sp, #32]
    str Q<saved3>, [sp, #48]
    str Q<saved4>, [sp, #64]
    str Q<saved5>, [sp, #80]
    str Q<saved6>, [sp, #96]
    str Q<saved7>, [sp, #112]
    str Q<saved8>, [sp, #128]
    str Q<saved9>, [sp, #144]
    str Q<saved10>, [sp, #160]
    str Q<saved11>, [sp, #176]
    str Q<saved12>, [sp, #192]
    str X<p0d14>, [sp, #208]
    str X<p1d12>, [sp, #216]
    str X<p1d13>, [sp, #224]
    str X<p1d14>, [sp, #232]
    str X<p0d15>, [sp, #240]
    str X<p0d16>, [sp, #248]
    str X<p0d17>, [sp, #256]
    str X<p1d15>, [sp, #264]
    str X<p1d16>, [sp, #272]
    str X<p1d17>, [sp, #280]
    str X<p0d18>, [sp, #288]
    str X<p0d19>, [sp, #296]
    str X<p0d20>, [sp, #304]
    str X<p1d18>, [sp, #312]
    str X<p1d19>, [sp, #320]
    str X<p1d20>, [sp, #328]
    str X<p0d21>, [sp, #336]
    str X<p0d22>, [sp, #344]
    str X<p0d23>, [sp, #352]
    str X<p1d21>, [sp, #360]
    str X<p1d22>, [sp, #368]
    str X<p1d23>, [sp, #376]
    str X<p0d24>, [sp, #384]
    str X<p0d25>, [sp, #392]
    str X<p0d26>, [sp, #400]
    str X<p1d24>, [sp, #408]
    str X<p1d25>, [sp, #416]
    str X<p1d26>, [sp, #424]
gt864_p6d_pair1_end:
    ret
