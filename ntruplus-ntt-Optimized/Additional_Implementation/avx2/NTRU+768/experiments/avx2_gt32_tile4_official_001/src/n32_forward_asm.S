/* GT-N32-FORWARD-ASM-013: complete R3 NTT32-first Forward. */

	.text

	.macro N32_FORM_PAIR b0,b1,tmp,vector
	vmovdqu 32*\vector(%rsi), \b0
	vmovdqu 768+32*\vector(%rsi), \b1
	vpmullw .Ln32_fwd_top_raw(%rip), \b1, \tmp
	vpaddw \b0, \b1, \b1
	vpsubw \tmp, \b1, \b1
	vpaddw \tmp, \b0, \b0
	/* Branch 0 twist. */
	vpmullw .Ln32_fwd_twist_qinv+64*\vector(%rip), \b0, \tmp
	vpmulhw .Ln32_fwd_twist_factor+64*\vector(%rip), \b0, \b0
	vpmulhw .Ln32_fwd_q(%rip), \tmp, \tmp
	vpsubw \tmp, \b0, \b0
	/* Branch 1 twist. */
	vpmullw .Ln32_fwd_twist_qinv+64*\vector+32(%rip), \b1, \tmp
	vpmulhw .Ln32_fwd_twist_factor+64*\vector+32(%rip), \b1, \b1
	vpmulhw .Ln32_fwd_q(%rip), \tmp, \tmp
	vpsubw \tmp, \b1, \b1
	.endm

	.macro N32_FORM_TOP_PAIR b0,b1,tmp,vector
	vmovdqu 32*\vector(%rsi), \b0
	vmovdqu 768+32*\vector(%rsi), \b1
	vpmullw .Ln32_fwd_top_raw(%rip), \b1, \tmp
	vpaddw \b0, \b1, \b1
	vpsubw \tmp, \b1, \b1
	vpaddw \tmp, \b0, \b0
	.endm

	.macro N32_RAW_DESTRUCTIVE lo,hi
	vpaddw \hi, \lo, \lo
	vpaddw \hi, \hi, \hi
	vpsubw \hi, \lo, \hi
	.endm

	.macro N32_CONJ_HALF_PAIR v0,v1,tlo,thi,tprod,qinv,factor,offset
	vperm2i128 $0x20, \v1, \v0, \tlo
	vperm2i128 $0x31, \v1, \v0, \thi
	vpmullw \qinv+\offset(%rip), \thi, \tprod
	vpmulhw \factor+\offset(%rip), \thi, \thi
	vpmulhw .Ln32_fwd_q(%rip), \tprod, \tprod
	vpsubw \tprod, \thi, \thi
	vpsubw \thi, \tlo, \tprod
	vpaddw \thi, \tlo, \tlo
	vperm2i128 $0x20, \tprod, \tlo, \v0
	vperm2i128 $0x31, \tprod, \tlo, \v1
	.endm

	.macro N32_CONJ_QWORD_PAIR v0,v1,tlo,thi,tprod,qinv,factor,offset
	vpunpcklqdq \v1, \v0, \tlo
	vpunpckhqdq \v1, \v0, \thi
	vpmullw \qinv+\offset(%rip), \thi, \tprod
	vpmulhw \factor+\offset(%rip), \thi, \thi
	vpmulhw .Ln32_fwd_q(%rip), \tprod, \tprod
	vpsubw \tprod, \thi, \thi
	vpsubw \thi, \tlo, \tprod
	vpaddw \thi, \tlo, \tlo
	vpunpcklqdq \tprod, \tlo, \v0
	vpunpckhqdq \tprod, \tlo, \v1
	.endm

	/* Exact row-conjugated S1-S3.  S4/S5 must run after the five-blend row
	 * route: before that route, q+2/q+1 live in different physical waves. */
	.macro N32_CONJ_WAVE wave,wid,v0,v1,v2,v3,v4,v5,v6,v7
	N32_FORM_TOP_PAIR %ymm0,%ymm8,%ymm15,\v0
	N32_FORM_TOP_PAIR %ymm1,%ymm9,%ymm15,\v1
	N32_FORM_TOP_PAIR %ymm2,%ymm10,%ymm15,\v2
	N32_FORM_TOP_PAIR %ymm3,%ymm11,%ymm15,\v3
	N32_FORM_TOP_PAIR %ymm4,%ymm12,%ymm15,\v4
	N32_FORM_TOP_PAIR %ymm5,%ymm13,%ymm15,\v5
	N32_FORM_TOP_PAIR %ymm6,%ymm14,%ymm15,\v6
	vmovdqu %ymm14, 1536(%rsp)
	N32_FORM_TOP_PAIR %ymm7,%ymm14,%ymm15,\v7

	N32_MONT_SERIAL %ymm0,%ymm4,%ymm15,.Ln32_conj_b0_w\wid\()_s1_qinv,.Ln32_conj_b0_w\wid\()_s1_factor,0
	N32_MONT_SERIAL %ymm1,%ymm5,%ymm15,.Ln32_conj_b0_w\wid\()_s1_qinv,.Ln32_conj_b0_w\wid\()_s1_factor,32
	N32_MONT_SERIAL %ymm2,%ymm6,%ymm15,.Ln32_conj_b0_w\wid\()_s1_qinv,.Ln32_conj_b0_w\wid\()_s1_factor,64
	N32_MONT_SERIAL %ymm3,%ymm7,%ymm15,.Ln32_conj_b0_w\wid\()_s1_qinv,.Ln32_conj_b0_w\wid\()_s1_factor,96
	N32_MONT_SERIAL %ymm0,%ymm2,%ymm15,.Ln32_conj_b0_w\wid\()_s2_qinv,.Ln32_conj_b0_w\wid\()_s2_factor,0
	N32_MONT_SERIAL %ymm1,%ymm3,%ymm15,.Ln32_conj_b0_w\wid\()_s2_qinv,.Ln32_conj_b0_w\wid\()_s2_factor,32
	N32_MONT_SERIAL %ymm4,%ymm6,%ymm15,.Ln32_conj_b0_w\wid\()_s2_qinv,.Ln32_conj_b0_w\wid\()_s2_factor,64
	N32_MONT_SERIAL %ymm5,%ymm7,%ymm15,.Ln32_conj_b0_w\wid\()_s2_qinv,.Ln32_conj_b0_w\wid\()_s2_factor,96
	N32_MONT_SERIAL %ymm0,%ymm1,%ymm15,.Ln32_conj_b0_w\wid\()_s3_qinv,.Ln32_conj_b0_w\wid\()_s3_factor,0
	N32_MONT_SERIAL %ymm2,%ymm3,%ymm15,.Ln32_conj_b0_w\wid\()_s3_qinv,.Ln32_conj_b0_w\wid\()_s3_factor,32
	N32_MONT_SERIAL %ymm4,%ymm5,%ymm15,.Ln32_conj_b0_w\wid\()_s3_qinv,.Ln32_conj_b0_w\wid\()_s3_factor,64
	N32_MONT_SERIAL %ymm6,%ymm7,%ymm15,.Ln32_conj_b0_w\wid\()_s3_qinv,.Ln32_conj_b0_w\wid\()_s3_factor,96
	vmovdqu %ymm0, \wave+0(%rsp)
	vmovdqu %ymm1, \wave+32(%rsp)
	vmovdqu %ymm2, \wave+64(%rsp)
	vmovdqu %ymm3, \wave+96(%rsp)
	vmovdqu %ymm4, \wave+128(%rsp)
	vmovdqu %ymm5, \wave+160(%rsp)
	vmovdqu %ymm6, \wave+192(%rsp)
	vmovdqu %ymm7, \wave+224(%rsp)

	vmovdqu 1536(%rsp), %ymm6
	N32_MONT_PAR %ymm8,%ymm12,%ymm9,%ymm13,%ymm10,%ymm6,%ymm11,%ymm14, \
		%ymm0,%ymm1,%ymm2,%ymm3,.Ln32_conj_b1_w\wid\()_s1_qinv,.Ln32_conj_b1_w\wid\()_s1_factor
	N32_MONT_PAR %ymm8,%ymm10,%ymm9,%ymm11,%ymm12,%ymm6,%ymm13,%ymm14, \
		%ymm0,%ymm1,%ymm2,%ymm3,.Ln32_conj_b1_w\wid\()_s2_qinv,.Ln32_conj_b1_w\wid\()_s2_factor
	N32_MONT_PAR %ymm8,%ymm9,%ymm10,%ymm11,%ymm12,%ymm13,%ymm6,%ymm14, \
		%ymm0,%ymm1,%ymm2,%ymm3,.Ln32_conj_b1_w\wid\()_s3_qinv,.Ln32_conj_b1_w\wid\()_s3_factor
	vmovdqu %ymm8, \wave+256(%rsp)
	vmovdqu %ymm9, \wave+288(%rsp)
	vmovdqu %ymm10, \wave+320(%rsp)
	vmovdqu %ymm11, \wave+352(%rsp)
	vmovdqu %ymm12, \wave+384(%rsp)
	vmovdqu %ymm13, \wave+416(%rsp)
	vmovdqu %ymm6, \wave+448(%rsp)
	vmovdqu %ymm14, \wave+480(%rsp)
	.endm

	.macro N32_MONT_SERIAL lo,hi,tmp,qinv,factor,offset
	vpmullw \qinv+\offset(%rip), \hi, \tmp
	vpmulhw \factor+\offset(%rip), \hi, \hi
	vpmulhw .Ln32_fwd_q(%rip), \tmp, \tmp
	vpsubw \tmp, \hi, \hi
	vpsubw \hi, \lo, \tmp
	vpaddw \hi, \lo, \lo
	vmovdqa \tmp, \hi
	.endm

	.macro N32_MONT_PAR lo0,hi0,lo1,hi1,lo2,hi2,lo3,hi3,t0,t1,t2,t3,qinv,factor
	vpmullw \qinv+0(%rip), \hi0, \t0
	vpmullw \qinv+32(%rip), \hi1, \t1
	vpmullw \qinv+64(%rip), \hi2, \t2
	vpmullw \qinv+96(%rip), \hi3, \t3
	vpmulhw \factor+0(%rip), \hi0, \hi0
	vpmulhw \factor+32(%rip), \hi1, \hi1
	vpmulhw \factor+64(%rip), \hi2, \hi2
	vpmulhw \factor+96(%rip), \hi3, \hi3
	vpmulhw .Ln32_fwd_q(%rip), \t0, \t0
	vpmulhw .Ln32_fwd_q(%rip), \t1, \t1
	vpmulhw .Ln32_fwd_q(%rip), \t2, \t2
	vpmulhw .Ln32_fwd_q(%rip), \t3, \t3
	vpsubw \t0, \hi0, \hi0
	vpsubw \t1, \hi1, \hi1
	vpsubw \t2, \hi2, \hi2
	vpsubw \t3, \hi3, \hi3
	vpsubw \hi0, \lo0, \t0
	vpsubw \hi1, \lo1, \t1
	vpsubw \hi2, \lo2, \t2
	vpsubw \hi3, \lo3, \t3
	vpaddw \hi0, \lo0, \lo0
	vpaddw \hi1, \lo1, \lo1
	vpaddw \hi2, \lo2, \lo2
	vpaddw \hi3, \lo3, \lo3
	vmovdqa \t0, \hi0
	vmovdqa \t1, \hi1
	vmovdqa \t2, \hi2
	vmovdqa \t3, \hi3
	.endm

	.macro N32_MONT_PAR_QREG lo0,hi0,lo1,hi1,lo2,hi2,lo3,hi3,t0,t1,t2,t3,qinv,factor
	vpmullw \qinv+0(%rip), \hi0, \t0
	vpmullw \qinv+32(%rip), \hi1, \t1
	vpmullw \qinv+64(%rip), \hi2, \t2
	vpmullw \qinv+96(%rip), \hi3, \t3
	vpmulhw \factor+0(%rip), \hi0, \hi0
	vpmulhw \factor+32(%rip), \hi1, \hi1
	vpmulhw \factor+64(%rip), \hi2, \hi2
	vpmulhw \factor+96(%rip), \hi3, \hi3
	vpmulhw %ymm15, \t0, \t0
	vpmulhw %ymm15, \t1, \t1
	vpmulhw %ymm15, \t2, \t2
	vpmulhw %ymm15, \t3, \t3
	vpsubw \t0, \hi0, \hi0
	vpsubw \t1, \hi1, \hi1
	vpsubw \t2, \hi2, \hi2
	vpsubw \t3, \hi3, \hi3
	vpsubw \hi0, \lo0, \t0
	vpsubw \hi1, \lo1, \t1
	vpsubw \hi2, \lo2, \t2
	vpsubw \hi3, \lo3, \t3
	vpaddw \hi0, \lo0, \lo0
	vpaddw \hi1, \lo1, \lo1
	vpaddw \hi2, \lo2, \lo2
	vpaddw \hi3, \lo3, \lo3
	vmovdqa \t0, \hi0
	vmovdqa \t1, \hi1
	vmovdqa \t2, \hi2
	vmovdqa \t3, \hi3
	.endm

	/* Shared top split followed by two closed eight-YMM transforms.  The
	 * inactive branch temporarily occupies its final post-S3 scratch slots. */
	.macro N32_CONJ_WAVE_BRANCH_AT_TIME wave,wid,v0,v1,v2,v3,v4,v5,v6,v7
	N32_FORM_TOP_PAIR %ymm0,%ymm8,%ymm9,\v0
	vmovdqu %ymm8, \wave+256(%rsp)
	N32_FORM_TOP_PAIR %ymm1,%ymm8,%ymm9,\v1
	vmovdqu %ymm8, \wave+288(%rsp)
	N32_FORM_TOP_PAIR %ymm2,%ymm8,%ymm9,\v2
	vmovdqu %ymm8, \wave+320(%rsp)
	N32_FORM_TOP_PAIR %ymm3,%ymm8,%ymm9,\v3
	vmovdqu %ymm8, \wave+352(%rsp)
	N32_FORM_TOP_PAIR %ymm4,%ymm8,%ymm9,\v4
	vmovdqu %ymm8, \wave+384(%rsp)
	N32_FORM_TOP_PAIR %ymm5,%ymm8,%ymm9,\v5
	vmovdqu %ymm8, \wave+416(%rsp)
	N32_FORM_TOP_PAIR %ymm6,%ymm8,%ymm9,\v6
	vmovdqu %ymm8, \wave+448(%rsp)
	N32_FORM_TOP_PAIR %ymm7,%ymm8,%ymm9,\v7
	vmovdqu %ymm8, \wave+480(%rsp)
	vmovdqa .Ln32_fwd_q(%rip), %ymm15
	N32_MONT_PAR_QREG %ymm0,%ymm4,%ymm1,%ymm5,%ymm2,%ymm6,%ymm3,%ymm7, \
		%ymm8,%ymm9,%ymm10,%ymm11,.Ln32_conj_b0_w\wid\()_s1_qinv,.Ln32_conj_b0_w\wid\()_s1_factor
	N32_MONT_PAR_QREG %ymm0,%ymm2,%ymm1,%ymm3,%ymm4,%ymm6,%ymm5,%ymm7, \
		%ymm8,%ymm9,%ymm10,%ymm11,.Ln32_conj_b0_w\wid\()_s2_qinv,.Ln32_conj_b0_w\wid\()_s2_factor
	N32_MONT_PAR_QREG %ymm0,%ymm1,%ymm2,%ymm3,%ymm4,%ymm5,%ymm6,%ymm7, \
		%ymm8,%ymm9,%ymm10,%ymm11,.Ln32_conj_b0_w\wid\()_s3_qinv,.Ln32_conj_b0_w\wid\()_s3_factor
	vmovdqu %ymm0, \wave+0(%rsp)
	vmovdqu %ymm1, \wave+32(%rsp)
	vmovdqu %ymm2, \wave+64(%rsp)
	vmovdqu %ymm3, \wave+96(%rsp)
	vmovdqu %ymm4, \wave+128(%rsp)
	vmovdqu %ymm5, \wave+160(%rsp)
	vmovdqu %ymm6, \wave+192(%rsp)
	vmovdqu %ymm7, \wave+224(%rsp)
	vmovdqu \wave+256(%rsp), %ymm0
	vmovdqu \wave+288(%rsp), %ymm1
	vmovdqu \wave+320(%rsp), %ymm2
	vmovdqu \wave+352(%rsp), %ymm3
	vmovdqu \wave+384(%rsp), %ymm4
	vmovdqu \wave+416(%rsp), %ymm5
	vmovdqu \wave+448(%rsp), %ymm6
	vmovdqu \wave+480(%rsp), %ymm7
	N32_MONT_PAR_QREG %ymm0,%ymm4,%ymm1,%ymm5,%ymm2,%ymm6,%ymm3,%ymm7, \
		%ymm8,%ymm9,%ymm10,%ymm11,.Ln32_conj_b1_w\wid\()_s1_qinv,.Ln32_conj_b1_w\wid\()_s1_factor
	N32_MONT_PAR_QREG %ymm0,%ymm2,%ymm1,%ymm3,%ymm4,%ymm6,%ymm5,%ymm7, \
		%ymm8,%ymm9,%ymm10,%ymm11,.Ln32_conj_b1_w\wid\()_s2_qinv,.Ln32_conj_b1_w\wid\()_s2_factor
	N32_MONT_PAR_QREG %ymm0,%ymm1,%ymm2,%ymm3,%ymm4,%ymm5,%ymm6,%ymm7, \
		%ymm8,%ymm9,%ymm10,%ymm11,.Ln32_conj_b1_w\wid\()_s3_qinv,.Ln32_conj_b1_w\wid\()_s3_factor
	vmovdqu %ymm0, \wave+256(%rsp)
	vmovdqu %ymm1, \wave+288(%rsp)
	vmovdqu %ymm2, \wave+320(%rsp)
	vmovdqu %ymm3, \wave+352(%rsp)
	vmovdqu %ymm4, \wave+384(%rsp)
	vmovdqu %ymm5, \wave+416(%rsp)
	vmovdqu %ymm6, \wave+448(%rsp)
	vmovdqu %ymm7, \wave+480(%rsp)
	.endm

/* Form one physical cohort and retire both branches at post-S3. */
	.macro N32_FORWARD_WAVE wave,v0,v1,v2,v3,v4,v5,v6,v7
	N32_FORM_PAIR %ymm0,%ymm8,%ymm15,\v0
	N32_FORM_PAIR %ymm1,%ymm9,%ymm15,\v1
	N32_FORM_PAIR %ymm2,%ymm10,%ymm15,\v2
	N32_FORM_PAIR %ymm3,%ymm11,%ymm15,\v3
	N32_FORM_PAIR %ymm4,%ymm12,%ymm15,\v4
	N32_FORM_PAIR %ymm5,%ymm13,%ymm15,\v5
	N32_FORM_PAIR %ymm6,%ymm14,%ymm15,\v6
	vmovdqu %ymm14, 1536(%rsp)
	N32_FORM_PAIR %ymm7,%ymm14,%ymm15,\v7

	N32_RAW_DESTRUCTIVE %ymm0,%ymm4
	N32_RAW_DESTRUCTIVE %ymm1,%ymm5
	N32_RAW_DESTRUCTIVE %ymm2,%ymm6
	N32_RAW_DESTRUCTIVE %ymm3,%ymm7
	N32_MONT_SERIAL %ymm0,%ymm2,%ymm15,.Ln32_fwd_s2_qinv,.Ln32_fwd_s2_factor,0
	N32_MONT_SERIAL %ymm1,%ymm3,%ymm15,.Ln32_fwd_s2_qinv,.Ln32_fwd_s2_factor,32
	N32_MONT_SERIAL %ymm4,%ymm6,%ymm15,.Ln32_fwd_s2_qinv,.Ln32_fwd_s2_factor,64
	N32_MONT_SERIAL %ymm5,%ymm7,%ymm15,.Ln32_fwd_s2_qinv,.Ln32_fwd_s2_factor,96
	N32_MONT_SERIAL %ymm0,%ymm1,%ymm15,.Ln32_fwd_s3_qinv,.Ln32_fwd_s3_factor,0
	N32_MONT_SERIAL %ymm2,%ymm3,%ymm15,.Ln32_fwd_s3_qinv,.Ln32_fwd_s3_factor,32
	N32_MONT_SERIAL %ymm4,%ymm5,%ymm15,.Ln32_fwd_s3_qinv,.Ln32_fwd_s3_factor,64
	N32_MONT_SERIAL %ymm6,%ymm7,%ymm15,.Ln32_fwd_s3_qinv,.Ln32_fwd_s3_factor,96
	vmovdqu %ymm0, \wave+0(%rsp)
	vmovdqu %ymm1, \wave+32(%rsp)
	vmovdqu %ymm2, \wave+64(%rsp)
	vmovdqu %ymm3, \wave+96(%rsp)
	vmovdqu %ymm4, \wave+128(%rsp)
	vmovdqu %ymm5, \wave+160(%rsp)
	vmovdqu %ymm6, \wave+192(%rsp)
	vmovdqu %ymm7, \wave+224(%rsp)

	vmovdqu 1536(%rsp), %ymm6
	N32_RAW_DESTRUCTIVE %ymm8,%ymm12
	N32_RAW_DESTRUCTIVE %ymm9,%ymm13
	N32_RAW_DESTRUCTIVE %ymm10,%ymm6
	N32_RAW_DESTRUCTIVE %ymm11,%ymm14
	N32_MONT_PAR %ymm8,%ymm10,%ymm9,%ymm11,%ymm12,%ymm6,%ymm13,%ymm14, \
		%ymm0,%ymm1,%ymm2,%ymm3,.Ln32_fwd_s2_qinv,.Ln32_fwd_s2_factor
	N32_MONT_PAR %ymm8,%ymm9,%ymm10,%ymm11,%ymm12,%ymm13,%ymm6,%ymm14, \
		%ymm0,%ymm1,%ymm2,%ymm3,.Ln32_fwd_s3_qinv,.Ln32_fwd_s3_factor
	vmovdqu %ymm8, \wave+256(%rsp)
	vmovdqu %ymm9, \wave+288(%rsp)
	vmovdqu %ymm10, \wave+320(%rsp)
	vmovdqu %ymm11, \wave+352(%rsp)
	vmovdqu %ymm12, \wave+384(%rsp)
	vmovdqu %ymm13, \wave+416(%rsp)
	vmovdqu %ymm6, \wave+448(%rsp)
	vmovdqu %ymm14, \wave+480(%rsp)
	.endm

	.macro N32_ROUTE_DFT_A
	vmovdqu 0(%rsi), %ymm0
	vmovdqu 512(%rsi), %ymm4
	vmovdqu 1024(%rsi), %ymm5
	vpblendd $0x0c, %ymm4, %ymm0, %ymm6
	vpblendd $0x30, %ymm5, %ymm6, %ymm6
	vpblendd $0xc0, %ymm4, %ymm0, %ymm7
	vpblendd $0x03, %ymm5, %ymm7, %ymm7
	vpblendd $0xcc, %ymm5, %ymm4, %ymm8
	vpsubw %ymm8, %ymm7, %ymm9
	vpmullw .Ln32_fwd_omega_qinv(%rip), %ymm9, %ymm10
	vpmulhw .Ln32_fwd_omega_factor(%rip), %ymm9, %ymm9
	vpmulhw %ymm15, %ymm10, %ymm10
	vpsubw %ymm10, %ymm9, %ymm9
	vpsubw %ymm8, %ymm6, %ymm0
	vpaddw %ymm9, %ymm0, %ymm0
	vpsubw %ymm7, %ymm6, %ymm4
	vpsubw %ymm9, %ymm4, %ymm4
	vpaddw %ymm7, %ymm6, %ymm6
	vpaddw %ymm8, %ymm6, %ymm6
	.endm

	.macro N32_ROUTE_DFT_B
	vmovdqu 32(%rsi), %ymm1
	vmovdqu 544(%rsi), %ymm2
	vmovdqu 1056(%rsi), %ymm3
	vpblendd $0x0c, %ymm2, %ymm1, %ymm5
	vpblendd $0x30, %ymm3, %ymm5, %ymm5
	vpblendd $0xc0, %ymm2, %ymm1, %ymm7
	vpblendd $0x03, %ymm3, %ymm7, %ymm7
	vpblendd $0xcc, %ymm3, %ymm2, %ymm8
	vpsubw %ymm8, %ymm7, %ymm9
	vpmullw .Ln32_fwd_omega_qinv(%rip), %ymm9, %ymm10
	vpmulhw .Ln32_fwd_omega_factor(%rip), %ymm9, %ymm9
	vpmulhw %ymm15, %ymm10, %ymm10
	vpsubw %ymm10, %ymm9, %ymm9
	vpsubw %ymm8, %ymm5, %ymm1
	vpaddw %ymm9, %ymm1, %ymm1
	vpsubw %ymm7, %ymm5, %ymm2
	vpsubw %ymm9, %ymm2, %ymm2
	vpaddw %ymm7, %ymm5, %ymm5
	vpaddw %ymm8, %ymm5, %ymm5
	.endm

	/* Route two adjacent q-blocks from the three physical waves.  The six
	 * outputs are A=(ymm6,ymm7,ymm8), B=(ymm3,ymm4,ymm5), with the typed
	 * [0,1,2]/[0,2,1] row reflection already present. */
	.macro N32_CONJ_ROUTE_PAIR
	vmovdqu 0(%rsi), %ymm0
	vmovdqu 512(%rsi), %ymm4
	vmovdqu 1024(%rsi), %ymm5
	vpblendd $0x0c, %ymm4, %ymm0, %ymm6
	vpblendd $0x30, %ymm5, %ymm6, %ymm6
	vpblendd $0xc0, %ymm4, %ymm0, %ymm7
	vpblendd $0x03, %ymm5, %ymm7, %ymm7
	vpblendd $0xcc, %ymm5, %ymm4, %ymm8
	vmovdqu 32(%rsi), %ymm0
	vmovdqu 544(%rsi), %ymm1
	vmovdqu 1056(%rsi), %ymm2
	vpblendd $0x0c, %ymm1, %ymm0, %ymm3
	vpblendd $0x30, %ymm2, %ymm3, %ymm3
	vpblendd $0xc0, %ymm1, %ymm0, %ymm4
	vpblendd $0x03, %ymm2, %ymm4, %ymm4
	vpblendd $0xcc, %ymm2, %ymm1, %ymm5
	.endm

	.macro N32_CONJ_HALF_PAIR_PTR v0,v1,tlo,thi,tprod,offset
	vperm2i128 $0x20, \v1, \v0, \tlo
	vperm2i128 $0x31, \v1, \v0, \thi
	vpmullw \offset(%r8), \thi, \tprod
	vpmulhw \offset(%r9), \thi, \thi
	vpmulhw %ymm15, \tprod, \tprod
	vpsubw \tprod, \thi, \thi
	vpsubw \thi, \tlo, \tprod
	vpaddw \thi, \tlo, \tlo
	vperm2i128 $0x20, \tprod, \tlo, \v0
	vperm2i128 $0x31, \tprod, \tlo, \v1
	.endm

	.macro N32_CONJ_HALF_CROSS_PTR v0,v1,tlo,thi,tprod,offset
	vperm2i128 $0x20, \v1, \v0, \tlo
	vperm2i128 $0x13, \v1, \v0, \thi
	vpmullw \offset(%r8), \thi, \tprod
	vpmulhw \offset(%r9), \thi, \thi
	vpmulhw %ymm15, \tprod, \tprod
	vpsubw \tprod, \thi, \thi
	vpsubw \thi, \tlo, \tprod
	vpaddw \thi, \tlo, \tlo
	vperm2i128 $0x30, \tprod, \tlo, \v0
	vperm2i128 $0x21, \tprod, \tlo, \v1
	.endm

	.macro N32_CONJ_QWORD_PAIR_PTR v0,v1,tlo,thi,tprod,offset
	vpunpcklqdq \v1, \v0, \tlo
	vpunpckhqdq \v1, \v0, \thi
	vpmullw \offset(%r10), \thi, \tprod
	vpmulhw \offset(%rax), \thi, \thi
	vpmulhw %ymm15, \tprod, \tprod
	vpsubw \tprod, \thi, \thi
	vpsubw \thi, \tlo, \tprod
	vpaddw \thi, \tlo, \tlo
	vpunpcklqdq \tprod, \tlo, \v0
	vpunpckhqdq \tprod, \tlo, \v1
	.endm

	/* Three independent S4 butterflies using the nine registers left free by
	 * the six-data-plus-q suffix frontier.  Arithmetic and representatives are
	 * bit-identical to three N32_CONJ_{HALF_PAIR,HALF_CROSS}_PTR calls. */
	.macro N32_CONJ_S4_3WAY
	vperm2i128 $0x20, %ymm3, %ymm6, %ymm0
	vperm2i128 $0x31, %ymm3, %ymm6, %ymm1
	vperm2i128 $0x20, %ymm8, %ymm7, %ymm9
	vperm2i128 $0x13, %ymm8, %ymm7, %ymm10
	vperm2i128 $0x20, %ymm5, %ymm4, %ymm12
	vperm2i128 $0x13, %ymm5, %ymm4, %ymm13
	vpmullw 0(%r8),  %ymm1,  %ymm2
	vpmullw 32(%r8), %ymm10, %ymm11
	vpmullw 64(%r8), %ymm13, %ymm14
	vpmulhw 0(%r9),  %ymm1,  %ymm1
	vpmulhw 32(%r9), %ymm10, %ymm10
	vpmulhw 64(%r9), %ymm13, %ymm13
	vpmulhw %ymm15, %ymm2,  %ymm2
	vpmulhw %ymm15, %ymm11, %ymm11
	vpmulhw %ymm15, %ymm14, %ymm14
	vpsubw %ymm2,  %ymm1,  %ymm1
	vpsubw %ymm11, %ymm10, %ymm10
	vpsubw %ymm14, %ymm13, %ymm13
	vpsubw %ymm1,  %ymm0,  %ymm2
	vpsubw %ymm10, %ymm9,  %ymm11
	vpsubw %ymm13, %ymm12, %ymm14
	vpaddw %ymm1,  %ymm0,  %ymm0
	vpaddw %ymm10, %ymm9,  %ymm9
	vpaddw %ymm13, %ymm12, %ymm12
	vperm2i128 $0x20, %ymm2,  %ymm0,  %ymm6
	vperm2i128 $0x31, %ymm2,  %ymm0,  %ymm3
	vperm2i128 $0x30, %ymm11, %ymm9,  %ymm7
	vperm2i128 $0x21, %ymm11, %ymm9,  %ymm8
	vperm2i128 $0x30, %ymm14, %ymm12, %ymm4
	vperm2i128 $0x21, %ymm14, %ymm12, %ymm5
	.endm

	/* The analogous three-chain schedule for S5. */
	.macro N32_CONJ_S5_3WAY
	vpunpcklqdq %ymm3, %ymm6, %ymm0
	vpunpckhqdq %ymm3, %ymm6, %ymm1
	vpunpcklqdq %ymm8, %ymm7, %ymm9
	vpunpckhqdq %ymm8, %ymm7, %ymm10
	vpunpcklqdq %ymm5, %ymm4, %ymm12
	vpunpckhqdq %ymm5, %ymm4, %ymm13
	vpmullw 0(%r10),  %ymm1,  %ymm2
	vpmullw 32(%r10), %ymm10, %ymm11
	vpmullw 64(%r10), %ymm13, %ymm14
	vpmulhw 0(%rax),  %ymm1,  %ymm1
	vpmulhw 32(%rax), %ymm10, %ymm10
	vpmulhw 64(%rax), %ymm13, %ymm13
	vpmulhw %ymm15, %ymm2,  %ymm2
	vpmulhw %ymm15, %ymm11, %ymm11
	vpmulhw %ymm15, %ymm14, %ymm14
	vpsubw %ymm2,  %ymm1,  %ymm1
	vpsubw %ymm11, %ymm10, %ymm10
	vpsubw %ymm14, %ymm13, %ymm13
	vpsubw %ymm1,  %ymm0,  %ymm2
	vpsubw %ymm10, %ymm9,  %ymm11
	vpsubw %ymm13, %ymm12, %ymm14
	vpaddw %ymm1,  %ymm0,  %ymm0
	vpaddw %ymm10, %ymm9,  %ymm9
	vpaddw %ymm13, %ymm12, %ymm12
	vpunpcklqdq %ymm2,  %ymm0,  %ymm6
	vpunpckhqdq %ymm2,  %ymm0,  %ymm3
	vpunpcklqdq %ymm11, %ymm9,  %ymm7
	vpunpckhqdq %ymm11, %ymm9,  %ymm8
	vpunpcklqdq %ymm14, %ymm12, %ymm4
	vpunpckhqdq %ymm14, %ymm12, %ymm5
	.endm

	/* MLKEM-style distributed updates.  Launch q*C first, use its latency to
	 * form L+H and L-H, then apply -C/+C.  The six original data registers
	 * are dead after extraction and provide the otherwise missing outputs. */
	.macro N32_CONJ_S4_MLK3WAY
	vperm2i128 $0x20, %ymm3, %ymm6, %ymm0
	vperm2i128 $0x31, %ymm3, %ymm6, %ymm1
	vperm2i128 $0x20, %ymm8, %ymm7, %ymm9
	vperm2i128 $0x13, %ymm8, %ymm7, %ymm10
	vperm2i128 $0x20, %ymm5, %ymm4, %ymm12
	vperm2i128 $0x13, %ymm5, %ymm4, %ymm13
	vpmullw 0(%r8),  %ymm1,  %ymm2
	vpmullw 32(%r8), %ymm10, %ymm11
	vpmullw 64(%r8), %ymm13, %ymm14
	vpmulhw 0(%r9),  %ymm1,  %ymm1
	vpmulhw 32(%r9), %ymm10, %ymm10
	vpmulhw 64(%r9), %ymm13, %ymm13
	vpmulhw %ymm15, %ymm2,  %ymm2
	vpmulhw %ymm15, %ymm11, %ymm11
	vpmulhw %ymm15, %ymm14, %ymm14
	vpsubw %ymm1,  %ymm0,  %ymm3
	vpsubw %ymm10, %ymm9,  %ymm8
	vpsubw %ymm13, %ymm12, %ymm5
	vpaddw %ymm1,  %ymm0,  %ymm0
	vpaddw %ymm10, %ymm9,  %ymm9
	vpaddw %ymm13, %ymm12, %ymm12
	vpaddw %ymm2,  %ymm3,  %ymm3
	vpaddw %ymm11, %ymm8,  %ymm8
	vpaddw %ymm14, %ymm5,  %ymm5
	vpsubw %ymm2,  %ymm0,  %ymm0
	vpsubw %ymm11, %ymm9,  %ymm9
	vpsubw %ymm14, %ymm12, %ymm12
	vperm2i128 $0x20, %ymm3, %ymm0,  %ymm6
	vperm2i128 $0x31, %ymm3, %ymm0,  %ymm3
	vperm2i128 $0x30, %ymm8, %ymm9,  %ymm7
	vperm2i128 $0x21, %ymm8, %ymm9,  %ymm8
	vperm2i128 $0x30, %ymm5, %ymm12, %ymm4
	vperm2i128 $0x21, %ymm5, %ymm12, %ymm5
	.endm

	.macro N32_CONJ_S5_MLK3WAY
	vpunpcklqdq %ymm3, %ymm6, %ymm0
	vpunpckhqdq %ymm3, %ymm6, %ymm1
	vpunpcklqdq %ymm8, %ymm7, %ymm9
	vpunpckhqdq %ymm8, %ymm7, %ymm10
	vpunpcklqdq %ymm5, %ymm4, %ymm12
	vpunpckhqdq %ymm5, %ymm4, %ymm13
	vpmullw 0(%r10),  %ymm1,  %ymm2
	vpmullw 32(%r10), %ymm10, %ymm11
	vpmullw 64(%r10), %ymm13, %ymm14
	vpmulhw 0(%rax),  %ymm1,  %ymm1
	vpmulhw 32(%rax), %ymm10, %ymm10
	vpmulhw 64(%rax), %ymm13, %ymm13
	vpmulhw %ymm15, %ymm2,  %ymm2
	vpmulhw %ymm15, %ymm11, %ymm11
	vpmulhw %ymm15, %ymm14, %ymm14
	vpsubw %ymm1,  %ymm0,  %ymm3
	vpsubw %ymm10, %ymm9,  %ymm8
	vpsubw %ymm13, %ymm12, %ymm5
	vpaddw %ymm1,  %ymm0,  %ymm0
	vpaddw %ymm10, %ymm9,  %ymm9
	vpaddw %ymm13, %ymm12, %ymm12
	vpaddw %ymm2,  %ymm3,  %ymm3
	vpaddw %ymm11, %ymm8,  %ymm8
	vpaddw %ymm14, %ymm5,  %ymm5
	vpsubw %ymm2,  %ymm0,  %ymm0
	vpsubw %ymm11, %ymm9,  %ymm9
	vpsubw %ymm14, %ymm12, %ymm12
	vpunpcklqdq %ymm3, %ymm0,  %ymm6
	vpunpckhqdq %ymm3, %ymm0,  %ymm3
	vpunpcklqdq %ymm8, %ymm9,  %ymm7
	vpunpckhqdq %ymm8, %ymm9,  %ymm8
	vpunpcklqdq %ymm5, %ymm12, %ymm4
	vpunpckhqdq %ymm5, %ymm12, %ymm5
	.endm

	.macro N32_CONJ_TYPED_DFT v0,v1,v2,t0,t1,t2,branch
	/* Residual row 0 is identity.  Typed rows 1/2 use half-reflected tables. */
	vpmullw .Ln32_conj_b\branch\()_residual1_qinv(%rip), \v1, \t0
	vpmulhw .Ln32_conj_b\branch\()_residual1_factor(%rip), \v1, \v1
	vpmulhw %ymm15, \t0, \t0
	vpsubw \t0, \v1, \v1
	vpmullw .Ln32_conj_b\branch\()_residual2_qinv(%rip), \v2, \t0
	vpmulhw .Ln32_conj_b\branch\()_residual2_factor(%rip), \v2, \v2
	vpmulhw %ymm15, \t0, \t0
	vpsubw \t0, \v2, \v2
	vpsubw \v2, \v1, \t0
	vpmullw .Ln32_fwd_omega_qinv(%rip), \t0, \t1
	vpmulhw .Ln32_fwd_omega_factor(%rip), \t0, \t0
	vpmulhw %ymm15, \t1, \t1
	vpsubw \t1, \t0, \t0
	vmovdqa \v0, \t2
	vpaddw \v1, \v0, \v0
	vpaddw \v2, \v0, \v0
	vpsubw \v2, \t2, \t1
	vpaddw \t0, \t1, \t1
	vpsubw \v1, \t2, \v2
	vpsubw \t0, \v2, \v2
	vmovdqa \t1, \v1
	.endm

	/* Two independent typed DFT3s with separate temporaries.  The result
	 * assignment is intentionally (ymm6,ymm1,ymm2) and
	 * (ymm3,ymm10,ymm11), so neither DFT needs its two register copies. */
	.macro N32_CONJ_TYPED_DFT_DUAL branch
	/* Residual row 1, both packets. */
	vpmullw .Ln32_conj_b\branch\()_residual1_qinv(%rip), %ymm7, %ymm0
	vpmullw .Ln32_conj_b\branch\()_residual1_qinv(%rip), %ymm4, %ymm9
	vpmulhw .Ln32_conj_b\branch\()_residual1_factor(%rip), %ymm7, %ymm7
	vpmulhw .Ln32_conj_b\branch\()_residual1_factor(%rip), %ymm4, %ymm4
	vpmulhw %ymm15, %ymm0, %ymm0
	vpmulhw %ymm15, %ymm9, %ymm9
	vpsubw %ymm0, %ymm7, %ymm7
	vpsubw %ymm9, %ymm4, %ymm4
	/* Residual row 2, both packets. */
	vpmullw .Ln32_conj_b\branch\()_residual2_qinv(%rip), %ymm8, %ymm0
	vpmullw .Ln32_conj_b\branch\()_residual2_qinv(%rip), %ymm5, %ymm9
	vpmulhw .Ln32_conj_b\branch\()_residual2_factor(%rip), %ymm8, %ymm8
	vpmulhw .Ln32_conj_b\branch\()_residual2_factor(%rip), %ymm5, %ymm5
	vpmulhw %ymm15, %ymm0, %ymm0
	vpmulhw %ymm15, %ymm9, %ymm9
	vpsubw %ymm0, %ymm8, %ymm8
	vpsubw %ymm9, %ymm5, %ymm5
	/* omega * (row1-row2), both packets. */
	vpsubw %ymm8, %ymm7, %ymm0
	vpsubw %ymm5, %ymm4, %ymm9
	vpmullw .Ln32_fwd_omega_qinv(%rip), %ymm0, %ymm1
	vpmullw .Ln32_fwd_omega_qinv(%rip), %ymm9, %ymm10
	vpmulhw .Ln32_fwd_omega_factor(%rip), %ymm0, %ymm0
	vpmulhw .Ln32_fwd_omega_factor(%rip), %ymm9, %ymm9
	vpmulhw %ymm15, %ymm1, %ymm1
	vpmulhw %ymm15, %ymm10, %ymm10
	vpsubw %ymm1, %ymm0, %ymm0
	vpsubw %ymm10, %ymm9, %ymm9
	/* Move-free result formation. */
	vpsubw %ymm8, %ymm6, %ymm1
	vpsubw %ymm5, %ymm3, %ymm10
	vpaddw %ymm0, %ymm1, %ymm1
	vpaddw %ymm9, %ymm10, %ymm10
	vpsubw %ymm7, %ymm6, %ymm2
	vpsubw %ymm4, %ymm3, %ymm11
	vpsubw %ymm0, %ymm2, %ymm2
	vpsubw %ymm9, %ymm11, %ymm11
	vpaddw %ymm7, %ymm6, %ymm6
	vpaddw %ymm4, %ymm3, %ymm3
	vpaddw %ymm8, %ymm6, %ymm6
	vpaddw %ymm5, %ymm3, %ymm3
	.endm

	.macro N32_CONJ_SUFFIX_BRANCH branch
	leaq .Ln32_conj_b\branch\()_suffix_s4_qinv(%rip), %r8
	leaq .Ln32_conj_b\branch\()_suffix_s4_factor(%rip), %r9
	leaq .Ln32_conj_b\branch\()_suffix_s5_qinv(%rip), %r10
	leaq .Ln32_conj_b\branch\()_suffix_s5_factor(%rip), %rax
	movl $4, %ecx
.Ln32_conj_suffix_loop\@:
	N32_CONJ_ROUTE_PAIR
	N32_CONJ_HALF_PAIR_PTR %ymm6,%ymm3,%ymm0,%ymm1,%ymm2,0
	N32_CONJ_HALF_CROSS_PTR %ymm7,%ymm8,%ymm0,%ymm1,%ymm2,32
	N32_CONJ_HALF_CROSS_PTR %ymm4,%ymm5,%ymm0,%ymm1,%ymm2,64
	N32_CONJ_QWORD_PAIR_PTR %ymm6,%ymm3,%ymm0,%ymm1,%ymm2,0
	N32_CONJ_QWORD_PAIR_PTR %ymm7,%ymm8,%ymm0,%ymm1,%ymm2,32
	N32_CONJ_QWORD_PAIR_PTR %ymm4,%ymm5,%ymm0,%ymm1,%ymm2,64
	/* The old 5.5k producer bound silently Montgomery-reduced residual row 0.
	 * Its factor is identity, so use the cheaper three-instruction center10
	 * checkpoint on only these two row-0 packets. */
	vpmulhrsw .Ln32_fwd_center10(%rip), %ymm6, %ymm0
	vpmullw %ymm15, %ymm0, %ymm0
	vpsubw %ymm0, %ymm6, %ymm6
	vpmulhrsw .Ln32_fwd_center10(%rip), %ymm3, %ymm0
	vpmullw %ymm15, %ymm0, %ymm0
	vpsubw %ymm0, %ymm3, %ymm3
	N32_CONJ_TYPED_DFT %ymm6,%ymm7,%ymm8,%ymm0,%ymm1,%ymm2,\branch
	N32_CONJ_TYPED_DFT %ymm3,%ymm4,%ymm5,%ymm0,%ymm1,%ymm2,\branch
	vmovdqu %ymm6, 0(%rdi)
	vmovdqu %ymm7, 32(%rdi)
	vmovdqu %ymm8, 64(%rdi)
	vmovdqu %ymm3, 96(%rdi)
	vmovdqu %ymm4, 128(%rdi)
	vmovdqu %ymm5, 160(%rdi)
	addq $64, %rsi
	addq $192, %rdi
	addq $96, %r8
	addq $96, %r9
	addq $96, %r10
	addq $96, %rax
	decl %ecx
	jne .Ln32_conj_suffix_loop\@
	.endm

	.macro N32_CONJ_SUFFIX_BRANCH_3WAY branch
	leaq .Ln32_conj_b\branch\()_suffix_s4_qinv(%rip), %r8
	leaq .Ln32_conj_b\branch\()_suffix_s4_factor(%rip), %r9
	leaq .Ln32_conj_b\branch\()_suffix_s5_qinv(%rip), %r10
	leaq .Ln32_conj_b\branch\()_suffix_s5_factor(%rip), %rax
	movl $4, %ecx
.Ln32_conj_suffix_3way_loop\@:
	N32_CONJ_ROUTE_PAIR
	N32_CONJ_S4_3WAY
	N32_CONJ_S5_3WAY
	/* Keep checkpoint and DFT order bit-identical to the control. */
	vpmulhrsw .Ln32_fwd_center10(%rip), %ymm6, %ymm0
	vpmullw %ymm15, %ymm0, %ymm0
	vpsubw %ymm0, %ymm6, %ymm6
	vpmulhrsw .Ln32_fwd_center10(%rip), %ymm3, %ymm0
	vpmullw %ymm15, %ymm0, %ymm0
	vpsubw %ymm0, %ymm3, %ymm3
	N32_CONJ_TYPED_DFT %ymm6,%ymm7,%ymm8,%ymm0,%ymm1,%ymm2,\branch
	N32_CONJ_TYPED_DFT %ymm3,%ymm4,%ymm5,%ymm0,%ymm1,%ymm2,\branch
	vmovdqu %ymm6, 0(%rdi)
	vmovdqu %ymm7, 32(%rdi)
	vmovdqu %ymm8, 64(%rdi)
	vmovdqu %ymm3, 96(%rdi)
	vmovdqu %ymm4, 128(%rdi)
	vmovdqu %ymm5, 160(%rdi)
	addq $64, %rsi
	addq $192, %rdi
	addq $96, %r8
	addq $96, %r9
	addq $96, %r10
	addq $96, %rax
	decl %ecx
	jne .Ln32_conj_suffix_3way_loop\@
	.endm

	.macro N32_CONJ_SUFFIX_BRANCH_DFT_DUAL branch
	leaq .Ln32_conj_b\branch\()_suffix_s4_qinv(%rip), %r8
	leaq .Ln32_conj_b\branch\()_suffix_s4_factor(%rip), %r9
	leaq .Ln32_conj_b\branch\()_suffix_s5_qinv(%rip), %r10
	leaq .Ln32_conj_b\branch\()_suffix_s5_factor(%rip), %rax
	movl $4, %ecx
.Ln32_conj_suffix_dft_dual_loop\@:
	N32_CONJ_ROUTE_PAIR
	N32_CONJ_HALF_PAIR_PTR %ymm6,%ymm3,%ymm0,%ymm1,%ymm2,0
	N32_CONJ_HALF_CROSS_PTR %ymm7,%ymm8,%ymm0,%ymm1,%ymm2,32
	N32_CONJ_HALF_CROSS_PTR %ymm4,%ymm5,%ymm0,%ymm1,%ymm2,64
	N32_CONJ_QWORD_PAIR_PTR %ymm6,%ymm3,%ymm0,%ymm1,%ymm2,0
	N32_CONJ_QWORD_PAIR_PTR %ymm7,%ymm8,%ymm0,%ymm1,%ymm2,32
	N32_CONJ_QWORD_PAIR_PTR %ymm4,%ymm5,%ymm0,%ymm1,%ymm2,64
	/* Center the two independent row-0 packets in parallel. */
	vpmulhrsw .Ln32_fwd_center10(%rip), %ymm6, %ymm0
	vpmulhrsw .Ln32_fwd_center10(%rip), %ymm3, %ymm1
	vpmullw %ymm15, %ymm0, %ymm0
	vpmullw %ymm15, %ymm1, %ymm1
	vpsubw %ymm0, %ymm6, %ymm6
	vpsubw %ymm1, %ymm3, %ymm3
	N32_CONJ_TYPED_DFT_DUAL \branch
	vmovdqu %ymm6, 0(%rdi)
	vmovdqu %ymm1, 32(%rdi)
	vmovdqu %ymm2, 64(%rdi)
	vmovdqu %ymm3, 96(%rdi)
	vmovdqu %ymm10, 128(%rdi)
	vmovdqu %ymm11, 160(%rdi)
	addq $64, %rsi
	addq $192, %rdi
	addq $96, %r8
	addq $96, %r9
	addq $96, %r10
	addq $96, %rax
	decl %ecx
	jne .Ln32_conj_suffix_dft_dual_loop\@
	.endm

	.macro N32_CONJ_SUFFIX_BRANCH_MLKSTYLE branch
	leaq .Ln32_conj_b\branch\()_suffix_s4_qinv(%rip), %r8
	leaq .Ln32_conj_b\branch\()_suffix_s4_factor(%rip), %r9
	leaq .Ln32_conj_b\branch\()_suffix_s5_qinv(%rip), %r10
	leaq .Ln32_conj_b\branch\()_suffix_s5_factor(%rip), %rax
	movl $4, %ecx
.Ln32_conj_suffix_mlkstyle_loop\@:
	N32_CONJ_ROUTE_PAIR
	N32_CONJ_S4_MLK3WAY
	N32_CONJ_S5_MLK3WAY
	vpmulhrsw .Ln32_fwd_center10(%rip), %ymm6, %ymm0
	vpmulhrsw .Ln32_fwd_center10(%rip), %ymm3, %ymm1
	vpmullw %ymm15, %ymm0, %ymm0
	vpmullw %ymm15, %ymm1, %ymm1
	vpsubw %ymm0, %ymm6, %ymm6
	vpsubw %ymm1, %ymm3, %ymm3
	N32_CONJ_TYPED_DFT_DUAL \branch
	vmovdqu %ymm6, 0(%rdi)
	vmovdqu %ymm1, 32(%rdi)
	vmovdqu %ymm2, 64(%rdi)
	vmovdqu %ymm3, 96(%rdi)
	vmovdqu %ymm10, 128(%rdi)
	vmovdqu %ymm11, 160(%rdi)
	addq $64, %rsi
	addq $192, %rdi
	addq $96, %r8
	addq $96, %r9
	addq $96, %r10
	addq $96, %rax
	decl %ecx
	jne .Ln32_conj_suffix_mlkstyle_loop\@
	.endm

	.macro N32_MONT_HALF_PAIR v0,v1,offset
	vperm2i128 $0x20, \v1, \v0, %ymm7
	vperm2i128 $0x31, \v1, \v0, %ymm8
	vpmullw \offset(%r8), %ymm8, %ymm9
	vpmulhw \offset(%r9), %ymm8, %ymm8
	vpmulhw %ymm15, %ymm9, %ymm9
	vpsubw %ymm9, %ymm8, %ymm8
	vpsubw %ymm8, %ymm7, %ymm9
	vpaddw %ymm8, %ymm7, %ymm7
	vperm2i128 $0x20, %ymm9, %ymm7, \v0
	vperm2i128 $0x31, %ymm9, %ymm7, \v1
	.endm

	/* S4 over the two typed k3=1/2 packets of one group. */
	.macro N32_MONT_HALF_CROSS v0,v1,offset
	vperm2i128 $0x20, \v1, \v0, %ymm7
	/* Reverse the two high halves so row 1/2 match the packed low halves. */
	vperm2i128 $0x13, \v1, \v0, %ymm8
	vpmullw \offset(%r8), %ymm8, %ymm9
	vpmulhw \offset(%r9), %ymm8, %ymm8
	vpmulhw %ymm15, %ymm9, %ymm9
	vpsubw %ymm9, %ymm8, %ymm8
	vpsubw %ymm8, %ymm7, %ymm9
	vpaddw %ymm8, %ymm7, %ymm7
	/* Restore low1|high2 and low2|high1 typed packets. */
	vperm2i128 $0x30, %ymm9, %ymm7, \v0
	vperm2i128 $0x21, %ymm9, %ymm7, \v1
	.endm

	.macro N32_MONT_QWORD_PAIR v0,v1,offset
	vpunpcklqdq \v1, \v0, %ymm7
	vpunpckhqdq \v1, \v0, %ymm8
	vpmullw \offset(%r10), %ymm8, %ymm9
	vpmulhw \offset(%rax), %ymm8, %ymm8
	vpmulhw %ymm15, %ymm9, %ymm9
	vpsubw %ymm9, %ymm8, %ymm8
	vpsubw %ymm8, %ymm7, %ymm9
	vpaddw %ymm8, %ymm7, %ymm7
	vpunpcklqdq %ymm9, %ymm7, \v0
	vpunpckhqdq %ymm9, %ymm7, \v1
	.endm

	.macro N32_CENTER value
	vpmulhrsw .Ln32_fwd_center10(%rip), \value, %ymm7
	vpmullw %ymm15, %ymm7, %ymm7
	vpsubw %ymm7, \value, \value
	.endm

	.macro N32_SUFFIX_BRANCH center
	leaq .Ln32_fwd_s4_pair_qinv(%rip), %r8
	leaq .Ln32_fwd_s4_pair_factor(%rip), %r9
	leaq .Ln32_fwd_s5_pair_qinv(%rip), %r10
	leaq .Ln32_fwd_s5_pair_factor(%rip), %rax
	movl $4, %ecx
.Ln32_suffix_loop\@:
	N32_ROUTE_DFT_A
	N32_ROUTE_DFT_B
	N32_MONT_HALF_PAIR %ymm6,%ymm5,0
	N32_MONT_HALF_CROSS %ymm0,%ymm4,32
	N32_MONT_HALF_CROSS %ymm1,%ymm2,64
	N32_MONT_QWORD_PAIR %ymm6,%ymm5,0
	N32_MONT_QWORD_PAIR %ymm0,%ymm4,32
	N32_MONT_QWORD_PAIR %ymm1,%ymm2,64
	.if \center
	N32_CENTER %ymm6
	N32_CENTER %ymm0
	N32_CENTER %ymm4
	N32_CENTER %ymm5
	N32_CENTER %ymm1
	N32_CENTER %ymm2
	.endif
	vmovdqu %ymm6, 0(%rdi)
	vmovdqu %ymm0, 32(%rdi)
	vmovdqu %ymm4, 64(%rdi)
	vmovdqu %ymm5, 96(%rdi)
	vmovdqu %ymm1, 128(%rdi)
	vmovdqu %ymm2, 160(%rdi)
	addq $64, %rsi
	addq $192, %rdi
	addq $96, %r8
	addq $96, %r9
	addq $96, %r10
	addq $96, %rax
	decl %ecx
	jne .Ln32_suffix_loop\@
	.endm

	.macro N32_SUFFIX_ALL center
	vmovdqa .Ln32_fwd_q(%rip), %ymm15
	movq %rsp, %rsi
	movq %r11, %rdi
	N32_SUFFIX_BRANCH \center
	leaq 256(%rsp), %rsi
	leaq 768(%r11), %rdi
	N32_SUFFIX_BRANCH \center
	.endm

	.section .text.gt32_n32_forward_half_asm,"ax",@progbits
	.p2align 6
	.globl gt32_n32_forward_half_raw_asm
	.type gt32_n32_forward_half_raw_asm,@function
gt32_n32_forward_half_raw_asm:
	xorl %eax, %eax
	jmp .Ln32_forward_common
	.size gt32_n32_forward_half_raw_asm,.-gt32_n32_forward_half_raw_asm

	.p2align 5
	.globl gt32_n32_forward_half_centered_asm
	.type gt32_n32_forward_half_centered_asm,@function
gt32_n32_forward_half_centered_asm:
	movl $1, %eax
.Ln32_forward_common:
	movq %rsp, %rdx
	movq %rdi, %r11
	andq $-64, %rsp
	subq $1600, %rsp
	N32_FORWARD_WAVE 0,0,9,18,3,12,21,6,15
	N32_FORWARD_WAVE 512,8,17,2,11,20,5,14,23
	N32_FORWARD_WAVE 1024,16,1,10,19,4,13,22,7
	testl %eax, %eax
	jne .Ln32_forward_centered_suffix
	N32_SUFFIX_ALL 0
	jmp .Ln32_forward_done
.Ln32_forward_centered_suffix:
	N32_SUFFIX_ALL 1
.Ln32_forward_done:
	movq %rdx, %rsp
	vzeroupper
	ret
	.size gt32_n32_forward_half_centered_asm,.-gt32_n32_forward_half_centered_asm

	.section .text.gt32_n32_forward_half_conjugated_asm,"ax",@progbits
	.p2align 6
	.globl gt32_n32_forward_half_conjugated_asm
	.type gt32_n32_forward_half_conjugated_asm,@function
gt32_n32_forward_half_conjugated_asm:
	movq %rsp, %rdx
	movq %rdi, %r11
	andq $-64, %rsp
	subq $1664, %rsp
	N32_CONJ_WAVE 0,0,0,9,18,3,12,21,6,15
	N32_CONJ_WAVE 512,1,8,17,2,11,20,5,14,23
	N32_CONJ_WAVE 1024,2,16,1,10,19,4,13,22,7
	vmovdqa .Ln32_fwd_q(%rip), %ymm15
	movq %rsp, %rsi
	movq %r11, %rdi
	N32_CONJ_SUFFIX_BRANCH 0
	leaq 256(%rsp), %rsi
	leaq 768(%r11), %rdi
	N32_CONJ_SUFFIX_BRANCH 1
	movq %rdx, %rsp
	vzeroupper
	ret
	.size gt32_n32_forward_half_conjugated_asm,.-gt32_n32_forward_half_conjugated_asm

	.section .text.gt32_n32_forward_half_conjugated_branch_at_time_asm,"ax",@progbits
	.p2align 6
	.globl gt32_n32_forward_half_conjugated_branch_at_time_asm
	.type gt32_n32_forward_half_conjugated_branch_at_time_asm,@function
gt32_n32_forward_half_conjugated_branch_at_time_asm:
	movq %rsp, %rdx
	movq %rdi, %r11
	andq $-64, %rsp
	subq $1664, %rsp
	N32_CONJ_WAVE_BRANCH_AT_TIME 0,0,0,9,18,3,12,21,6,15
	N32_CONJ_WAVE_BRANCH_AT_TIME 512,1,8,17,2,11,20,5,14,23
	N32_CONJ_WAVE_BRANCH_AT_TIME 1024,2,16,1,10,19,4,13,22,7
	vmovdqa .Ln32_fwd_q(%rip), %ymm15
	movq %rsp, %rsi
	movq %r11, %rdi
	N32_CONJ_SUFFIX_BRANCH 0
	leaq 256(%rsp), %rsi
	leaq 768(%r11), %rdi
	N32_CONJ_SUFFIX_BRANCH 1
	movq %rdx, %rsp
	vzeroupper
	ret
	.size gt32_n32_forward_half_conjugated_branch_at_time_asm,.-gt32_n32_forward_half_conjugated_branch_at_time_asm

	/* Benchmark-only suffix probes.  Input is the 48-vector post-S3 scratch
	 * layout used internally by the complete conjugated Forward. */
	.section .text.gt32_n32_suffix_serial_asm,"ax",@progbits
	.p2align 5
	.globl gt32_n32_suffix_serial_asm
	.type gt32_n32_suffix_serial_asm,@function
gt32_n32_suffix_serial_asm:
	vmovdqa .Ln32_fwd_q(%rip), %ymm15
	N32_CONJ_SUFFIX_BRANCH 0
	N32_CONJ_SUFFIX_BRANCH 1
	vzeroupper
	ret
	.size gt32_n32_suffix_serial_asm,.-gt32_n32_suffix_serial_asm

	.section .text.gt32_n32_suffix_3way_asm,"ax",@progbits
	.p2align 5
	.globl gt32_n32_suffix_3way_asm
	.type gt32_n32_suffix_3way_asm,@function
gt32_n32_suffix_3way_asm:
	vmovdqa .Ln32_fwd_q(%rip), %ymm15
	N32_CONJ_SUFFIX_BRANCH_3WAY 0
	N32_CONJ_SUFFIX_BRANCH_3WAY 1
	vzeroupper
	ret
	.size gt32_n32_suffix_3way_asm,.-gt32_n32_suffix_3way_asm

	.section .text.gt32_n32_suffix_dft_dual_asm,"ax",@progbits
	.p2align 5
	.globl gt32_n32_suffix_dft_dual_asm
	.type gt32_n32_suffix_dft_dual_asm,@function
gt32_n32_suffix_dft_dual_asm:
	vmovdqa .Ln32_fwd_q(%rip), %ymm15
	N32_CONJ_SUFFIX_BRANCH_DFT_DUAL 0
	N32_CONJ_SUFFIX_BRANCH_DFT_DUAL 1
	vzeroupper
	ret
	.size gt32_n32_suffix_dft_dual_asm,.-gt32_n32_suffix_dft_dual_asm

	.section .text.gt32_n32_suffix_mlkstyle_asm,"ax",@progbits
	.p2align 5
	.globl gt32_n32_suffix_mlkstyle_asm
	.type gt32_n32_suffix_mlkstyle_asm,@function
gt32_n32_suffix_mlkstyle_asm:
	vmovdqa .Ln32_fwd_q(%rip), %ymm15
	N32_CONJ_SUFFIX_BRANCH_MLKSTYLE 0
	N32_CONJ_SUFFIX_BRANCH_MLKSTYLE 1
	vzeroupper
	ret
	.size gt32_n32_suffix_mlkstyle_asm,.-gt32_n32_suffix_mlkstyle_asm

	.section .rodata
#include "../generated/tile4_n32_forward_constants.inc"

	.section .note.GNU-stack,"",@progbits
