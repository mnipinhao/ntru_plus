.text
.align 2
.global qsoa_frombytes
.global _qsoa_frombytes
qsoa_frombytes:
_qsoa_frombytes:
 sub sp, sp, #64
 stp d8, d9, [sp, #0]
 stp d10, d11, [sp, #16]
 stp d12, d13, [sp, #32]
 stp d14, d15, [sp, #48]
 adr x2, support_const_mask_0fff
 ldr q0, [x2]
 mov w8, #3457
 dup v1.8h, w8
 movi v3.16b, #0
 movi v11.16b, #0
 mov x8, #1536

.align 2
_support_loop_frombytes:
 /*
	 * Live-in: x0=dst, x1=src bytes, x8=public byte counter, v0=0x0fff mask.
	 * Live-out: dst advances by 128 bytes, src advances by 96 bytes.
	 * Range: packed 12-bit coefficients unpack to masked int16 lanes.
	 * Reserved physical registers: x9-x30 and sp.
	 */
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
        umax v3.8h, v3.8h, v24.8h
        umax v3.8h, v3.8h, v25.8h
        umax v3.8h, v3.8h, v26.8h
        umax v3.8h, v3.8h, v27.8h
        shl v5.8H, v15.8H, #8
        trn2 v29.8H, v23.8H, v21.8H
        ushr v13.8H, v15.8H, #4
        st1 {v24.8H, v25.8H, v26.8H, v27.8H}, [x0], #64
        ushr v6.8H, v4.8H, #8
        ushr v25.8H, v29.8H, #12
        eor v6.16B, v6.16B, v5.16B
        eor v30.16B, v25.16B, v22.16B
        and v14.16B, v29.16B, v0.16B
        and v16.16B, v6.16B, v0.16B
        and v17.16B, v13.16B, v0.16B
        and v15.16B, v30.16B, v0.16B
        umax v11.8h, v11.8h, v14.8h
        umax v11.8h, v11.8h, v15.8h
        umax v11.8h, v11.8h, v16.8h
        umax v11.8h, v11.8h, v17.8h
        st1 {v14.8H, v15.8H, v16.8H, v17.8H}, [x0], #64

 subs x8, x8, #128
 b.ne _support_loop_frombytes
 umax v3.8h, v3.8h, v11.8h
 cmhs v3.8h, v3.8h, v1.8h
 umaxv h7, v3.8h
 umov w0, v7.h[0]
 cmp w0, #0
 cset w0, ne
 ldp d8, d9, [sp, #0]
 ldp d10, d11, [sp, #16]
 ldp d12, d13, [sp, #32]
 ldp d14, d15, [sp, #48]
 add sp, sp, #64
 ret

.global qsoa_tobytes
.global _qsoa_tobytes
qsoa_tobytes:
_qsoa_tobytes:
 adr x2, support_const_q
 ldr q0, [x2]
 mov x8, #1536

.align 2
_support_loop_tobytes:
 /*
	 * Live-in: x0=dst bytes, x1=src coefficients, x8=public byte counter, v0=q.
	 * Live-out: v1..v6 hold packed byte vectors for the two original stores;
	 * src advances by 128 bytes, and dst advances after the stores below.
	 * Range: int16 coefficients are conditionally lifted by q then packed.
	 * Reserved physical registers: x9-x30 and sp.
	 */
        ld1 {v9.8H, v10.8H, v11.8H, v12.8H}, [x1], #64
        ld1 {v26.8H, v27.8H, v28.8H, v29.8H}, [x1], #64
        sshr v8.8H, v9.8H, #15
        sshr v30.8H, v10.8H, #15
        and v25.16B, v8.16B, v0.16B
        sshr v24.8H, v12.8H, #15
        sshr v18.8H, v11.8H, #15
        and v30.16B, v30.16B, v0.16B
        add v7.8H, v9.8H, v25.8H
        and v4.16B, v24.16B, v0.16B
        sshr v3.8H, v26.8H, #15
        and v9.16B, v18.16B, v0.16B
        add v24.8H, v12.8H, v4.8H
        sshr v19.8H, v29.8H, #15
        add v21.8H, v11.8H, v9.8H
        sshr v9.8H, v27.8H, #15
        and v19.16B, v19.16B, v0.16B
        shl v11.8H, v24.8H, #4
        and v25.16B, v9.16B, v0.16B
        sshr v1.8H, v28.8H, #15
        add v10.8H, v10.8H, v30.8H
        add v9.8H, v29.8H, v19.8H
        add v25.8H, v27.8H, v25.8H
        ushr v8.8H, v21.8H, #8
        and v22.16B, v3.16B, v0.16B
        ushr v20.8H, v10.8H, #4
        shl v24.8H, v9.8H, #4
        and v3.16B, v1.16B, v0.16B
        eor v11.16B, v8.16B, v11.16B
        ushr v15.8H, v25.8H, #4
        add v2.8H, v28.8H, v3.8H
        shl v19.8H, v10.8H, #12
        shl v18.8H, v21.8H, #8
        add v5.8H, v26.8H, v22.8H
        shl v25.8H, v25.8H, #12
        eor v31.16B, v7.16B, v19.16B
        shl v9.8H, v2.8H, #8
        eor v6.16B, v20.16B, v18.16B
        ushr v3.8H, v2.8H, #8
        eor v8.16B, v5.16B, v25.16B
        trn1 v1.8H, v31.8H, v6.8H
        eor v27.16B, v15.16B, v9.16B
        eor v3.16B, v3.16B, v24.16B
        trn1 v9.8H, v11.8H, v8.8H
        trn2 v30.8H, v31.8H, v6.8H
        trn2 v5.8H, v11.8H, v8.8H
        trn2 v14.4S, v1.4S, v9.4S
        trn2 v8.8H, v27.8H, v3.8H
        trn1 v18.8H, v27.8H, v3.8H
        trn1 v25.4S, v1.4S, v9.4S
        trn1 v22.4S, v5.4S, v8.4S
        trn2 v24.4S, v5.4S, v8.4S
        trn1 v10.4S, v18.4S, v30.4S
        trn2 v18.4S, v18.4S, v30.4S
        trn1 v2.2D, v22.2D, v14.2D
        trn2 v5.2D, v22.2D, v14.2D
        trn1 v1.2D, v25.2D, v10.2D
        trn1 v3.2D, v18.2D, v24.2D
        trn2 v4.2D, v25.2D, v10.2D
        trn2 v6.2D, v18.2D, v24.2D

 st1 {v1.8h, v2.8h, v3.8h}, [x0], #48
 st1 {v4.8h, v5.8h, v6.8h}, [x0], #48
 subs x8, x8, #128
 b.ne _support_loop_tobytes
 ret

.align 4
support_const_mask_0fff:
 .hword 0x0fff, 0x0fff, 0x0fff, 0x0fff
 .hword 0x0fff, 0x0fff, 0x0fff, 0x0fff

.align 4
support_const_q:
 .hword 3457, 3457, 3457, 3457
 .hword 3457, 3457, 3457, 3457
