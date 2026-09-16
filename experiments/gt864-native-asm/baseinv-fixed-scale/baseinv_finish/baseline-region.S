        binv_finish_tile_slothy_start:
        mov w3, #3457
        mov w4, #1728
        mov w15, #1
        dup v7.8H, w3
        mov w3, #-12929
        dup v21.8H, w3
        ldr q4, [x1, #0]
        ldr q15, [x0, #32]
        dup v10.8H, w15
        dup v28.8H, w4
        ldr q16, [x0, #16]
        ldr q25, [x0, #0]
        mul v29.8H, v10.8H, v21.8H
        smull v18.4S, v4.4H, v10.4H
        mul v11.8H, v4.8H, v29.8H
        smull2 v29.4S, v4.8H, v10.8H
        smlal v18.4S, v11.4H, v7.4H
        smlal2 v29.4S, v11.8H, v7.8H
        uzp2 v23.8H, v18.8H, v29.8H
        mul v8.8H, v23.8H, v21.8H
        smull v29.4S, v25.4H, v23.4H
        mul v4.8H, v25.8H, v8.8H
        smull2 v18.4S, v25.8H, v23.8H
        smlal v29.4S, v4.4H, v7.4H
        smlal2 v18.4S, v4.8H, v7.8H
        uzp2 v30.8H, v29.8H, v18.8H
        sshr v12.8H, v30.8H, #15
        and v18.16B, v12.16B, v7.16B
        add v4.8H, v30.8H, v18.8H
        mul v30.8H, v16.8H, v8.8H
        cmgt v31.8H, v4.8H, v28.8H
        and v25.16B, v31.16B, v7.16B
        smull v14.4S, v16.4H, v23.4H
        sub v11.8H, v4.8H, v25.8H
        smull2 v21.4S, v16.8H, v23.8H
        str q11, [x0, #0]
        smlal v14.4S, v30.4H, v7.4H
        smlal2 v21.4S, v30.8H, v7.8H
        uzp2 v16.8H, v14.8H, v21.8H
        sshr v11.8H, v16.8H, #15
        and v3.16B, v11.16B, v7.16B
        add v18.8H, v16.8H, v3.8H
        mul v13.8H, v15.8H, v8.8H
        cmgt v2.8H, v18.8H, v28.8H
        smull2 v21.4S, v15.8H, v23.8H
        and v10.16B, v2.16B, v7.16B
        smull v26.4S, v15.4H, v23.4H
        sub v27.8H, v18.8H, v10.8H
        smlal2 v21.4S, v13.8H, v7.8H
        smlal v26.4S, v13.4H, v7.4H
        str q27, [x0, #16]
        uzp2 v18.8H, v26.8H, v21.8H
        sshr v31.8H, v18.8H, #15
        and v4.16B, v31.16B, v7.16B
        add v1.8H, v18.8H, v4.8H
        cmgt v24.8H, v1.8H, v28.8H
        and v22.16B, v24.16B, v7.16B
        sub v15.8H, v1.8H, v22.8H
        str q15, [x0, #32]
        binv_finish_tile_slothy_end:
