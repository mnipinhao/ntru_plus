/* Promoted fused-wide 84-instruction core; source evidence in baseinv-tobytes-next-model. */
#ifdef __APPLE__
#define binv_num_tile _binv_num_tile
#endif
.text
.global binv_num_tile
binv_num_tile:
        binv_num_tile_slothy_start:
        mov w7, #3457
        mov w15, #-147
        ldr q15, [x1, #0]
        mov w17, #-1393
        dup v31.8H, w17
        mov w11, #-12929
        ldr q18, [x1, #16]
        dup v10.8H, w15
        ldr q27, [x1, #32]
        dup v23.8H, w11
        ldr q26, [x2, #0]
        sqrdmulh v12.8H, v15.8H, v31.8H
        dup v19.8H, w7
        sqrdmulh v1.8H, v27.8H, v31.8H
        sqrdmulh v14.8H, v18.8H, v31.8H
        mul v22.8H, v27.8H, v10.8H
        mls v22.8H, v1.8H, v19.8H
        mul v4.8H, v15.8H, v10.8H
        mul v24.8H, v18.8H, v10.8H
        mul v18.8H, v22.8H, v23.8H
        mls v24.8H, v14.8H, v19.8H
        smull v14.4S, v22.4H, v22.4H
        mul v27.8H, v22.8H, v18.8H
        smull2 v1.4S, v22.8H, v22.8H
        mls v4.8H, v12.8H, v19.8H
        smull v15.4S, v24.4H, v24.4H
        smlal2 v1.4S, v27.8H, v19.8H
        smlal v14.4S, v27.4H, v19.4H
        smull2 v18.4S, v24.8H, v24.8H
        smlsl2 v18.4S, v4.8H, v22.8H
        mul v12.8H, v22.8H, v23.8H
        uzp2 v27.8H, v14.8H, v1.8H
        smlsl v15.4S, v4.4H, v22.4H
        smull2 v1.4S, v27.8H, v26.8H
        smull v11.4S, v27.4H, v26.4H
        smlsl2 v1.4S, v4.8H, v24.8H
        smlsl v11.4S, v4.4H, v24.4H
        mul v6.8H, v24.8H, v12.8H
        uzp1 v12.8H, v15.8H, v18.8H
        mul v12.8H, v12.8H, v23.8H
        uzp1 v14.8H, v11.8H, v1.8H
        smull v31.4S, v24.4H, v22.4H
        mul v27.8H, v14.8H, v23.8H
        smlal2 v18.4S, v12.8H, v19.8H
        smlal v15.4S, v12.4H, v19.4H
        smull2 v17.4S, v24.8H, v22.8H
        smlal2 v1.4S, v27.8H, v19.8H
        smlal v11.4S, v27.4H, v19.4H
        smlal2 v17.4S, v6.8H, v19.8H
        uzp2 v18.8H, v15.8H, v18.8H
        smlal v31.4S, v6.4H, v19.4H
        smull2 v14.4S, v18.8H, v24.8H
        smull v12.4S, v18.4H, v24.4H
        uzp2 v27.8H, v11.8H, v1.8H
        smull2 v1.4S, v4.8H, v4.8H
        uzp2 v11.8H, v31.8H, v17.8H
        smlal2 v14.4S, v27.8H, v22.8H
        smlal v12.4S, v27.4H, v22.4H
        str q27, [x0, #16]
        smull v15.4S, v4.4H, v4.4H
        smlsl2 v1.4S, v11.8H, v26.8H
        smlsl v15.4S, v11.4H, v26.4H
        uzp1 v27.8H, v12.8H, v14.8H
        str q18, [x0, #32]
        mul v18.8H, v27.8H, v23.8H
        uzp1 v11.8H, v15.8H, v1.8H
        mul v27.8H, v11.8H, v23.8H
        smlal2 v14.4S, v18.8H, v19.8H
        smlal v12.4S, v18.4H, v19.4H
        smlal2 v1.4S, v27.8H, v19.8H
        smlal v15.4S, v27.4H, v19.4H
        uzp2 v18.8H, v12.8H, v14.8H
        smull v27.4S, v18.4H, v26.4H
        uzp2 v14.8H, v15.8H, v1.8H
        smull2 v18.4S, v18.8H, v26.8H
        smlal v27.4S, v14.4H, v4.4H
        smlal2 v18.4S, v14.8H, v4.8H
        str q14, [x0, #0]
        uzp1 v12.8H, v27.8H, v18.8H
        mul v1.8H, v12.8H, v23.8H
        smlal2 v18.4S, v1.8H, v19.8H
        smlal v27.4S, v1.4H, v19.4H
        uzp2 v1.8H, v27.8H, v18.8H
        str q1, [x3, #0]
        binv_num_tile_slothy_end:
    ret
