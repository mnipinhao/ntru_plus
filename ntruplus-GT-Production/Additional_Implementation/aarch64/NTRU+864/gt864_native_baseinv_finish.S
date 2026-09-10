/* Promoted 37-instruction no-centering finish; Keygen -> D1 range closure passed. */
#ifdef __APPLE__
#define binv_finish_tile _binv_finish_tile
#endif
.text
.global binv_finish_tile
binv_finish_tile:
        binv_finish_tile_slothy_start:
        ldr q18, [x1, #0]
        mov w6, #-12929
        mov w11, #-682
        ldr q5, [x0, #0]
        dup v31.8H, w6
        mov w7, #-6464
        ldr q8, [x0, #16]
        mov w6, #3457
        dup v7.8H, w7
        ldr q30, [x0, #32]
        dup v10.8H, w6
        dup v29.8H, w11
        sqrdmulh v7.8H, v18.8H, v7.8H
        mul v18.8H, v18.8H, v29.8H
        mls v18.8H, v7.8H, v10.8H
        mul v22.8H, v18.8H, v31.8H
        smull v31.4S, v8.4H, v18.4H
        smull v29.4S, v5.4H, v18.4H
        smull2 v7.4S, v5.8H, v18.8H
        mul v5.8H, v5.8H, v22.8H
        mul v9.8H, v8.8H, v22.8H
        smull2 v8.4S, v8.8H, v18.8H
        smlal2 v7.4S, v5.8H, v10.8H
        smlal v29.4S, v5.4H, v10.4H
        smlal v31.4S, v9.4H, v10.4H
        mul v5.8H, v30.8H, v22.8H
        uzp2 v29.8H, v29.8H, v7.8H
        smull2 v7.4S, v30.8H, v18.8H
        smull v18.4S, v30.4H, v18.4H
        smlal2 v8.4S, v9.8H, v10.8H
        str q29, [x0, #0]
        smlal2 v7.4S, v5.8H, v10.8H
        smlal v18.4S, v5.4H, v10.4H
        uzp2 v25.8H, v31.8H, v8.8H
        str q25, [x0, #16]
        uzp2 v18.8H, v18.8H, v7.8H
        str q18, [x0, #32]
        binv_finish_tile_slothy_end:
    ret
