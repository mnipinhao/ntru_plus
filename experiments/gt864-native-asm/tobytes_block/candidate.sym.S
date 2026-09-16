.text
.global byte_pair_block
byte_pair_block:
// live-in: x0-x4 as specified in kernel-contract.yml.
// live-out: exact output memory; no coefficient scratch.
// range: normalized bytes; small producer requires -3457 < input < 3457; see contract.
// reserved registers: x18-x30; outer wrapper preserves d8-d15.
byte_pair_block_slothy_start:
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
    mov w8, #9
    dup V<recip>.8h, w8
    // ROW 0: create only this pair; t-1 dies after this row when applicable
    ldr Q<idx0>, [x4, #0]
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
    add x5, x0, #0
    st3 {V<lo0>.8b, V<mid0>.8b, V<hi0>.8b}, [x5]
    // ROW 1: create only this pair; t0 dies after this row when applicable
    ldr Q<idx1>, [x4, #16]
    ldr Q<mask1>, [x3, #0]
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
    add x5, x0, #72
    st3 {V<lo1>.8b, V<mid1>.8b, V<hi1>.8b}, [x5]
    // ROW 2: create only this pair; t1 dies after this row when applicable
    ldr Q<idx2>, [x4, #32]
    ldr Q<mask2>, [x3, #16]
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
    add x5, x0, #144
    st3 {V<lo2>.8b, V<mid2>.8b, V<hi2>.8b}, [x5]
    // ROW 3: create only this pair; t2 dies after this row when applicable
    ldr Q<idx3>, [x4, #48]
    ldr Q<mask3>, [x3, #32]
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
    add x5, x0, #24
    st3 {V<lo3>.8b, V<mid3>.8b, V<hi3>.8b}, [x5]
    // ROW 4: create only this pair; t3 dies after this row when applicable
    ldr Q<idx4>, [x4, #64]
    ldr Q<mask4>, [x3, #48]
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
    add x5, x0, #96
    st3 {V<lo4>.8b, V<mid4>.8b, V<hi4>.8b}, [x5]
    // ROW 5: create only this pair; t4 dies after this row when applicable
    ldr Q<idx5>, [x4, #80]
    ldr Q<mask5>, [x3, #64]
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
    add x5, x0, #168
    st3 {V<lo5>.8b, V<mid5>.8b, V<hi5>.8b}, [x5]
    // ROW 6: create only this pair; t5 dies after this row when applicable
    ldr Q<idx6>, [x4, #96]
    ldr Q<mask6>, [x3, #80]
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
    add x5, x0, #48
    st3 {V<lo6>.8b, V<mid6>.8b, V<hi6>.8b}, [x5]
    // ROW 7: create only this pair; t6 dies after this row when applicable
    ldr Q<idx7>, [x4, #112]
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
    add x5, x0, #120
    st3 {V<lo7>.8b, V<mid7>.8b, V<hi7>.8b}, [x5]
    // ROW 8: create only this pair; t7 dies after this row when applicable
    ldr Q<idx8>, [x4, #128]
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
    add x5, x0, #192
    st3 {V<lo8>.8b, V<mid8>.8b, V<hi8>.8b}, [x5]
byte_pair_block_slothy_end:
    ret
