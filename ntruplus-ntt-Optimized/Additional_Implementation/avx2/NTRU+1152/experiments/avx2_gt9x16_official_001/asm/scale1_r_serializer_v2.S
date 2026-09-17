/* Generated scale-1 serializer V2; preserve the materialized wire boundary. */
.text
.p2align 5
.globl ntruplus1152_exp001_scale1_r_serializer_v2
.type ntruplus1152_exp001_scale1_r_serializer_v2,@function
ntruplus1152_exp001_scale1_r_serializer_v2:
vmovdqa _16xv(%rip), %ymm15
vmovdqa _16xq(%rip), %ymm14
/* packet 0: coefficients 0..127 */
vmovdqa 640(%rsi), %ymm0
vmovdqa 512(%rsi), %ymm1
vpshufb .Lserializer_v2_even_odd(%rip), %ymm0, %ymm0
vpshufb .Lserializer_v2_even_odd(%rip), %ymm1, %ymm1
vpermq $0xd8, %ymm0, %ymm0
vpermq $0xd8, %ymm1, %ymm1
vperm2i128 $0x20, %ymm1, %ymm0, %ymm8
vperm2i128 $0x31, %ymm1, %ymm0, %ymm12
vmovdqa 672(%rsi), %ymm0
vmovdqa 544(%rsi), %ymm1
vpshufb .Lserializer_v2_even_odd(%rip), %ymm0, %ymm0
vpshufb .Lserializer_v2_even_odd(%rip), %ymm1, %ymm1
vpermq $0xd8, %ymm0, %ymm0
vpermq $0xd8, %ymm1, %ymm1
vperm2i128 $0x20, %ymm1, %ymm0, %ymm9
vperm2i128 $0x31, %ymm1, %ymm0, %ymm6
vmovdqa 704(%rsi), %ymm0
vmovdqa 576(%rsi), %ymm1
vpshufb .Lserializer_v2_even_odd(%rip), %ymm0, %ymm0
vpshufb .Lserializer_v2_even_odd(%rip), %ymm1, %ymm1
vpermq $0xd8, %ymm0, %ymm0
vpermq $0xd8, %ymm1, %ymm1
vperm2i128 $0x20, %ymm1, %ymm0, %ymm10
vperm2i128 $0x31, %ymm1, %ymm0, %ymm13
vmovdqa 736(%rsi), %ymm0
vmovdqa 608(%rsi), %ymm1
vpshufb .Lserializer_v2_even_odd(%rip), %ymm0, %ymm0
vpshufb .Lserializer_v2_even_odd(%rip), %ymm1, %ymm1
vpermq $0xd8, %ymm0, %ymm0
vpermq $0xd8, %ymm1, %ymm1
vperm2i128 $0x20, %ymm1, %ymm0, %ymm11
vperm2i128 $0x31, %ymm1, %ymm0, %ymm7
vpmulhrsw %ymm15, %ymm8, %ymm2
vpmulhrsw %ymm15, %ymm9, %ymm3
vpmulhrsw %ymm15, %ymm10, %ymm4
vpmulhrsw %ymm15, %ymm11, %ymm5
vpmullw %ymm14, %ymm2, %ymm2
vpmullw %ymm14, %ymm3, %ymm3
vpmullw %ymm14, %ymm4, %ymm4
vpmullw %ymm14, %ymm5, %ymm5
vpsubw %ymm2, %ymm8,  %ymm8
vpsubw %ymm3, %ymm9,  %ymm9
vpsubw %ymm4, %ymm10,  %ymm10
vpsubw %ymm5, %ymm11,  %ymm11

vpmulhrsw %ymm15, %ymm12, %ymm2
vpmulhrsw %ymm15, %ymm6, %ymm3
vpmulhrsw %ymm15, %ymm13, %ymm4
vpmulhrsw %ymm15, %ymm7, %ymm5
vpmullw %ymm14, %ymm2, %ymm2
vpmullw %ymm14, %ymm3, %ymm3
vpmullw %ymm14, %ymm4, %ymm4
vpmullw %ymm14, %ymm5, %ymm5
vpsubw %ymm2, %ymm12,  %ymm12
vpsubw %ymm3, %ymm6,  %ymm6
vpsubw %ymm4, %ymm13,  %ymm13
vpsubw %ymm5, %ymm7, %ymm7

vpsraw $15,    %ymm8,  %ymm2
vpsraw $15,    %ymm9,  %ymm3
vpsraw $15,    %ymm10,  %ymm4
vpsraw $15,    %ymm11,  %ymm5
vpand  %ymm14,  %ymm2, %ymm2
vpand  %ymm14,  %ymm3, %ymm3
vpand  %ymm14,  %ymm4, %ymm4
vpand  %ymm14,  %ymm5, %ymm5
vpaddw %ymm2, %ymm8,  %ymm8
vpaddw %ymm3, %ymm9,  %ymm9
vpaddw %ymm4, %ymm10,  %ymm10
vpaddw %ymm5, %ymm11,  %ymm11

vpsraw $15,    %ymm12,  %ymm2
vpsraw $15,    %ymm6,  %ymm3
vpsraw $15,    %ymm13,  %ymm4
vpsraw $15,    %ymm7, %ymm5
vpand  %ymm14,  %ymm2, %ymm2
vpand  %ymm14,  %ymm3, %ymm3
vpand  %ymm14,  %ymm4, %ymm4
vpand  %ymm14,  %ymm5, %ymm5
vpaddw %ymm2, %ymm12,  %ymm12
vpaddw %ymm3, %ymm6,  %ymm6
vpaddw %ymm4, %ymm13,  %ymm13
vpaddw %ymm5, %ymm7, %ymm7

vpsllw $12,    %ymm9,  %ymm2
vpsllw $12,    %ymm6,  %ymm3
vpxor  %ymm2, %ymm8,  %ymm8
vpxor  %ymm3, %ymm12,  %ymm12
vpsllw $8,     %ymm10,  %ymm2
vpsllw $8,     %ymm13,  %ymm3
vpsrlw $4,     %ymm9,  %ymm4
vpsrlw $4,     %ymm6,  %ymm5
vpxor  %ymm2, %ymm4, %ymm9
vpxor  %ymm3, %ymm5, %ymm6
vpsllw $4,     %ymm11,  %ymm2
vpsllw $4,     %ymm7, %ymm3
vpsrlw $8,     %ymm10,  %ymm4
vpsrlw $8,     %ymm13,  %ymm5
vpxor  %ymm2, %ymm4, %ymm10
vpxor  %ymm3, %ymm5, %ymm13

#shuffle
vpslld      $16, %ymm9, %ymm7
vpslld      $16, %ymm12, %ymm0
vpslld      $16, %ymm13, %ymm1
vpblendw    $0xAA, %ymm7, %ymm8, %ymm7
vpblendw    $0xAA, %ymm0, %ymm10, %ymm0
vpblendw    $0xAA, %ymm1, %ymm6, %ymm1

vpsrlq      $16,   %ymm8, %ymm2
vpsrlq      $16,   %ymm10, %ymm3
vpsrlq      $16,   %ymm6, %ymm4
vpblendw    $0xAA, %ymm9, %ymm2, %ymm2
vpblendw    $0xAA, %ymm12, %ymm3, %ymm3
vpblendw    $0xAA, %ymm13, %ymm4, %ymm4

vpsllq      $32,   %ymm0,  %ymm8
vpsllq      $32,   %ymm2, %ymm9
vpsllq      $32,   %ymm4, %ymm10
vpblendd    $0xAA, %ymm8,  %ymm7,  %ymm8
vpblendd    $0xAA, %ymm9,  %ymm1,  %ymm9
vpblendd    $0xAA, %ymm10,  %ymm3, %ymm10

vpsrlq      $32,   %ymm7,  %ymm11
vpsrlq      $32,   %ymm1,  %ymm12
vpsrlq      $32,   %ymm3, %ymm6
vpblendd    $0xAA, %ymm0,  %ymm11, %ymm11
vpblendd    $0xAA, %ymm2, %ymm12, %ymm12
vpblendd    $0xAA, %ymm4, %ymm6, %ymm6

vpunpcklqdq %ymm9, %ymm8, %ymm13
vpunpcklqdq %ymm11, %ymm10, %ymm7
vpunpcklqdq %ymm6, %ymm12, %ymm0
vpunpckhqdq %ymm9, %ymm8, %ymm1
vpunpckhqdq %ymm11, %ymm10, %ymm2
vpunpckhqdq %ymm6, %ymm12, %ymm3

vperm2i128  $0x20, %ymm7,  %ymm13,  %ymm8
vperm2i128  $0x20, %ymm1,  %ymm0,  %ymm9
vperm2i128  $0x20, %ymm3, %ymm2, %ymm10
vperm2i128  $0x31, %ymm7,  %ymm13,  %ymm11
vperm2i128  $0x31, %ymm1,  %ymm0,  %ymm12
vperm2i128  $0x31, %ymm3, %ymm2, %ymm6

vmovdqu %ymm8,    (%rdi)
vmovdqu %ymm9,  32(%rdi)
vmovdqu %ymm10,  64(%rdi)
vmovdqu %ymm11,  96(%rdi)
vmovdqu %ymm12, 128(%rdi)
vmovdqu %ymm6, 160(%rdi)
add $192, %rdi
/* packet 1: coefficients 128..255 */
vmovdqa 384(%rsi), %ymm0
vmovdqa 0(%rsi), %ymm1
vpshufb .Lserializer_v2_even_odd(%rip), %ymm0, %ymm0
vpshufb .Lserializer_v2_even_odd(%rip), %ymm1, %ymm1
vpermq $0xd8, %ymm0, %ymm0
vpermq $0xd8, %ymm1, %ymm1
vperm2i128 $0x20, %ymm1, %ymm0, %ymm8
vperm2i128 $0x31, %ymm1, %ymm0, %ymm12
vmovdqa 416(%rsi), %ymm0
vmovdqa 32(%rsi), %ymm1
vpshufb .Lserializer_v2_even_odd(%rip), %ymm0, %ymm0
vpshufb .Lserializer_v2_even_odd(%rip), %ymm1, %ymm1
vpermq $0xd8, %ymm0, %ymm0
vpermq $0xd8, %ymm1, %ymm1
vperm2i128 $0x20, %ymm1, %ymm0, %ymm9
vperm2i128 $0x31, %ymm1, %ymm0, %ymm6
vmovdqa 448(%rsi), %ymm0
vmovdqa 64(%rsi), %ymm1
vpshufb .Lserializer_v2_even_odd(%rip), %ymm0, %ymm0
vpshufb .Lserializer_v2_even_odd(%rip), %ymm1, %ymm1
vpermq $0xd8, %ymm0, %ymm0
vpermq $0xd8, %ymm1, %ymm1
vperm2i128 $0x20, %ymm1, %ymm0, %ymm10
vperm2i128 $0x31, %ymm1, %ymm0, %ymm13
vmovdqa 480(%rsi), %ymm0
vmovdqa 96(%rsi), %ymm1
vpshufb .Lserializer_v2_even_odd(%rip), %ymm0, %ymm0
vpshufb .Lserializer_v2_even_odd(%rip), %ymm1, %ymm1
vpermq $0xd8, %ymm0, %ymm0
vpermq $0xd8, %ymm1, %ymm1
vperm2i128 $0x20, %ymm1, %ymm0, %ymm11
vperm2i128 $0x31, %ymm1, %ymm0, %ymm7
vpmulhrsw %ymm15, %ymm8, %ymm2
vpmulhrsw %ymm15, %ymm9, %ymm3
vpmulhrsw %ymm15, %ymm10, %ymm4
vpmulhrsw %ymm15, %ymm11, %ymm5
vpmullw %ymm14, %ymm2, %ymm2
vpmullw %ymm14, %ymm3, %ymm3
vpmullw %ymm14, %ymm4, %ymm4
vpmullw %ymm14, %ymm5, %ymm5
vpsubw %ymm2, %ymm8,  %ymm8
vpsubw %ymm3, %ymm9,  %ymm9
vpsubw %ymm4, %ymm10,  %ymm10
vpsubw %ymm5, %ymm11,  %ymm11

vpmulhrsw %ymm15, %ymm12, %ymm2
vpmulhrsw %ymm15, %ymm6, %ymm3
vpmulhrsw %ymm15, %ymm13, %ymm4
vpmulhrsw %ymm15, %ymm7, %ymm5
vpmullw %ymm14, %ymm2, %ymm2
vpmullw %ymm14, %ymm3, %ymm3
vpmullw %ymm14, %ymm4, %ymm4
vpmullw %ymm14, %ymm5, %ymm5
vpsubw %ymm2, %ymm12,  %ymm12
vpsubw %ymm3, %ymm6,  %ymm6
vpsubw %ymm4, %ymm13,  %ymm13
vpsubw %ymm5, %ymm7, %ymm7

vpsraw $15,    %ymm8,  %ymm2
vpsraw $15,    %ymm9,  %ymm3
vpsraw $15,    %ymm10,  %ymm4
vpsraw $15,    %ymm11,  %ymm5
vpand  %ymm14,  %ymm2, %ymm2
vpand  %ymm14,  %ymm3, %ymm3
vpand  %ymm14,  %ymm4, %ymm4
vpand  %ymm14,  %ymm5, %ymm5
vpaddw %ymm2, %ymm8,  %ymm8
vpaddw %ymm3, %ymm9,  %ymm9
vpaddw %ymm4, %ymm10,  %ymm10
vpaddw %ymm5, %ymm11,  %ymm11

vpsraw $15,    %ymm12,  %ymm2
vpsraw $15,    %ymm6,  %ymm3
vpsraw $15,    %ymm13,  %ymm4
vpsraw $15,    %ymm7, %ymm5
vpand  %ymm14,  %ymm2, %ymm2
vpand  %ymm14,  %ymm3, %ymm3
vpand  %ymm14,  %ymm4, %ymm4
vpand  %ymm14,  %ymm5, %ymm5
vpaddw %ymm2, %ymm12,  %ymm12
vpaddw %ymm3, %ymm6,  %ymm6
vpaddw %ymm4, %ymm13,  %ymm13
vpaddw %ymm5, %ymm7, %ymm7

vpsllw $12,    %ymm9,  %ymm2
vpsllw $12,    %ymm6,  %ymm3
vpxor  %ymm2, %ymm8,  %ymm8
vpxor  %ymm3, %ymm12,  %ymm12
vpsllw $8,     %ymm10,  %ymm2
vpsllw $8,     %ymm13,  %ymm3
vpsrlw $4,     %ymm9,  %ymm4
vpsrlw $4,     %ymm6,  %ymm5
vpxor  %ymm2, %ymm4, %ymm9
vpxor  %ymm3, %ymm5, %ymm6
vpsllw $4,     %ymm11,  %ymm2
vpsllw $4,     %ymm7, %ymm3
vpsrlw $8,     %ymm10,  %ymm4
vpsrlw $8,     %ymm13,  %ymm5
vpxor  %ymm2, %ymm4, %ymm10
vpxor  %ymm3, %ymm5, %ymm13

#shuffle
vpslld      $16, %ymm9, %ymm7
vpslld      $16, %ymm12, %ymm0
vpslld      $16, %ymm13, %ymm1
vpblendw    $0xAA, %ymm7, %ymm8, %ymm7
vpblendw    $0xAA, %ymm0, %ymm10, %ymm0
vpblendw    $0xAA, %ymm1, %ymm6, %ymm1

vpsrlq      $16,   %ymm8, %ymm2
vpsrlq      $16,   %ymm10, %ymm3
vpsrlq      $16,   %ymm6, %ymm4
vpblendw    $0xAA, %ymm9, %ymm2, %ymm2
vpblendw    $0xAA, %ymm12, %ymm3, %ymm3
vpblendw    $0xAA, %ymm13, %ymm4, %ymm4

vpsllq      $32,   %ymm0,  %ymm8
vpsllq      $32,   %ymm2, %ymm9
vpsllq      $32,   %ymm4, %ymm10
vpblendd    $0xAA, %ymm8,  %ymm7,  %ymm8
vpblendd    $0xAA, %ymm9,  %ymm1,  %ymm9
vpblendd    $0xAA, %ymm10,  %ymm3, %ymm10

vpsrlq      $32,   %ymm7,  %ymm11
vpsrlq      $32,   %ymm1,  %ymm12
vpsrlq      $32,   %ymm3, %ymm6
vpblendd    $0xAA, %ymm0,  %ymm11, %ymm11
vpblendd    $0xAA, %ymm2, %ymm12, %ymm12
vpblendd    $0xAA, %ymm4, %ymm6, %ymm6

vpunpcklqdq %ymm9, %ymm8, %ymm13
vpunpcklqdq %ymm11, %ymm10, %ymm7
vpunpcklqdq %ymm6, %ymm12, %ymm0
vpunpckhqdq %ymm9, %ymm8, %ymm1
vpunpckhqdq %ymm11, %ymm10, %ymm2
vpunpckhqdq %ymm6, %ymm12, %ymm3

vperm2i128  $0x20, %ymm7,  %ymm13,  %ymm8
vperm2i128  $0x20, %ymm1,  %ymm0,  %ymm9
vperm2i128  $0x20, %ymm3, %ymm2, %ymm10
vperm2i128  $0x31, %ymm7,  %ymm13,  %ymm11
vperm2i128  $0x31, %ymm1,  %ymm0,  %ymm12
vperm2i128  $0x31, %ymm3, %ymm2, %ymm6

vmovdqu %ymm8,    (%rdi)
vmovdqu %ymm9,  32(%rdi)
vmovdqu %ymm10,  64(%rdi)
vmovdqu %ymm11,  96(%rdi)
vmovdqu %ymm12, 128(%rdi)
vmovdqu %ymm6, 160(%rdi)
add $192, %rdi
/* packet 2: coefficients 256..383 */
vmovdqa 256(%rsi), %ymm0
vmovdqa 128(%rsi), %ymm1
vpshufb .Lserializer_v2_even_odd(%rip), %ymm0, %ymm0
vpshufb .Lserializer_v2_even_odd(%rip), %ymm1, %ymm1
vpermq $0xd8, %ymm0, %ymm0
vpermq $0xd8, %ymm1, %ymm1
vperm2i128 $0x20, %ymm1, %ymm0, %ymm8
vperm2i128 $0x31, %ymm1, %ymm0, %ymm12
vmovdqa 288(%rsi), %ymm0
vmovdqa 160(%rsi), %ymm1
vpshufb .Lserializer_v2_even_odd(%rip), %ymm0, %ymm0
vpshufb .Lserializer_v2_even_odd(%rip), %ymm1, %ymm1
vpermq $0xd8, %ymm0, %ymm0
vpermq $0xd8, %ymm1, %ymm1
vperm2i128 $0x20, %ymm1, %ymm0, %ymm9
vperm2i128 $0x31, %ymm1, %ymm0, %ymm6
vmovdqa 320(%rsi), %ymm0
vmovdqa 192(%rsi), %ymm1
vpshufb .Lserializer_v2_even_odd(%rip), %ymm0, %ymm0
vpshufb .Lserializer_v2_even_odd(%rip), %ymm1, %ymm1
vpermq $0xd8, %ymm0, %ymm0
vpermq $0xd8, %ymm1, %ymm1
vperm2i128 $0x20, %ymm1, %ymm0, %ymm10
vperm2i128 $0x31, %ymm1, %ymm0, %ymm13
vmovdqa 352(%rsi), %ymm0
vmovdqa 224(%rsi), %ymm1
vpshufb .Lserializer_v2_even_odd(%rip), %ymm0, %ymm0
vpshufb .Lserializer_v2_even_odd(%rip), %ymm1, %ymm1
vpermq $0xd8, %ymm0, %ymm0
vpermq $0xd8, %ymm1, %ymm1
vperm2i128 $0x20, %ymm1, %ymm0, %ymm11
vperm2i128 $0x31, %ymm1, %ymm0, %ymm7
vpmulhrsw %ymm15, %ymm8, %ymm2
vpmulhrsw %ymm15, %ymm9, %ymm3
vpmulhrsw %ymm15, %ymm10, %ymm4
vpmulhrsw %ymm15, %ymm11, %ymm5
vpmullw %ymm14, %ymm2, %ymm2
vpmullw %ymm14, %ymm3, %ymm3
vpmullw %ymm14, %ymm4, %ymm4
vpmullw %ymm14, %ymm5, %ymm5
vpsubw %ymm2, %ymm8,  %ymm8
vpsubw %ymm3, %ymm9,  %ymm9
vpsubw %ymm4, %ymm10,  %ymm10
vpsubw %ymm5, %ymm11,  %ymm11

vpmulhrsw %ymm15, %ymm12, %ymm2
vpmulhrsw %ymm15, %ymm6, %ymm3
vpmulhrsw %ymm15, %ymm13, %ymm4
vpmulhrsw %ymm15, %ymm7, %ymm5
vpmullw %ymm14, %ymm2, %ymm2
vpmullw %ymm14, %ymm3, %ymm3
vpmullw %ymm14, %ymm4, %ymm4
vpmullw %ymm14, %ymm5, %ymm5
vpsubw %ymm2, %ymm12,  %ymm12
vpsubw %ymm3, %ymm6,  %ymm6
vpsubw %ymm4, %ymm13,  %ymm13
vpsubw %ymm5, %ymm7, %ymm7

vpsraw $15,    %ymm8,  %ymm2
vpsraw $15,    %ymm9,  %ymm3
vpsraw $15,    %ymm10,  %ymm4
vpsraw $15,    %ymm11,  %ymm5
vpand  %ymm14,  %ymm2, %ymm2
vpand  %ymm14,  %ymm3, %ymm3
vpand  %ymm14,  %ymm4, %ymm4
vpand  %ymm14,  %ymm5, %ymm5
vpaddw %ymm2, %ymm8,  %ymm8
vpaddw %ymm3, %ymm9,  %ymm9
vpaddw %ymm4, %ymm10,  %ymm10
vpaddw %ymm5, %ymm11,  %ymm11

vpsraw $15,    %ymm12,  %ymm2
vpsraw $15,    %ymm6,  %ymm3
vpsraw $15,    %ymm13,  %ymm4
vpsraw $15,    %ymm7, %ymm5
vpand  %ymm14,  %ymm2, %ymm2
vpand  %ymm14,  %ymm3, %ymm3
vpand  %ymm14,  %ymm4, %ymm4
vpand  %ymm14,  %ymm5, %ymm5
vpaddw %ymm2, %ymm12,  %ymm12
vpaddw %ymm3, %ymm6,  %ymm6
vpaddw %ymm4, %ymm13,  %ymm13
vpaddw %ymm5, %ymm7, %ymm7

vpsllw $12,    %ymm9,  %ymm2
vpsllw $12,    %ymm6,  %ymm3
vpxor  %ymm2, %ymm8,  %ymm8
vpxor  %ymm3, %ymm12,  %ymm12
vpsllw $8,     %ymm10,  %ymm2
vpsllw $8,     %ymm13,  %ymm3
vpsrlw $4,     %ymm9,  %ymm4
vpsrlw $4,     %ymm6,  %ymm5
vpxor  %ymm2, %ymm4, %ymm9
vpxor  %ymm3, %ymm5, %ymm6
vpsllw $4,     %ymm11,  %ymm2
vpsllw $4,     %ymm7, %ymm3
vpsrlw $8,     %ymm10,  %ymm4
vpsrlw $8,     %ymm13,  %ymm5
vpxor  %ymm2, %ymm4, %ymm10
vpxor  %ymm3, %ymm5, %ymm13

#shuffle
vpslld      $16, %ymm9, %ymm7
vpslld      $16, %ymm12, %ymm0
vpslld      $16, %ymm13, %ymm1
vpblendw    $0xAA, %ymm7, %ymm8, %ymm7
vpblendw    $0xAA, %ymm0, %ymm10, %ymm0
vpblendw    $0xAA, %ymm1, %ymm6, %ymm1

vpsrlq      $16,   %ymm8, %ymm2
vpsrlq      $16,   %ymm10, %ymm3
vpsrlq      $16,   %ymm6, %ymm4
vpblendw    $0xAA, %ymm9, %ymm2, %ymm2
vpblendw    $0xAA, %ymm12, %ymm3, %ymm3
vpblendw    $0xAA, %ymm13, %ymm4, %ymm4

vpsllq      $32,   %ymm0,  %ymm8
vpsllq      $32,   %ymm2, %ymm9
vpsllq      $32,   %ymm4, %ymm10
vpblendd    $0xAA, %ymm8,  %ymm7,  %ymm8
vpblendd    $0xAA, %ymm9,  %ymm1,  %ymm9
vpblendd    $0xAA, %ymm10,  %ymm3, %ymm10

vpsrlq      $32,   %ymm7,  %ymm11
vpsrlq      $32,   %ymm1,  %ymm12
vpsrlq      $32,   %ymm3, %ymm6
vpblendd    $0xAA, %ymm0,  %ymm11, %ymm11
vpblendd    $0xAA, %ymm2, %ymm12, %ymm12
vpblendd    $0xAA, %ymm4, %ymm6, %ymm6

vpunpcklqdq %ymm9, %ymm8, %ymm13
vpunpcklqdq %ymm11, %ymm10, %ymm7
vpunpcklqdq %ymm6, %ymm12, %ymm0
vpunpckhqdq %ymm9, %ymm8, %ymm1
vpunpckhqdq %ymm11, %ymm10, %ymm2
vpunpckhqdq %ymm6, %ymm12, %ymm3

vperm2i128  $0x20, %ymm7,  %ymm13,  %ymm8
vperm2i128  $0x20, %ymm1,  %ymm0,  %ymm9
vperm2i128  $0x20, %ymm3, %ymm2, %ymm10
vperm2i128  $0x31, %ymm7,  %ymm13,  %ymm11
vperm2i128  $0x31, %ymm1,  %ymm0,  %ymm12
vperm2i128  $0x31, %ymm3, %ymm2, %ymm6

vmovdqu %ymm8,    (%rdi)
vmovdqu %ymm9,  32(%rdi)
vmovdqu %ymm10,  64(%rdi)
vmovdqu %ymm11,  96(%rdi)
vmovdqu %ymm12, 128(%rdi)
vmovdqu %ymm6, 160(%rdi)
add $192, %rdi
/* packet 3: coefficients 384..511 */
vmovdqa 896(%rsi), %ymm0
vmovdqa 768(%rsi), %ymm1
vpshufb .Lserializer_v2_even_odd(%rip), %ymm0, %ymm0
vpshufb .Lserializer_v2_even_odd(%rip), %ymm1, %ymm1
vpermq $0xd8, %ymm0, %ymm0
vpermq $0xd8, %ymm1, %ymm1
vperm2i128 $0x20, %ymm1, %ymm0, %ymm8
vperm2i128 $0x31, %ymm1, %ymm0, %ymm12
vmovdqa 928(%rsi), %ymm0
vmovdqa 800(%rsi), %ymm1
vpshufb .Lserializer_v2_even_odd(%rip), %ymm0, %ymm0
vpshufb .Lserializer_v2_even_odd(%rip), %ymm1, %ymm1
vpermq $0xd8, %ymm0, %ymm0
vpermq $0xd8, %ymm1, %ymm1
vperm2i128 $0x20, %ymm1, %ymm0, %ymm9
vperm2i128 $0x31, %ymm1, %ymm0, %ymm6
vmovdqa 960(%rsi), %ymm0
vmovdqa 832(%rsi), %ymm1
vpshufb .Lserializer_v2_even_odd(%rip), %ymm0, %ymm0
vpshufb .Lserializer_v2_even_odd(%rip), %ymm1, %ymm1
vpermq $0xd8, %ymm0, %ymm0
vpermq $0xd8, %ymm1, %ymm1
vperm2i128 $0x20, %ymm1, %ymm0, %ymm10
vperm2i128 $0x31, %ymm1, %ymm0, %ymm13
vmovdqa 992(%rsi), %ymm0
vmovdqa 864(%rsi), %ymm1
vpshufb .Lserializer_v2_even_odd(%rip), %ymm0, %ymm0
vpshufb .Lserializer_v2_even_odd(%rip), %ymm1, %ymm1
vpermq $0xd8, %ymm0, %ymm0
vpermq $0xd8, %ymm1, %ymm1
vperm2i128 $0x20, %ymm1, %ymm0, %ymm11
vperm2i128 $0x31, %ymm1, %ymm0, %ymm7
vpmulhrsw %ymm15, %ymm8, %ymm2
vpmulhrsw %ymm15, %ymm9, %ymm3
vpmulhrsw %ymm15, %ymm10, %ymm4
vpmulhrsw %ymm15, %ymm11, %ymm5
vpmullw %ymm14, %ymm2, %ymm2
vpmullw %ymm14, %ymm3, %ymm3
vpmullw %ymm14, %ymm4, %ymm4
vpmullw %ymm14, %ymm5, %ymm5
vpsubw %ymm2, %ymm8,  %ymm8
vpsubw %ymm3, %ymm9,  %ymm9
vpsubw %ymm4, %ymm10,  %ymm10
vpsubw %ymm5, %ymm11,  %ymm11

vpmulhrsw %ymm15, %ymm12, %ymm2
vpmulhrsw %ymm15, %ymm6, %ymm3
vpmulhrsw %ymm15, %ymm13, %ymm4
vpmulhrsw %ymm15, %ymm7, %ymm5
vpmullw %ymm14, %ymm2, %ymm2
vpmullw %ymm14, %ymm3, %ymm3
vpmullw %ymm14, %ymm4, %ymm4
vpmullw %ymm14, %ymm5, %ymm5
vpsubw %ymm2, %ymm12,  %ymm12
vpsubw %ymm3, %ymm6,  %ymm6
vpsubw %ymm4, %ymm13,  %ymm13
vpsubw %ymm5, %ymm7, %ymm7

vpsraw $15,    %ymm8,  %ymm2
vpsraw $15,    %ymm9,  %ymm3
vpsraw $15,    %ymm10,  %ymm4
vpsraw $15,    %ymm11,  %ymm5
vpand  %ymm14,  %ymm2, %ymm2
vpand  %ymm14,  %ymm3, %ymm3
vpand  %ymm14,  %ymm4, %ymm4
vpand  %ymm14,  %ymm5, %ymm5
vpaddw %ymm2, %ymm8,  %ymm8
vpaddw %ymm3, %ymm9,  %ymm9
vpaddw %ymm4, %ymm10,  %ymm10
vpaddw %ymm5, %ymm11,  %ymm11

vpsraw $15,    %ymm12,  %ymm2
vpsraw $15,    %ymm6,  %ymm3
vpsraw $15,    %ymm13,  %ymm4
vpsraw $15,    %ymm7, %ymm5
vpand  %ymm14,  %ymm2, %ymm2
vpand  %ymm14,  %ymm3, %ymm3
vpand  %ymm14,  %ymm4, %ymm4
vpand  %ymm14,  %ymm5, %ymm5
vpaddw %ymm2, %ymm12,  %ymm12
vpaddw %ymm3, %ymm6,  %ymm6
vpaddw %ymm4, %ymm13,  %ymm13
vpaddw %ymm5, %ymm7, %ymm7

vpsllw $12,    %ymm9,  %ymm2
vpsllw $12,    %ymm6,  %ymm3
vpxor  %ymm2, %ymm8,  %ymm8
vpxor  %ymm3, %ymm12,  %ymm12
vpsllw $8,     %ymm10,  %ymm2
vpsllw $8,     %ymm13,  %ymm3
vpsrlw $4,     %ymm9,  %ymm4
vpsrlw $4,     %ymm6,  %ymm5
vpxor  %ymm2, %ymm4, %ymm9
vpxor  %ymm3, %ymm5, %ymm6
vpsllw $4,     %ymm11,  %ymm2
vpsllw $4,     %ymm7, %ymm3
vpsrlw $8,     %ymm10,  %ymm4
vpsrlw $8,     %ymm13,  %ymm5
vpxor  %ymm2, %ymm4, %ymm10
vpxor  %ymm3, %ymm5, %ymm13

#shuffle
vpslld      $16, %ymm9, %ymm7
vpslld      $16, %ymm12, %ymm0
vpslld      $16, %ymm13, %ymm1
vpblendw    $0xAA, %ymm7, %ymm8, %ymm7
vpblendw    $0xAA, %ymm0, %ymm10, %ymm0
vpblendw    $0xAA, %ymm1, %ymm6, %ymm1

vpsrlq      $16,   %ymm8, %ymm2
vpsrlq      $16,   %ymm10, %ymm3
vpsrlq      $16,   %ymm6, %ymm4
vpblendw    $0xAA, %ymm9, %ymm2, %ymm2
vpblendw    $0xAA, %ymm12, %ymm3, %ymm3
vpblendw    $0xAA, %ymm13, %ymm4, %ymm4

vpsllq      $32,   %ymm0,  %ymm8
vpsllq      $32,   %ymm2, %ymm9
vpsllq      $32,   %ymm4, %ymm10
vpblendd    $0xAA, %ymm8,  %ymm7,  %ymm8
vpblendd    $0xAA, %ymm9,  %ymm1,  %ymm9
vpblendd    $0xAA, %ymm10,  %ymm3, %ymm10

vpsrlq      $32,   %ymm7,  %ymm11
vpsrlq      $32,   %ymm1,  %ymm12
vpsrlq      $32,   %ymm3, %ymm6
vpblendd    $0xAA, %ymm0,  %ymm11, %ymm11
vpblendd    $0xAA, %ymm2, %ymm12, %ymm12
vpblendd    $0xAA, %ymm4, %ymm6, %ymm6

vpunpcklqdq %ymm9, %ymm8, %ymm13
vpunpcklqdq %ymm11, %ymm10, %ymm7
vpunpcklqdq %ymm6, %ymm12, %ymm0
vpunpckhqdq %ymm9, %ymm8, %ymm1
vpunpckhqdq %ymm11, %ymm10, %ymm2
vpunpckhqdq %ymm6, %ymm12, %ymm3

vperm2i128  $0x20, %ymm7,  %ymm13,  %ymm8
vperm2i128  $0x20, %ymm1,  %ymm0,  %ymm9
vperm2i128  $0x20, %ymm3, %ymm2, %ymm10
vperm2i128  $0x31, %ymm7,  %ymm13,  %ymm11
vperm2i128  $0x31, %ymm1,  %ymm0,  %ymm12
vperm2i128  $0x31, %ymm3, %ymm2, %ymm6

vmovdqu %ymm8,    (%rdi)
vmovdqu %ymm9,  32(%rdi)
vmovdqu %ymm10,  64(%rdi)
vmovdqu %ymm11,  96(%rdi)
vmovdqu %ymm12, 128(%rdi)
vmovdqu %ymm6, 160(%rdi)
add $192, %rdi
/* packet 4: coefficients 512..639 */
vmovdqa 1024(%rsi), %ymm0
vmovdqa 1280(%rsi), %ymm1
vpshufb .Lserializer_v2_even_odd(%rip), %ymm0, %ymm0
vpshufb .Lserializer_v2_even_odd(%rip), %ymm1, %ymm1
vpermq $0xd8, %ymm0, %ymm0
vpermq $0xd8, %ymm1, %ymm1
vperm2i128 $0x20, %ymm1, %ymm0, %ymm8
vperm2i128 $0x31, %ymm1, %ymm0, %ymm12
vmovdqa 1056(%rsi), %ymm0
vmovdqa 1312(%rsi), %ymm1
vpshufb .Lserializer_v2_even_odd(%rip), %ymm0, %ymm0
vpshufb .Lserializer_v2_even_odd(%rip), %ymm1, %ymm1
vpermq $0xd8, %ymm0, %ymm0
vpermq $0xd8, %ymm1, %ymm1
vperm2i128 $0x20, %ymm1, %ymm0, %ymm9
vperm2i128 $0x31, %ymm1, %ymm0, %ymm6
vmovdqa 1088(%rsi), %ymm0
vmovdqa 1344(%rsi), %ymm1
vpshufb .Lserializer_v2_even_odd(%rip), %ymm0, %ymm0
vpshufb .Lserializer_v2_even_odd(%rip), %ymm1, %ymm1
vpermq $0xd8, %ymm0, %ymm0
vpermq $0xd8, %ymm1, %ymm1
vperm2i128 $0x20, %ymm1, %ymm0, %ymm10
vperm2i128 $0x31, %ymm1, %ymm0, %ymm13
vmovdqa 1120(%rsi), %ymm0
vmovdqa 1376(%rsi), %ymm1
vpshufb .Lserializer_v2_even_odd(%rip), %ymm0, %ymm0
vpshufb .Lserializer_v2_even_odd(%rip), %ymm1, %ymm1
vpermq $0xd8, %ymm0, %ymm0
vpermq $0xd8, %ymm1, %ymm1
vperm2i128 $0x20, %ymm1, %ymm0, %ymm11
vperm2i128 $0x31, %ymm1, %ymm0, %ymm7
vpmulhrsw %ymm15, %ymm8, %ymm2
vpmulhrsw %ymm15, %ymm9, %ymm3
vpmulhrsw %ymm15, %ymm10, %ymm4
vpmulhrsw %ymm15, %ymm11, %ymm5
vpmullw %ymm14, %ymm2, %ymm2
vpmullw %ymm14, %ymm3, %ymm3
vpmullw %ymm14, %ymm4, %ymm4
vpmullw %ymm14, %ymm5, %ymm5
vpsubw %ymm2, %ymm8,  %ymm8
vpsubw %ymm3, %ymm9,  %ymm9
vpsubw %ymm4, %ymm10,  %ymm10
vpsubw %ymm5, %ymm11,  %ymm11

vpmulhrsw %ymm15, %ymm12, %ymm2
vpmulhrsw %ymm15, %ymm6, %ymm3
vpmulhrsw %ymm15, %ymm13, %ymm4
vpmulhrsw %ymm15, %ymm7, %ymm5
vpmullw %ymm14, %ymm2, %ymm2
vpmullw %ymm14, %ymm3, %ymm3
vpmullw %ymm14, %ymm4, %ymm4
vpmullw %ymm14, %ymm5, %ymm5
vpsubw %ymm2, %ymm12,  %ymm12
vpsubw %ymm3, %ymm6,  %ymm6
vpsubw %ymm4, %ymm13,  %ymm13
vpsubw %ymm5, %ymm7, %ymm7

vpsraw $15,    %ymm8,  %ymm2
vpsraw $15,    %ymm9,  %ymm3
vpsraw $15,    %ymm10,  %ymm4
vpsraw $15,    %ymm11,  %ymm5
vpand  %ymm14,  %ymm2, %ymm2
vpand  %ymm14,  %ymm3, %ymm3
vpand  %ymm14,  %ymm4, %ymm4
vpand  %ymm14,  %ymm5, %ymm5
vpaddw %ymm2, %ymm8,  %ymm8
vpaddw %ymm3, %ymm9,  %ymm9
vpaddw %ymm4, %ymm10,  %ymm10
vpaddw %ymm5, %ymm11,  %ymm11

vpsraw $15,    %ymm12,  %ymm2
vpsraw $15,    %ymm6,  %ymm3
vpsraw $15,    %ymm13,  %ymm4
vpsraw $15,    %ymm7, %ymm5
vpand  %ymm14,  %ymm2, %ymm2
vpand  %ymm14,  %ymm3, %ymm3
vpand  %ymm14,  %ymm4, %ymm4
vpand  %ymm14,  %ymm5, %ymm5
vpaddw %ymm2, %ymm12,  %ymm12
vpaddw %ymm3, %ymm6,  %ymm6
vpaddw %ymm4, %ymm13,  %ymm13
vpaddw %ymm5, %ymm7, %ymm7

vpsllw $12,    %ymm9,  %ymm2
vpsllw $12,    %ymm6,  %ymm3
vpxor  %ymm2, %ymm8,  %ymm8
vpxor  %ymm3, %ymm12,  %ymm12
vpsllw $8,     %ymm10,  %ymm2
vpsllw $8,     %ymm13,  %ymm3
vpsrlw $4,     %ymm9,  %ymm4
vpsrlw $4,     %ymm6,  %ymm5
vpxor  %ymm2, %ymm4, %ymm9
vpxor  %ymm3, %ymm5, %ymm6
vpsllw $4,     %ymm11,  %ymm2
vpsllw $4,     %ymm7, %ymm3
vpsrlw $8,     %ymm10,  %ymm4
vpsrlw $8,     %ymm13,  %ymm5
vpxor  %ymm2, %ymm4, %ymm10
vpxor  %ymm3, %ymm5, %ymm13

#shuffle
vpslld      $16, %ymm9, %ymm7
vpslld      $16, %ymm12, %ymm0
vpslld      $16, %ymm13, %ymm1
vpblendw    $0xAA, %ymm7, %ymm8, %ymm7
vpblendw    $0xAA, %ymm0, %ymm10, %ymm0
vpblendw    $0xAA, %ymm1, %ymm6, %ymm1

vpsrlq      $16,   %ymm8, %ymm2
vpsrlq      $16,   %ymm10, %ymm3
vpsrlq      $16,   %ymm6, %ymm4
vpblendw    $0xAA, %ymm9, %ymm2, %ymm2
vpblendw    $0xAA, %ymm12, %ymm3, %ymm3
vpblendw    $0xAA, %ymm13, %ymm4, %ymm4

vpsllq      $32,   %ymm0,  %ymm8
vpsllq      $32,   %ymm2, %ymm9
vpsllq      $32,   %ymm4, %ymm10
vpblendd    $0xAA, %ymm8,  %ymm7,  %ymm8
vpblendd    $0xAA, %ymm9,  %ymm1,  %ymm9
vpblendd    $0xAA, %ymm10,  %ymm3, %ymm10

vpsrlq      $32,   %ymm7,  %ymm11
vpsrlq      $32,   %ymm1,  %ymm12
vpsrlq      $32,   %ymm3, %ymm6
vpblendd    $0xAA, %ymm0,  %ymm11, %ymm11
vpblendd    $0xAA, %ymm2, %ymm12, %ymm12
vpblendd    $0xAA, %ymm4, %ymm6, %ymm6

vpunpcklqdq %ymm9, %ymm8, %ymm13
vpunpcklqdq %ymm11, %ymm10, %ymm7
vpunpcklqdq %ymm6, %ymm12, %ymm0
vpunpckhqdq %ymm9, %ymm8, %ymm1
vpunpckhqdq %ymm11, %ymm10, %ymm2
vpunpckhqdq %ymm6, %ymm12, %ymm3

vperm2i128  $0x20, %ymm7,  %ymm13,  %ymm8
vperm2i128  $0x20, %ymm1,  %ymm0,  %ymm9
vperm2i128  $0x20, %ymm3, %ymm2, %ymm10
vperm2i128  $0x31, %ymm7,  %ymm13,  %ymm11
vperm2i128  $0x31, %ymm1,  %ymm0,  %ymm12
vperm2i128  $0x31, %ymm3, %ymm2, %ymm6

vmovdqu %ymm8,    (%rdi)
vmovdqu %ymm9,  32(%rdi)
vmovdqu %ymm10,  64(%rdi)
vmovdqu %ymm11,  96(%rdi)
vmovdqu %ymm12, 128(%rdi)
vmovdqu %ymm6, 160(%rdi)
add $192, %rdi
/* packet 5: coefficients 640..767 */
vmovdqa 1152(%rsi), %ymm0
vmovdqa 1408(%rsi), %ymm1
vpshufb .Lserializer_v2_even_odd(%rip), %ymm0, %ymm0
vpshufb .Lserializer_v2_even_odd(%rip), %ymm1, %ymm1
vpermq $0xd8, %ymm0, %ymm0
vpermq $0xd8, %ymm1, %ymm1
vperm2i128 $0x20, %ymm1, %ymm0, %ymm8
vperm2i128 $0x31, %ymm1, %ymm0, %ymm12
vmovdqa 1184(%rsi), %ymm0
vmovdqa 1440(%rsi), %ymm1
vpshufb .Lserializer_v2_even_odd(%rip), %ymm0, %ymm0
vpshufb .Lserializer_v2_even_odd(%rip), %ymm1, %ymm1
vpermq $0xd8, %ymm0, %ymm0
vpermq $0xd8, %ymm1, %ymm1
vperm2i128 $0x20, %ymm1, %ymm0, %ymm9
vperm2i128 $0x31, %ymm1, %ymm0, %ymm6
vmovdqa 1216(%rsi), %ymm0
vmovdqa 1472(%rsi), %ymm1
vpshufb .Lserializer_v2_even_odd(%rip), %ymm0, %ymm0
vpshufb .Lserializer_v2_even_odd(%rip), %ymm1, %ymm1
vpermq $0xd8, %ymm0, %ymm0
vpermq $0xd8, %ymm1, %ymm1
vperm2i128 $0x20, %ymm1, %ymm0, %ymm10
vperm2i128 $0x31, %ymm1, %ymm0, %ymm13
vmovdqa 1248(%rsi), %ymm0
vmovdqa 1504(%rsi), %ymm1
vpshufb .Lserializer_v2_even_odd(%rip), %ymm0, %ymm0
vpshufb .Lserializer_v2_even_odd(%rip), %ymm1, %ymm1
vpermq $0xd8, %ymm0, %ymm0
vpermq $0xd8, %ymm1, %ymm1
vperm2i128 $0x20, %ymm1, %ymm0, %ymm11
vperm2i128 $0x31, %ymm1, %ymm0, %ymm7
vpmulhrsw %ymm15, %ymm8, %ymm2
vpmulhrsw %ymm15, %ymm9, %ymm3
vpmulhrsw %ymm15, %ymm10, %ymm4
vpmulhrsw %ymm15, %ymm11, %ymm5
vpmullw %ymm14, %ymm2, %ymm2
vpmullw %ymm14, %ymm3, %ymm3
vpmullw %ymm14, %ymm4, %ymm4
vpmullw %ymm14, %ymm5, %ymm5
vpsubw %ymm2, %ymm8,  %ymm8
vpsubw %ymm3, %ymm9,  %ymm9
vpsubw %ymm4, %ymm10,  %ymm10
vpsubw %ymm5, %ymm11,  %ymm11

vpmulhrsw %ymm15, %ymm12, %ymm2
vpmulhrsw %ymm15, %ymm6, %ymm3
vpmulhrsw %ymm15, %ymm13, %ymm4
vpmulhrsw %ymm15, %ymm7, %ymm5
vpmullw %ymm14, %ymm2, %ymm2
vpmullw %ymm14, %ymm3, %ymm3
vpmullw %ymm14, %ymm4, %ymm4
vpmullw %ymm14, %ymm5, %ymm5
vpsubw %ymm2, %ymm12,  %ymm12
vpsubw %ymm3, %ymm6,  %ymm6
vpsubw %ymm4, %ymm13,  %ymm13
vpsubw %ymm5, %ymm7, %ymm7

vpsraw $15,    %ymm8,  %ymm2
vpsraw $15,    %ymm9,  %ymm3
vpsraw $15,    %ymm10,  %ymm4
vpsraw $15,    %ymm11,  %ymm5
vpand  %ymm14,  %ymm2, %ymm2
vpand  %ymm14,  %ymm3, %ymm3
vpand  %ymm14,  %ymm4, %ymm4
vpand  %ymm14,  %ymm5, %ymm5
vpaddw %ymm2, %ymm8,  %ymm8
vpaddw %ymm3, %ymm9,  %ymm9
vpaddw %ymm4, %ymm10,  %ymm10
vpaddw %ymm5, %ymm11,  %ymm11

vpsraw $15,    %ymm12,  %ymm2
vpsraw $15,    %ymm6,  %ymm3
vpsraw $15,    %ymm13,  %ymm4
vpsraw $15,    %ymm7, %ymm5
vpand  %ymm14,  %ymm2, %ymm2
vpand  %ymm14,  %ymm3, %ymm3
vpand  %ymm14,  %ymm4, %ymm4
vpand  %ymm14,  %ymm5, %ymm5
vpaddw %ymm2, %ymm12,  %ymm12
vpaddw %ymm3, %ymm6,  %ymm6
vpaddw %ymm4, %ymm13,  %ymm13
vpaddw %ymm5, %ymm7, %ymm7

vpsllw $12,    %ymm9,  %ymm2
vpsllw $12,    %ymm6,  %ymm3
vpxor  %ymm2, %ymm8,  %ymm8
vpxor  %ymm3, %ymm12,  %ymm12
vpsllw $8,     %ymm10,  %ymm2
vpsllw $8,     %ymm13,  %ymm3
vpsrlw $4,     %ymm9,  %ymm4
vpsrlw $4,     %ymm6,  %ymm5
vpxor  %ymm2, %ymm4, %ymm9
vpxor  %ymm3, %ymm5, %ymm6
vpsllw $4,     %ymm11,  %ymm2
vpsllw $4,     %ymm7, %ymm3
vpsrlw $8,     %ymm10,  %ymm4
vpsrlw $8,     %ymm13,  %ymm5
vpxor  %ymm2, %ymm4, %ymm10
vpxor  %ymm3, %ymm5, %ymm13

#shuffle
vpslld      $16, %ymm9, %ymm7
vpslld      $16, %ymm12, %ymm0
vpslld      $16, %ymm13, %ymm1
vpblendw    $0xAA, %ymm7, %ymm8, %ymm7
vpblendw    $0xAA, %ymm0, %ymm10, %ymm0
vpblendw    $0xAA, %ymm1, %ymm6, %ymm1

vpsrlq      $16,   %ymm8, %ymm2
vpsrlq      $16,   %ymm10, %ymm3
vpsrlq      $16,   %ymm6, %ymm4
vpblendw    $0xAA, %ymm9, %ymm2, %ymm2
vpblendw    $0xAA, %ymm12, %ymm3, %ymm3
vpblendw    $0xAA, %ymm13, %ymm4, %ymm4

vpsllq      $32,   %ymm0,  %ymm8
vpsllq      $32,   %ymm2, %ymm9
vpsllq      $32,   %ymm4, %ymm10
vpblendd    $0xAA, %ymm8,  %ymm7,  %ymm8
vpblendd    $0xAA, %ymm9,  %ymm1,  %ymm9
vpblendd    $0xAA, %ymm10,  %ymm3, %ymm10

vpsrlq      $32,   %ymm7,  %ymm11
vpsrlq      $32,   %ymm1,  %ymm12
vpsrlq      $32,   %ymm3, %ymm6
vpblendd    $0xAA, %ymm0,  %ymm11, %ymm11
vpblendd    $0xAA, %ymm2, %ymm12, %ymm12
vpblendd    $0xAA, %ymm4, %ymm6, %ymm6

vpunpcklqdq %ymm9, %ymm8, %ymm13
vpunpcklqdq %ymm11, %ymm10, %ymm7
vpunpcklqdq %ymm6, %ymm12, %ymm0
vpunpckhqdq %ymm9, %ymm8, %ymm1
vpunpckhqdq %ymm11, %ymm10, %ymm2
vpunpckhqdq %ymm6, %ymm12, %ymm3

vperm2i128  $0x20, %ymm7,  %ymm13,  %ymm8
vperm2i128  $0x20, %ymm1,  %ymm0,  %ymm9
vperm2i128  $0x20, %ymm3, %ymm2, %ymm10
vperm2i128  $0x31, %ymm7,  %ymm13,  %ymm11
vperm2i128  $0x31, %ymm1,  %ymm0,  %ymm12
vperm2i128  $0x31, %ymm3, %ymm2, %ymm6

vmovdqu %ymm8,    (%rdi)
vmovdqu %ymm9,  32(%rdi)
vmovdqu %ymm10,  64(%rdi)
vmovdqu %ymm11,  96(%rdi)
vmovdqu %ymm12, 128(%rdi)
vmovdqu %ymm6, 160(%rdi)
add $192, %rdi
/* packet 6: coefficients 768..895 */
vmovdqa 2176(%rsi), %ymm0
vmovdqa 2048(%rsi), %ymm1
vpshufb .Lserializer_v2_even_odd(%rip), %ymm0, %ymm0
vpshufb .Lserializer_v2_even_odd(%rip), %ymm1, %ymm1
vpermq $0xd8, %ymm0, %ymm0
vpermq $0xd8, %ymm1, %ymm1
vperm2i128 $0x20, %ymm1, %ymm0, %ymm8
vperm2i128 $0x31, %ymm1, %ymm0, %ymm12
vmovdqa 2208(%rsi), %ymm0
vmovdqa 2080(%rsi), %ymm1
vpshufb .Lserializer_v2_even_odd(%rip), %ymm0, %ymm0
vpshufb .Lserializer_v2_even_odd(%rip), %ymm1, %ymm1
vpermq $0xd8, %ymm0, %ymm0
vpermq $0xd8, %ymm1, %ymm1
vperm2i128 $0x20, %ymm1, %ymm0, %ymm9
vperm2i128 $0x31, %ymm1, %ymm0, %ymm6
vmovdqa 2240(%rsi), %ymm0
vmovdqa 2112(%rsi), %ymm1
vpshufb .Lserializer_v2_even_odd(%rip), %ymm0, %ymm0
vpshufb .Lserializer_v2_even_odd(%rip), %ymm1, %ymm1
vpermq $0xd8, %ymm0, %ymm0
vpermq $0xd8, %ymm1, %ymm1
vperm2i128 $0x20, %ymm1, %ymm0, %ymm10
vperm2i128 $0x31, %ymm1, %ymm0, %ymm13
vmovdqa 2272(%rsi), %ymm0
vmovdqa 2144(%rsi), %ymm1
vpshufb .Lserializer_v2_even_odd(%rip), %ymm0, %ymm0
vpshufb .Lserializer_v2_even_odd(%rip), %ymm1, %ymm1
vpermq $0xd8, %ymm0, %ymm0
vpermq $0xd8, %ymm1, %ymm1
vperm2i128 $0x20, %ymm1, %ymm0, %ymm11
vperm2i128 $0x31, %ymm1, %ymm0, %ymm7
vpmulhrsw %ymm15, %ymm8, %ymm2
vpmulhrsw %ymm15, %ymm9, %ymm3
vpmulhrsw %ymm15, %ymm10, %ymm4
vpmulhrsw %ymm15, %ymm11, %ymm5
vpmullw %ymm14, %ymm2, %ymm2
vpmullw %ymm14, %ymm3, %ymm3
vpmullw %ymm14, %ymm4, %ymm4
vpmullw %ymm14, %ymm5, %ymm5
vpsubw %ymm2, %ymm8,  %ymm8
vpsubw %ymm3, %ymm9,  %ymm9
vpsubw %ymm4, %ymm10,  %ymm10
vpsubw %ymm5, %ymm11,  %ymm11

vpmulhrsw %ymm15, %ymm12, %ymm2
vpmulhrsw %ymm15, %ymm6, %ymm3
vpmulhrsw %ymm15, %ymm13, %ymm4
vpmulhrsw %ymm15, %ymm7, %ymm5
vpmullw %ymm14, %ymm2, %ymm2
vpmullw %ymm14, %ymm3, %ymm3
vpmullw %ymm14, %ymm4, %ymm4
vpmullw %ymm14, %ymm5, %ymm5
vpsubw %ymm2, %ymm12,  %ymm12
vpsubw %ymm3, %ymm6,  %ymm6
vpsubw %ymm4, %ymm13,  %ymm13
vpsubw %ymm5, %ymm7, %ymm7

vpsraw $15,    %ymm8,  %ymm2
vpsraw $15,    %ymm9,  %ymm3
vpsraw $15,    %ymm10,  %ymm4
vpsraw $15,    %ymm11,  %ymm5
vpand  %ymm14,  %ymm2, %ymm2
vpand  %ymm14,  %ymm3, %ymm3
vpand  %ymm14,  %ymm4, %ymm4
vpand  %ymm14,  %ymm5, %ymm5
vpaddw %ymm2, %ymm8,  %ymm8
vpaddw %ymm3, %ymm9,  %ymm9
vpaddw %ymm4, %ymm10,  %ymm10
vpaddw %ymm5, %ymm11,  %ymm11

vpsraw $15,    %ymm12,  %ymm2
vpsraw $15,    %ymm6,  %ymm3
vpsraw $15,    %ymm13,  %ymm4
vpsraw $15,    %ymm7, %ymm5
vpand  %ymm14,  %ymm2, %ymm2
vpand  %ymm14,  %ymm3, %ymm3
vpand  %ymm14,  %ymm4, %ymm4
vpand  %ymm14,  %ymm5, %ymm5
vpaddw %ymm2, %ymm12,  %ymm12
vpaddw %ymm3, %ymm6,  %ymm6
vpaddw %ymm4, %ymm13,  %ymm13
vpaddw %ymm5, %ymm7, %ymm7

vpsllw $12,    %ymm9,  %ymm2
vpsllw $12,    %ymm6,  %ymm3
vpxor  %ymm2, %ymm8,  %ymm8
vpxor  %ymm3, %ymm12,  %ymm12
vpsllw $8,     %ymm10,  %ymm2
vpsllw $8,     %ymm13,  %ymm3
vpsrlw $4,     %ymm9,  %ymm4
vpsrlw $4,     %ymm6,  %ymm5
vpxor  %ymm2, %ymm4, %ymm9
vpxor  %ymm3, %ymm5, %ymm6
vpsllw $4,     %ymm11,  %ymm2
vpsllw $4,     %ymm7, %ymm3
vpsrlw $8,     %ymm10,  %ymm4
vpsrlw $8,     %ymm13,  %ymm5
vpxor  %ymm2, %ymm4, %ymm10
vpxor  %ymm3, %ymm5, %ymm13

#shuffle
vpslld      $16, %ymm9, %ymm7
vpslld      $16, %ymm12, %ymm0
vpslld      $16, %ymm13, %ymm1
vpblendw    $0xAA, %ymm7, %ymm8, %ymm7
vpblendw    $0xAA, %ymm0, %ymm10, %ymm0
vpblendw    $0xAA, %ymm1, %ymm6, %ymm1

vpsrlq      $16,   %ymm8, %ymm2
vpsrlq      $16,   %ymm10, %ymm3
vpsrlq      $16,   %ymm6, %ymm4
vpblendw    $0xAA, %ymm9, %ymm2, %ymm2
vpblendw    $0xAA, %ymm12, %ymm3, %ymm3
vpblendw    $0xAA, %ymm13, %ymm4, %ymm4

vpsllq      $32,   %ymm0,  %ymm8
vpsllq      $32,   %ymm2, %ymm9
vpsllq      $32,   %ymm4, %ymm10
vpblendd    $0xAA, %ymm8,  %ymm7,  %ymm8
vpblendd    $0xAA, %ymm9,  %ymm1,  %ymm9
vpblendd    $0xAA, %ymm10,  %ymm3, %ymm10

vpsrlq      $32,   %ymm7,  %ymm11
vpsrlq      $32,   %ymm1,  %ymm12
vpsrlq      $32,   %ymm3, %ymm6
vpblendd    $0xAA, %ymm0,  %ymm11, %ymm11
vpblendd    $0xAA, %ymm2, %ymm12, %ymm12
vpblendd    $0xAA, %ymm4, %ymm6, %ymm6

vpunpcklqdq %ymm9, %ymm8, %ymm13
vpunpcklqdq %ymm11, %ymm10, %ymm7
vpunpcklqdq %ymm6, %ymm12, %ymm0
vpunpckhqdq %ymm9, %ymm8, %ymm1
vpunpckhqdq %ymm11, %ymm10, %ymm2
vpunpckhqdq %ymm6, %ymm12, %ymm3

vperm2i128  $0x20, %ymm7,  %ymm13,  %ymm8
vperm2i128  $0x20, %ymm1,  %ymm0,  %ymm9
vperm2i128  $0x20, %ymm3, %ymm2, %ymm10
vperm2i128  $0x31, %ymm7,  %ymm13,  %ymm11
vperm2i128  $0x31, %ymm1,  %ymm0,  %ymm12
vperm2i128  $0x31, %ymm3, %ymm2, %ymm6

vmovdqu %ymm8,    (%rdi)
vmovdqu %ymm9,  32(%rdi)
vmovdqu %ymm10,  64(%rdi)
vmovdqu %ymm11,  96(%rdi)
vmovdqu %ymm12, 128(%rdi)
vmovdqu %ymm6, 160(%rdi)
add $192, %rdi
/* packet 7: coefficients 896..1023 */
vmovdqa 1920(%rsi), %ymm0
vmovdqa 1792(%rsi), %ymm1
vpshufb .Lserializer_v2_even_odd(%rip), %ymm0, %ymm0
vpshufb .Lserializer_v2_even_odd(%rip), %ymm1, %ymm1
vpermq $0xd8, %ymm0, %ymm0
vpermq $0xd8, %ymm1, %ymm1
vperm2i128 $0x20, %ymm1, %ymm0, %ymm8
vperm2i128 $0x31, %ymm1, %ymm0, %ymm12
vmovdqa 1952(%rsi), %ymm0
vmovdqa 1824(%rsi), %ymm1
vpshufb .Lserializer_v2_even_odd(%rip), %ymm0, %ymm0
vpshufb .Lserializer_v2_even_odd(%rip), %ymm1, %ymm1
vpermq $0xd8, %ymm0, %ymm0
vpermq $0xd8, %ymm1, %ymm1
vperm2i128 $0x20, %ymm1, %ymm0, %ymm9
vperm2i128 $0x31, %ymm1, %ymm0, %ymm6
vmovdqa 1984(%rsi), %ymm0
vmovdqa 1856(%rsi), %ymm1
vpshufb .Lserializer_v2_even_odd(%rip), %ymm0, %ymm0
vpshufb .Lserializer_v2_even_odd(%rip), %ymm1, %ymm1
vpermq $0xd8, %ymm0, %ymm0
vpermq $0xd8, %ymm1, %ymm1
vperm2i128 $0x20, %ymm1, %ymm0, %ymm10
vperm2i128 $0x31, %ymm1, %ymm0, %ymm13
vmovdqa 2016(%rsi), %ymm0
vmovdqa 1888(%rsi), %ymm1
vpshufb .Lserializer_v2_even_odd(%rip), %ymm0, %ymm0
vpshufb .Lserializer_v2_even_odd(%rip), %ymm1, %ymm1
vpermq $0xd8, %ymm0, %ymm0
vpermq $0xd8, %ymm1, %ymm1
vperm2i128 $0x20, %ymm1, %ymm0, %ymm11
vperm2i128 $0x31, %ymm1, %ymm0, %ymm7
vpmulhrsw %ymm15, %ymm8, %ymm2
vpmulhrsw %ymm15, %ymm9, %ymm3
vpmulhrsw %ymm15, %ymm10, %ymm4
vpmulhrsw %ymm15, %ymm11, %ymm5
vpmullw %ymm14, %ymm2, %ymm2
vpmullw %ymm14, %ymm3, %ymm3
vpmullw %ymm14, %ymm4, %ymm4
vpmullw %ymm14, %ymm5, %ymm5
vpsubw %ymm2, %ymm8,  %ymm8
vpsubw %ymm3, %ymm9,  %ymm9
vpsubw %ymm4, %ymm10,  %ymm10
vpsubw %ymm5, %ymm11,  %ymm11

vpmulhrsw %ymm15, %ymm12, %ymm2
vpmulhrsw %ymm15, %ymm6, %ymm3
vpmulhrsw %ymm15, %ymm13, %ymm4
vpmulhrsw %ymm15, %ymm7, %ymm5
vpmullw %ymm14, %ymm2, %ymm2
vpmullw %ymm14, %ymm3, %ymm3
vpmullw %ymm14, %ymm4, %ymm4
vpmullw %ymm14, %ymm5, %ymm5
vpsubw %ymm2, %ymm12,  %ymm12
vpsubw %ymm3, %ymm6,  %ymm6
vpsubw %ymm4, %ymm13,  %ymm13
vpsubw %ymm5, %ymm7, %ymm7

vpsraw $15,    %ymm8,  %ymm2
vpsraw $15,    %ymm9,  %ymm3
vpsraw $15,    %ymm10,  %ymm4
vpsraw $15,    %ymm11,  %ymm5
vpand  %ymm14,  %ymm2, %ymm2
vpand  %ymm14,  %ymm3, %ymm3
vpand  %ymm14,  %ymm4, %ymm4
vpand  %ymm14,  %ymm5, %ymm5
vpaddw %ymm2, %ymm8,  %ymm8
vpaddw %ymm3, %ymm9,  %ymm9
vpaddw %ymm4, %ymm10,  %ymm10
vpaddw %ymm5, %ymm11,  %ymm11

vpsraw $15,    %ymm12,  %ymm2
vpsraw $15,    %ymm6,  %ymm3
vpsraw $15,    %ymm13,  %ymm4
vpsraw $15,    %ymm7, %ymm5
vpand  %ymm14,  %ymm2, %ymm2
vpand  %ymm14,  %ymm3, %ymm3
vpand  %ymm14,  %ymm4, %ymm4
vpand  %ymm14,  %ymm5, %ymm5
vpaddw %ymm2, %ymm12,  %ymm12
vpaddw %ymm3, %ymm6,  %ymm6
vpaddw %ymm4, %ymm13,  %ymm13
vpaddw %ymm5, %ymm7, %ymm7

vpsllw $12,    %ymm9,  %ymm2
vpsllw $12,    %ymm6,  %ymm3
vpxor  %ymm2, %ymm8,  %ymm8
vpxor  %ymm3, %ymm12,  %ymm12
vpsllw $8,     %ymm10,  %ymm2
vpsllw $8,     %ymm13,  %ymm3
vpsrlw $4,     %ymm9,  %ymm4
vpsrlw $4,     %ymm6,  %ymm5
vpxor  %ymm2, %ymm4, %ymm9
vpxor  %ymm3, %ymm5, %ymm6
vpsllw $4,     %ymm11,  %ymm2
vpsllw $4,     %ymm7, %ymm3
vpsrlw $8,     %ymm10,  %ymm4
vpsrlw $8,     %ymm13,  %ymm5
vpxor  %ymm2, %ymm4, %ymm10
vpxor  %ymm3, %ymm5, %ymm13

#shuffle
vpslld      $16, %ymm9, %ymm7
vpslld      $16, %ymm12, %ymm0
vpslld      $16, %ymm13, %ymm1
vpblendw    $0xAA, %ymm7, %ymm8, %ymm7
vpblendw    $0xAA, %ymm0, %ymm10, %ymm0
vpblendw    $0xAA, %ymm1, %ymm6, %ymm1

vpsrlq      $16,   %ymm8, %ymm2
vpsrlq      $16,   %ymm10, %ymm3
vpsrlq      $16,   %ymm6, %ymm4
vpblendw    $0xAA, %ymm9, %ymm2, %ymm2
vpblendw    $0xAA, %ymm12, %ymm3, %ymm3
vpblendw    $0xAA, %ymm13, %ymm4, %ymm4

vpsllq      $32,   %ymm0,  %ymm8
vpsllq      $32,   %ymm2, %ymm9
vpsllq      $32,   %ymm4, %ymm10
vpblendd    $0xAA, %ymm8,  %ymm7,  %ymm8
vpblendd    $0xAA, %ymm9,  %ymm1,  %ymm9
vpblendd    $0xAA, %ymm10,  %ymm3, %ymm10

vpsrlq      $32,   %ymm7,  %ymm11
vpsrlq      $32,   %ymm1,  %ymm12
vpsrlq      $32,   %ymm3, %ymm6
vpblendd    $0xAA, %ymm0,  %ymm11, %ymm11
vpblendd    $0xAA, %ymm2, %ymm12, %ymm12
vpblendd    $0xAA, %ymm4, %ymm6, %ymm6

vpunpcklqdq %ymm9, %ymm8, %ymm13
vpunpcklqdq %ymm11, %ymm10, %ymm7
vpunpcklqdq %ymm6, %ymm12, %ymm0
vpunpckhqdq %ymm9, %ymm8, %ymm1
vpunpckhqdq %ymm11, %ymm10, %ymm2
vpunpckhqdq %ymm6, %ymm12, %ymm3

vperm2i128  $0x20, %ymm7,  %ymm13,  %ymm8
vperm2i128  $0x20, %ymm1,  %ymm0,  %ymm9
vperm2i128  $0x20, %ymm3, %ymm2, %ymm10
vperm2i128  $0x31, %ymm7,  %ymm13,  %ymm11
vperm2i128  $0x31, %ymm1,  %ymm0,  %ymm12
vperm2i128  $0x31, %ymm3, %ymm2, %ymm6

vmovdqu %ymm8,    (%rdi)
vmovdqu %ymm9,  32(%rdi)
vmovdqu %ymm10,  64(%rdi)
vmovdqu %ymm11,  96(%rdi)
vmovdqu %ymm12, 128(%rdi)
vmovdqu %ymm6, 160(%rdi)
add $192, %rdi
/* packet 8: coefficients 1024..1151 */
vmovdqa 1664(%rsi), %ymm0
vmovdqa 1536(%rsi), %ymm1
vpshufb .Lserializer_v2_even_odd(%rip), %ymm0, %ymm0
vpshufb .Lserializer_v2_even_odd(%rip), %ymm1, %ymm1
vpermq $0xd8, %ymm0, %ymm0
vpermq $0xd8, %ymm1, %ymm1
vperm2i128 $0x20, %ymm1, %ymm0, %ymm8
vperm2i128 $0x31, %ymm1, %ymm0, %ymm12
vmovdqa 1696(%rsi), %ymm0
vmovdqa 1568(%rsi), %ymm1
vpshufb .Lserializer_v2_even_odd(%rip), %ymm0, %ymm0
vpshufb .Lserializer_v2_even_odd(%rip), %ymm1, %ymm1
vpermq $0xd8, %ymm0, %ymm0
vpermq $0xd8, %ymm1, %ymm1
vperm2i128 $0x20, %ymm1, %ymm0, %ymm9
vperm2i128 $0x31, %ymm1, %ymm0, %ymm6
vmovdqa 1728(%rsi), %ymm0
vmovdqa 1600(%rsi), %ymm1
vpshufb .Lserializer_v2_even_odd(%rip), %ymm0, %ymm0
vpshufb .Lserializer_v2_even_odd(%rip), %ymm1, %ymm1
vpermq $0xd8, %ymm0, %ymm0
vpermq $0xd8, %ymm1, %ymm1
vperm2i128 $0x20, %ymm1, %ymm0, %ymm10
vperm2i128 $0x31, %ymm1, %ymm0, %ymm13
vmovdqa 1760(%rsi), %ymm0
vmovdqa 1632(%rsi), %ymm1
vpshufb .Lserializer_v2_even_odd(%rip), %ymm0, %ymm0
vpshufb .Lserializer_v2_even_odd(%rip), %ymm1, %ymm1
vpermq $0xd8, %ymm0, %ymm0
vpermq $0xd8, %ymm1, %ymm1
vperm2i128 $0x20, %ymm1, %ymm0, %ymm11
vperm2i128 $0x31, %ymm1, %ymm0, %ymm7
vpmulhrsw %ymm15, %ymm8, %ymm2
vpmulhrsw %ymm15, %ymm9, %ymm3
vpmulhrsw %ymm15, %ymm10, %ymm4
vpmulhrsw %ymm15, %ymm11, %ymm5
vpmullw %ymm14, %ymm2, %ymm2
vpmullw %ymm14, %ymm3, %ymm3
vpmullw %ymm14, %ymm4, %ymm4
vpmullw %ymm14, %ymm5, %ymm5
vpsubw %ymm2, %ymm8,  %ymm8
vpsubw %ymm3, %ymm9,  %ymm9
vpsubw %ymm4, %ymm10,  %ymm10
vpsubw %ymm5, %ymm11,  %ymm11

vpmulhrsw %ymm15, %ymm12, %ymm2
vpmulhrsw %ymm15, %ymm6, %ymm3
vpmulhrsw %ymm15, %ymm13, %ymm4
vpmulhrsw %ymm15, %ymm7, %ymm5
vpmullw %ymm14, %ymm2, %ymm2
vpmullw %ymm14, %ymm3, %ymm3
vpmullw %ymm14, %ymm4, %ymm4
vpmullw %ymm14, %ymm5, %ymm5
vpsubw %ymm2, %ymm12,  %ymm12
vpsubw %ymm3, %ymm6,  %ymm6
vpsubw %ymm4, %ymm13,  %ymm13
vpsubw %ymm5, %ymm7, %ymm7

vpsraw $15,    %ymm8,  %ymm2
vpsraw $15,    %ymm9,  %ymm3
vpsraw $15,    %ymm10,  %ymm4
vpsraw $15,    %ymm11,  %ymm5
vpand  %ymm14,  %ymm2, %ymm2
vpand  %ymm14,  %ymm3, %ymm3
vpand  %ymm14,  %ymm4, %ymm4
vpand  %ymm14,  %ymm5, %ymm5
vpaddw %ymm2, %ymm8,  %ymm8
vpaddw %ymm3, %ymm9,  %ymm9
vpaddw %ymm4, %ymm10,  %ymm10
vpaddw %ymm5, %ymm11,  %ymm11

vpsraw $15,    %ymm12,  %ymm2
vpsraw $15,    %ymm6,  %ymm3
vpsraw $15,    %ymm13,  %ymm4
vpsraw $15,    %ymm7, %ymm5
vpand  %ymm14,  %ymm2, %ymm2
vpand  %ymm14,  %ymm3, %ymm3
vpand  %ymm14,  %ymm4, %ymm4
vpand  %ymm14,  %ymm5, %ymm5
vpaddw %ymm2, %ymm12,  %ymm12
vpaddw %ymm3, %ymm6,  %ymm6
vpaddw %ymm4, %ymm13,  %ymm13
vpaddw %ymm5, %ymm7, %ymm7

vpsllw $12,    %ymm9,  %ymm2
vpsllw $12,    %ymm6,  %ymm3
vpxor  %ymm2, %ymm8,  %ymm8
vpxor  %ymm3, %ymm12,  %ymm12
vpsllw $8,     %ymm10,  %ymm2
vpsllw $8,     %ymm13,  %ymm3
vpsrlw $4,     %ymm9,  %ymm4
vpsrlw $4,     %ymm6,  %ymm5
vpxor  %ymm2, %ymm4, %ymm9
vpxor  %ymm3, %ymm5, %ymm6
vpsllw $4,     %ymm11,  %ymm2
vpsllw $4,     %ymm7, %ymm3
vpsrlw $8,     %ymm10,  %ymm4
vpsrlw $8,     %ymm13,  %ymm5
vpxor  %ymm2, %ymm4, %ymm10
vpxor  %ymm3, %ymm5, %ymm13

#shuffle
vpslld      $16, %ymm9, %ymm7
vpslld      $16, %ymm12, %ymm0
vpslld      $16, %ymm13, %ymm1
vpblendw    $0xAA, %ymm7, %ymm8, %ymm7
vpblendw    $0xAA, %ymm0, %ymm10, %ymm0
vpblendw    $0xAA, %ymm1, %ymm6, %ymm1

vpsrlq      $16,   %ymm8, %ymm2
vpsrlq      $16,   %ymm10, %ymm3
vpsrlq      $16,   %ymm6, %ymm4
vpblendw    $0xAA, %ymm9, %ymm2, %ymm2
vpblendw    $0xAA, %ymm12, %ymm3, %ymm3
vpblendw    $0xAA, %ymm13, %ymm4, %ymm4

vpsllq      $32,   %ymm0,  %ymm8
vpsllq      $32,   %ymm2, %ymm9
vpsllq      $32,   %ymm4, %ymm10
vpblendd    $0xAA, %ymm8,  %ymm7,  %ymm8
vpblendd    $0xAA, %ymm9,  %ymm1,  %ymm9
vpblendd    $0xAA, %ymm10,  %ymm3, %ymm10

vpsrlq      $32,   %ymm7,  %ymm11
vpsrlq      $32,   %ymm1,  %ymm12
vpsrlq      $32,   %ymm3, %ymm6
vpblendd    $0xAA, %ymm0,  %ymm11, %ymm11
vpblendd    $0xAA, %ymm2, %ymm12, %ymm12
vpblendd    $0xAA, %ymm4, %ymm6, %ymm6

vpunpcklqdq %ymm9, %ymm8, %ymm13
vpunpcklqdq %ymm11, %ymm10, %ymm7
vpunpcklqdq %ymm6, %ymm12, %ymm0
vpunpckhqdq %ymm9, %ymm8, %ymm1
vpunpckhqdq %ymm11, %ymm10, %ymm2
vpunpckhqdq %ymm6, %ymm12, %ymm3

vperm2i128  $0x20, %ymm7,  %ymm13,  %ymm8
vperm2i128  $0x20, %ymm1,  %ymm0,  %ymm9
vperm2i128  $0x20, %ymm3, %ymm2, %ymm10
vperm2i128  $0x31, %ymm7,  %ymm13,  %ymm11
vperm2i128  $0x31, %ymm1,  %ymm0,  %ymm12
vperm2i128  $0x31, %ymm3, %ymm2, %ymm6

vmovdqu %ymm8,    (%rdi)
vmovdqu %ymm9,  32(%rdi)
vmovdqu %ymm10,  64(%rdi)
vmovdqu %ymm11,  96(%rdi)
vmovdqu %ymm12, 128(%rdi)
vmovdqu %ymm6, 160(%rdi)
vzeroupper
ret
.size ntruplus1152_exp001_scale1_r_serializer_v2, .-ntruplus1152_exp001_scale1_r_serializer_v2
.section .rodata,"a",@progbits
.p2align 5
.Lserializer_v2_even_odd:
  .byte 0,1,4,5,8,9,12,13,2,3,6,7,10,11,14,15,0,1,4,5,8,9,12,13,2,3,6,7,10,11,14,15
.section .note.GNU-stack,"",@progbits
