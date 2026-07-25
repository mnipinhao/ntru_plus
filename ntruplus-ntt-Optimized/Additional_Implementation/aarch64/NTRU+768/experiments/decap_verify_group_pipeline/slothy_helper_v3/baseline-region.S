/* Mechanically extracted from the V3 shared helper. */
.text
.align 2
slothy_start_decap_verify_helper_v3_baseline:
    ld1 {v1.8h}, [x3], #16
    ld1 {v8.8h-v11.8h}, [x2], #64
    smull v12.4s, v5.4h, v11.4h
    smull2 v13.4s, v5.8h, v11.8h
    smull v14.4s, v6.4h, v11.4h
    smull2 v15.4s, v6.8h, v11.8h
    smull v16.4s, v7.4h, v11.4h
    smull2 v17.4s, v7.8h, v11.8h

    smlal v12.4s, v6.4h, v10.4h
    smlal2 v13.4s, v6.8h, v10.8h
    smlal v14.4s, v7.4h, v10.4h
    smlal2 v15.4s, v7.8h, v10.8h
    smlal v12.4s, v7.4h, v9.4h
    smlal2 v13.4s, v7.8h, v9.8h

    uzp1 v20.8h, v16.8h, v17.8h
    uzp1 v19.8h, v14.8h, v15.8h
    uzp1 v18.8h, v12.8h, v13.8h
    mul v20.8h, v20.8h, v0.h[2]
    mul v19.8h, v19.8h, v0.h[2]
    mul v18.8h, v18.8h, v0.h[2]
    smlal v16.4s, v20.4h, v0.h[0]
    smlal2 v17.4s, v20.8h, v0.h[0]
    smlal v14.4s, v19.4h, v0.h[0]
    smlal2 v15.4s, v19.8h, v0.h[0]
    smlal v12.4s, v18.4h, v0.h[0]
    smlal2 v13.4s, v18.8h, v0.h[0]

    uzp2 v2.8h, v16.8h, v17.8h
    uzp2 v3.8h, v14.8h, v15.8h
    smull v18.4s, v7.4h, v8.4h
    smull2 v19.4s, v7.8h, v8.8h
    smull v16.4s, v2.4h, v1.4h
    smull2 v17.4s, v2.8h, v1.8h
    uzp2 v2.8h, v12.8h, v13.8h
    smull v14.4s, v3.4h, v1.4h
    smull2 v15.4s, v3.8h, v1.8h
    smull v12.4s, v2.4h, v1.4h
    smull2 v13.4s, v2.8h, v1.8h

    smlal v18.4s, v4.4h, v11.4h
    smlal2 v19.4s, v4.8h, v11.8h
    smlal v16.4s, v4.4h, v10.4h
    smlal2 v17.4s, v4.8h, v10.8h
    smlal v14.4s, v4.4h, v9.4h
    smlal2 v15.4s, v4.8h, v9.8h
    smlal v12.4s, v4.4h, v8.4h
    smlal2 v13.4s, v4.8h, v8.8h
    smlal v18.4s, v5.4h, v10.4h
    smlal2 v19.4s, v5.8h, v10.8h
    smlal v16.4s, v5.4h, v9.4h
    smlal2 v17.4s, v5.8h, v9.8h
    smlal v14.4s, v5.4h, v8.4h
    smlal2 v15.4s, v5.8h, v8.8h
    smlal v18.4s, v6.4h, v9.4h
    smlal2 v19.4s, v6.8h, v9.8h
    smlal v16.4s, v6.4h, v8.4h
    smlal2 v17.4s, v6.8h, v8.8h

    uzp1 v23.8h, v18.8h, v19.8h
    uzp1 v22.8h, v16.8h, v17.8h
    uzp1 v21.8h, v14.8h, v15.8h
    uzp1 v20.8h, v12.8h, v13.8h
    mul v23.8h, v23.8h, v0.h[2]
    mul v22.8h, v22.8h, v0.h[2]
    mul v21.8h, v21.8h, v0.h[2]
    mul v20.8h, v20.8h, v0.h[2]
    smlal v18.4s, v23.4h, v0.h[0]
    smlal v16.4s, v22.4h, v0.h[0]
    smlal v14.4s, v21.4h, v0.h[0]
    smlal v12.4s, v20.4h, v0.h[0]
    smlal2 v19.4s, v23.8h, v0.h[0]
    smlal2 v17.4s, v22.8h, v0.h[0]
    smlal2 v15.4s, v21.8h, v0.h[0]
    smlal2 v13.4s, v20.8h, v0.h[0]

    uzp2 v7.8h, v18.8h, v19.8h
    uzp2 v6.8h, v16.8h, v17.8h
    uzp2 v5.8h, v14.8h, v15.8h
    uzp2 v4.8h, v12.8h, v13.8h
    mul v11.8h, v7.8h, v0.h[3]
    mul v10.8h, v6.8h, v0.h[3]
    mul v9.8h, v5.8h, v0.h[3]
    mul v8.8h, v4.8h, v0.h[3]
    sqrdmulh v7.8h, v7.8h, v0.h[4]
    sqrdmulh v6.8h, v6.8h, v0.h[4]
    sqrdmulh v5.8h, v5.8h, v0.h[4]
    sqrdmulh v4.8h, v4.8h, v0.h[4]
    mls v11.8h, v7.8h, v0.h[0]
    mls v10.8h, v6.8h, v0.h[0]
    mls v9.8h, v5.8h, v0.h[0]
    mls v8.8h, v4.8h, v0.h[0]

    sqdmulh v15.8h, v11.8h, v0.h[1]
    sqdmulh v14.8h, v10.8h, v0.h[1]
    sqdmulh v13.8h, v9.8h, v0.h[1]
    sqdmulh v12.8h, v8.8h, v0.h[1]
    srshr v15.8h, v15.8h, #11
    srshr v14.8h, v14.8h, #11
    srshr v13.8h, v13.8h, #11
    srshr v12.8h, v12.8h, #11
    mls v11.8h, v15.8h, v0.h[0]
    mls v10.8h, v14.8h, v0.h[0]
    mls v9.8h, v13.8h, v0.h[0]
    mls v8.8h, v12.8h, v0.h[0]

    st1 {v8.8h-v11.8h}, [x0], #64
slothy_end_decap_verify_helper_v3_baseline:
