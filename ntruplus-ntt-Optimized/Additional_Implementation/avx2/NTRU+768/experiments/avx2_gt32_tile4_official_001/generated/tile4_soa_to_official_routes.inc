	.macro TILE4_SOA_TO_OFFICIAL_WORDS
	vmovdqu 0(%rsi), %ymm0
	vperm2i128 $32, 128(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_0(%rip), %ymm0, %ymm1
	vmovdqu 0(%rsi), %ymm0
	vperm2i128 $49, 128(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_1(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 0(%rdi)
	vmovdqu 32(%rsi), %ymm0
	vperm2i128 $32, 160(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_0(%rip), %ymm0, %ymm1
	vmovdqu 32(%rsi), %ymm0
	vperm2i128 $49, 160(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_1(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 32(%rdi)
	vmovdqu 64(%rsi), %ymm0
	vperm2i128 $32, 192(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_0(%rip), %ymm0, %ymm1
	vmovdqu 64(%rsi), %ymm0
	vperm2i128 $49, 192(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_1(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 64(%rdi)
	vmovdqu 96(%rsi), %ymm0
	vperm2i128 $32, 224(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_0(%rip), %ymm0, %ymm1
	vmovdqu 96(%rsi), %ymm0
	vperm2i128 $49, 224(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_1(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 96(%rdi)
	vmovdqu 0(%rsi), %ymm0
	vperm2i128 $32, 128(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_2(%rip), %ymm0, %ymm1
	vmovdqu 0(%rsi), %ymm0
	vperm2i128 $49, 128(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_3(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 128(%rdi)
	vmovdqu 32(%rsi), %ymm0
	vperm2i128 $32, 160(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_2(%rip), %ymm0, %ymm1
	vmovdqu 32(%rsi), %ymm0
	vperm2i128 $49, 160(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_3(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 160(%rdi)
	vmovdqu 64(%rsi), %ymm0
	vperm2i128 $32, 192(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_2(%rip), %ymm0, %ymm1
	vmovdqu 64(%rsi), %ymm0
	vperm2i128 $49, 192(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_3(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 192(%rdi)
	vmovdqu 96(%rsi), %ymm0
	vperm2i128 $32, 224(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_2(%rip), %ymm0, %ymm1
	vmovdqu 96(%rsi), %ymm0
	vperm2i128 $49, 224(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_3(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 224(%rdi)
	vmovdqu 1152(%rsi), %ymm0
	vperm2i128 $32, 1024(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_4(%rip), %ymm0, %ymm1
	vmovdqu 1152(%rsi), %ymm0
	vperm2i128 $49, 1024(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_5(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 256(%rdi)
	vmovdqu 1184(%rsi), %ymm0
	vperm2i128 $32, 1056(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_4(%rip), %ymm0, %ymm1
	vmovdqu 1184(%rsi), %ymm0
	vperm2i128 $49, 1056(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_5(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 288(%rdi)
	vmovdqu 1216(%rsi), %ymm0
	vperm2i128 $32, 1088(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_4(%rip), %ymm0, %ymm1
	vmovdqu 1216(%rsi), %ymm0
	vperm2i128 $49, 1088(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_5(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 320(%rdi)
	vmovdqu 1248(%rsi), %ymm0
	vperm2i128 $32, 1120(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_4(%rip), %ymm0, %ymm1
	vmovdqu 1248(%rsi), %ymm0
	vperm2i128 $49, 1120(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_5(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 352(%rdi)
	vmovdqu 1152(%rsi), %ymm0
	vperm2i128 $32, 1024(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_6(%rip), %ymm0, %ymm1
	vmovdqu 1152(%rsi), %ymm0
	vperm2i128 $49, 1024(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_7(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 384(%rdi)
	vmovdqu 1184(%rsi), %ymm0
	vperm2i128 $32, 1056(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_6(%rip), %ymm0, %ymm1
	vmovdqu 1184(%rsi), %ymm0
	vperm2i128 $49, 1056(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_7(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 416(%rdi)
	vmovdqu 1216(%rsi), %ymm0
	vperm2i128 $32, 1088(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_6(%rip), %ymm0, %ymm1
	vmovdqu 1216(%rsi), %ymm0
	vperm2i128 $49, 1088(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_7(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 448(%rdi)
	vmovdqu 1248(%rsi), %ymm0
	vperm2i128 $32, 1120(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_6(%rip), %ymm0, %ymm1
	vmovdqu 1248(%rsi), %ymm0
	vperm2i128 $49, 1120(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_7(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 480(%rdi)
	vmovdqu 512(%rsi), %ymm0
	vperm2i128 $32, 640(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_8(%rip), %ymm0, %ymm1
	vmovdqu 512(%rsi), %ymm0
	vperm2i128 $49, 640(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_9(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 512(%rdi)
	vmovdqu 544(%rsi), %ymm0
	vperm2i128 $32, 672(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_8(%rip), %ymm0, %ymm1
	vmovdqu 544(%rsi), %ymm0
	vperm2i128 $49, 672(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_9(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 544(%rdi)
	vmovdqu 576(%rsi), %ymm0
	vperm2i128 $32, 704(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_8(%rip), %ymm0, %ymm1
	vmovdqu 576(%rsi), %ymm0
	vperm2i128 $49, 704(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_9(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 576(%rdi)
	vmovdqu 608(%rsi), %ymm0
	vperm2i128 $32, 736(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_8(%rip), %ymm0, %ymm1
	vmovdqu 608(%rsi), %ymm0
	vperm2i128 $49, 736(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_9(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 608(%rdi)
	vmovdqu 512(%rsi), %ymm0
	vperm2i128 $32, 640(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_10(%rip), %ymm0, %ymm1
	vmovdqu 512(%rsi), %ymm0
	vperm2i128 $49, 640(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_11(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 640(%rdi)
	vmovdqu 544(%rsi), %ymm0
	vperm2i128 $32, 672(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_10(%rip), %ymm0, %ymm1
	vmovdqu 544(%rsi), %ymm0
	vperm2i128 $49, 672(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_11(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 672(%rdi)
	vmovdqu 576(%rsi), %ymm0
	vperm2i128 $32, 704(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_10(%rip), %ymm0, %ymm1
	vmovdqu 576(%rsi), %ymm0
	vperm2i128 $49, 704(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_11(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 704(%rdi)
	vmovdqu 608(%rsi), %ymm0
	vperm2i128 $32, 736(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_10(%rip), %ymm0, %ymm1
	vmovdqu 608(%rsi), %ymm0
	vperm2i128 $49, 736(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_11(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 736(%rdi)
	vmovdqu 1408(%rsi), %ymm0
	vperm2i128 $32, 1280(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_12(%rip), %ymm0, %ymm1
	vmovdqu 1408(%rsi), %ymm0
	vperm2i128 $49, 1280(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_13(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 768(%rdi)
	vmovdqu 1440(%rsi), %ymm0
	vperm2i128 $32, 1312(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_12(%rip), %ymm0, %ymm1
	vmovdqu 1440(%rsi), %ymm0
	vperm2i128 $49, 1312(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_13(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 800(%rdi)
	vmovdqu 1472(%rsi), %ymm0
	vperm2i128 $32, 1344(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_12(%rip), %ymm0, %ymm1
	vmovdqu 1472(%rsi), %ymm0
	vperm2i128 $49, 1344(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_13(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 832(%rdi)
	vmovdqu 1504(%rsi), %ymm0
	vperm2i128 $32, 1376(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_12(%rip), %ymm0, %ymm1
	vmovdqu 1504(%rsi), %ymm0
	vperm2i128 $49, 1376(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_13(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 864(%rdi)
	vmovdqu 1408(%rsi), %ymm0
	vperm2i128 $32, 1280(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_14(%rip), %ymm0, %ymm1
	vmovdqu 1408(%rsi), %ymm0
	vperm2i128 $49, 1280(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_15(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 896(%rdi)
	vmovdqu 1440(%rsi), %ymm0
	vperm2i128 $32, 1312(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_14(%rip), %ymm0, %ymm1
	vmovdqu 1440(%rsi), %ymm0
	vperm2i128 $49, 1312(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_15(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 928(%rdi)
	vmovdqu 1472(%rsi), %ymm0
	vperm2i128 $32, 1344(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_14(%rip), %ymm0, %ymm1
	vmovdqu 1472(%rsi), %ymm0
	vperm2i128 $49, 1344(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_15(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 960(%rdi)
	vmovdqu 1504(%rsi), %ymm0
	vperm2i128 $32, 1376(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_14(%rip), %ymm0, %ymm1
	vmovdqu 1504(%rsi), %ymm0
	vperm2i128 $49, 1376(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_15(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 992(%rdi)
	vmovdqu 768(%rsi), %ymm0
	vperm2i128 $32, 896(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_0(%rip), %ymm0, %ymm1
	vmovdqu 768(%rsi), %ymm0
	vperm2i128 $49, 896(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_1(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 1024(%rdi)
	vmovdqu 800(%rsi), %ymm0
	vperm2i128 $32, 928(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_0(%rip), %ymm0, %ymm1
	vmovdqu 800(%rsi), %ymm0
	vperm2i128 $49, 928(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_1(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 1056(%rdi)
	vmovdqu 832(%rsi), %ymm0
	vperm2i128 $32, 960(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_0(%rip), %ymm0, %ymm1
	vmovdqu 832(%rsi), %ymm0
	vperm2i128 $49, 960(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_1(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 1088(%rdi)
	vmovdqu 864(%rsi), %ymm0
	vperm2i128 $32, 992(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_0(%rip), %ymm0, %ymm1
	vmovdqu 864(%rsi), %ymm0
	vperm2i128 $49, 992(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_1(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 1120(%rdi)
	vmovdqu 768(%rsi), %ymm0
	vperm2i128 $32, 896(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_2(%rip), %ymm0, %ymm1
	vmovdqu 768(%rsi), %ymm0
	vperm2i128 $49, 896(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_3(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 1152(%rdi)
	vmovdqu 800(%rsi), %ymm0
	vperm2i128 $32, 928(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_2(%rip), %ymm0, %ymm1
	vmovdqu 800(%rsi), %ymm0
	vperm2i128 $49, 928(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_3(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 1184(%rdi)
	vmovdqu 832(%rsi), %ymm0
	vperm2i128 $32, 960(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_2(%rip), %ymm0, %ymm1
	vmovdqu 832(%rsi), %ymm0
	vperm2i128 $49, 960(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_3(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 1216(%rdi)
	vmovdqu 864(%rsi), %ymm0
	vperm2i128 $32, 992(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_2(%rip), %ymm0, %ymm1
	vmovdqu 864(%rsi), %ymm0
	vperm2i128 $49, 992(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_3(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 1248(%rdi)
	vmovdqu 384(%rsi), %ymm0
	vperm2i128 $32, 256(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_4(%rip), %ymm0, %ymm1
	vmovdqu 384(%rsi), %ymm0
	vperm2i128 $49, 256(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_5(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 1280(%rdi)
	vmovdqu 416(%rsi), %ymm0
	vperm2i128 $32, 288(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_4(%rip), %ymm0, %ymm1
	vmovdqu 416(%rsi), %ymm0
	vperm2i128 $49, 288(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_5(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 1312(%rdi)
	vmovdqu 448(%rsi), %ymm0
	vperm2i128 $32, 320(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_4(%rip), %ymm0, %ymm1
	vmovdqu 448(%rsi), %ymm0
	vperm2i128 $49, 320(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_5(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 1344(%rdi)
	vmovdqu 480(%rsi), %ymm0
	vperm2i128 $32, 352(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_4(%rip), %ymm0, %ymm1
	vmovdqu 480(%rsi), %ymm0
	vperm2i128 $49, 352(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_5(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 1376(%rdi)
	vmovdqu 384(%rsi), %ymm0
	vperm2i128 $32, 256(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_6(%rip), %ymm0, %ymm1
	vmovdqu 384(%rsi), %ymm0
	vperm2i128 $49, 256(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_7(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 1408(%rdi)
	vmovdqu 416(%rsi), %ymm0
	vperm2i128 $32, 288(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_6(%rip), %ymm0, %ymm1
	vmovdqu 416(%rsi), %ymm0
	vperm2i128 $49, 288(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_7(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 1440(%rdi)
	vmovdqu 448(%rsi), %ymm0
	vperm2i128 $32, 320(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_6(%rip), %ymm0, %ymm1
	vmovdqu 448(%rsi), %ymm0
	vperm2i128 $49, 320(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_7(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 1472(%rdi)
	vmovdqu 480(%rsi), %ymm0
	vperm2i128 $32, 352(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_6(%rip), %ymm0, %ymm1
	vmovdqu 480(%rsi), %ymm0
	vperm2i128 $49, 352(%rsi), %ymm0, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_7(%rip), %ymm0, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 1504(%rdi)
	.endm

	.macro TILE4_SOA_TO_OFFICIAL_WORDS_GROUPED
	vmovdqu 0(%rsi), %ymm0
	vmovdqu 128(%rsi), %ymm3
	vperm2i128 $32, %ymm3, %ymm0, %ymm4
	vperm2i128 $49, %ymm3, %ymm0, %ymm5
	vpshufb .Ltile4_encodeq_soa_mask_0(%rip), %ymm4, %ymm1
	vpshufb .Ltile4_encodeq_soa_mask_1(%rip), %ymm5, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 0(%rdi)
	vpshufb .Ltile4_encodeq_soa_mask_2(%rip), %ymm4, %ymm1
	vpshufb .Ltile4_encodeq_soa_mask_3(%rip), %ymm5, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 128(%rdi)
	vmovdqu 32(%rsi), %ymm0
	vmovdqu 160(%rsi), %ymm3
	vperm2i128 $32, %ymm3, %ymm0, %ymm4
	vperm2i128 $49, %ymm3, %ymm0, %ymm5
	vpshufb .Ltile4_encodeq_soa_mask_0(%rip), %ymm4, %ymm1
	vpshufb .Ltile4_encodeq_soa_mask_1(%rip), %ymm5, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 32(%rdi)
	vpshufb .Ltile4_encodeq_soa_mask_2(%rip), %ymm4, %ymm1
	vpshufb .Ltile4_encodeq_soa_mask_3(%rip), %ymm5, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 160(%rdi)
	vmovdqu 64(%rsi), %ymm0
	vmovdqu 192(%rsi), %ymm3
	vperm2i128 $32, %ymm3, %ymm0, %ymm4
	vperm2i128 $49, %ymm3, %ymm0, %ymm5
	vpshufb .Ltile4_encodeq_soa_mask_0(%rip), %ymm4, %ymm1
	vpshufb .Ltile4_encodeq_soa_mask_1(%rip), %ymm5, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 64(%rdi)
	vpshufb .Ltile4_encodeq_soa_mask_2(%rip), %ymm4, %ymm1
	vpshufb .Ltile4_encodeq_soa_mask_3(%rip), %ymm5, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 192(%rdi)
	vmovdqu 96(%rsi), %ymm0
	vmovdqu 224(%rsi), %ymm3
	vperm2i128 $32, %ymm3, %ymm0, %ymm4
	vperm2i128 $49, %ymm3, %ymm0, %ymm5
	vpshufb .Ltile4_encodeq_soa_mask_0(%rip), %ymm4, %ymm1
	vpshufb .Ltile4_encodeq_soa_mask_1(%rip), %ymm5, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 96(%rdi)
	vpshufb .Ltile4_encodeq_soa_mask_2(%rip), %ymm4, %ymm1
	vpshufb .Ltile4_encodeq_soa_mask_3(%rip), %ymm5, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 224(%rdi)
	vmovdqu 1152(%rsi), %ymm0
	vmovdqu 1024(%rsi), %ymm3
	vperm2i128 $32, %ymm3, %ymm0, %ymm4
	vperm2i128 $49, %ymm3, %ymm0, %ymm5
	vpshufb .Ltile4_encodeq_soa_mask_4(%rip), %ymm4, %ymm1
	vpshufb .Ltile4_encodeq_soa_mask_5(%rip), %ymm5, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 256(%rdi)
	vpshufb .Ltile4_encodeq_soa_mask_6(%rip), %ymm4, %ymm1
	vpshufb .Ltile4_encodeq_soa_mask_7(%rip), %ymm5, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 384(%rdi)
	vmovdqu 1184(%rsi), %ymm0
	vmovdqu 1056(%rsi), %ymm3
	vperm2i128 $32, %ymm3, %ymm0, %ymm4
	vperm2i128 $49, %ymm3, %ymm0, %ymm5
	vpshufb .Ltile4_encodeq_soa_mask_4(%rip), %ymm4, %ymm1
	vpshufb .Ltile4_encodeq_soa_mask_5(%rip), %ymm5, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 288(%rdi)
	vpshufb .Ltile4_encodeq_soa_mask_6(%rip), %ymm4, %ymm1
	vpshufb .Ltile4_encodeq_soa_mask_7(%rip), %ymm5, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 416(%rdi)
	vmovdqu 1216(%rsi), %ymm0
	vmovdqu 1088(%rsi), %ymm3
	vperm2i128 $32, %ymm3, %ymm0, %ymm4
	vperm2i128 $49, %ymm3, %ymm0, %ymm5
	vpshufb .Ltile4_encodeq_soa_mask_4(%rip), %ymm4, %ymm1
	vpshufb .Ltile4_encodeq_soa_mask_5(%rip), %ymm5, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 320(%rdi)
	vpshufb .Ltile4_encodeq_soa_mask_6(%rip), %ymm4, %ymm1
	vpshufb .Ltile4_encodeq_soa_mask_7(%rip), %ymm5, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 448(%rdi)
	vmovdqu 1248(%rsi), %ymm0
	vmovdqu 1120(%rsi), %ymm3
	vperm2i128 $32, %ymm3, %ymm0, %ymm4
	vperm2i128 $49, %ymm3, %ymm0, %ymm5
	vpshufb .Ltile4_encodeq_soa_mask_4(%rip), %ymm4, %ymm1
	vpshufb .Ltile4_encodeq_soa_mask_5(%rip), %ymm5, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 352(%rdi)
	vpshufb .Ltile4_encodeq_soa_mask_6(%rip), %ymm4, %ymm1
	vpshufb .Ltile4_encodeq_soa_mask_7(%rip), %ymm5, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 480(%rdi)
	vmovdqu 512(%rsi), %ymm0
	vmovdqu 640(%rsi), %ymm3
	vperm2i128 $32, %ymm3, %ymm0, %ymm4
	vperm2i128 $49, %ymm3, %ymm0, %ymm5
	vpshufb .Ltile4_encodeq_soa_mask_8(%rip), %ymm4, %ymm1
	vpshufb .Ltile4_encodeq_soa_mask_9(%rip), %ymm5, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 512(%rdi)
	vpshufb .Ltile4_encodeq_soa_mask_10(%rip), %ymm4, %ymm1
	vpshufb .Ltile4_encodeq_soa_mask_11(%rip), %ymm5, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 640(%rdi)
	vmovdqu 544(%rsi), %ymm0
	vmovdqu 672(%rsi), %ymm3
	vperm2i128 $32, %ymm3, %ymm0, %ymm4
	vperm2i128 $49, %ymm3, %ymm0, %ymm5
	vpshufb .Ltile4_encodeq_soa_mask_8(%rip), %ymm4, %ymm1
	vpshufb .Ltile4_encodeq_soa_mask_9(%rip), %ymm5, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 544(%rdi)
	vpshufb .Ltile4_encodeq_soa_mask_10(%rip), %ymm4, %ymm1
	vpshufb .Ltile4_encodeq_soa_mask_11(%rip), %ymm5, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 672(%rdi)
	vmovdqu 576(%rsi), %ymm0
	vmovdqu 704(%rsi), %ymm3
	vperm2i128 $32, %ymm3, %ymm0, %ymm4
	vperm2i128 $49, %ymm3, %ymm0, %ymm5
	vpshufb .Ltile4_encodeq_soa_mask_8(%rip), %ymm4, %ymm1
	vpshufb .Ltile4_encodeq_soa_mask_9(%rip), %ymm5, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 576(%rdi)
	vpshufb .Ltile4_encodeq_soa_mask_10(%rip), %ymm4, %ymm1
	vpshufb .Ltile4_encodeq_soa_mask_11(%rip), %ymm5, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 704(%rdi)
	vmovdqu 608(%rsi), %ymm0
	vmovdqu 736(%rsi), %ymm3
	vperm2i128 $32, %ymm3, %ymm0, %ymm4
	vperm2i128 $49, %ymm3, %ymm0, %ymm5
	vpshufb .Ltile4_encodeq_soa_mask_8(%rip), %ymm4, %ymm1
	vpshufb .Ltile4_encodeq_soa_mask_9(%rip), %ymm5, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 608(%rdi)
	vpshufb .Ltile4_encodeq_soa_mask_10(%rip), %ymm4, %ymm1
	vpshufb .Ltile4_encodeq_soa_mask_11(%rip), %ymm5, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 736(%rdi)
	vmovdqu 1408(%rsi), %ymm0
	vmovdqu 1280(%rsi), %ymm3
	vperm2i128 $32, %ymm3, %ymm0, %ymm4
	vperm2i128 $49, %ymm3, %ymm0, %ymm5
	vpshufb .Ltile4_encodeq_soa_mask_12(%rip), %ymm4, %ymm1
	vpshufb .Ltile4_encodeq_soa_mask_13(%rip), %ymm5, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 768(%rdi)
	vpshufb .Ltile4_encodeq_soa_mask_14(%rip), %ymm4, %ymm1
	vpshufb .Ltile4_encodeq_soa_mask_15(%rip), %ymm5, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 896(%rdi)
	vmovdqu 1440(%rsi), %ymm0
	vmovdqu 1312(%rsi), %ymm3
	vperm2i128 $32, %ymm3, %ymm0, %ymm4
	vperm2i128 $49, %ymm3, %ymm0, %ymm5
	vpshufb .Ltile4_encodeq_soa_mask_12(%rip), %ymm4, %ymm1
	vpshufb .Ltile4_encodeq_soa_mask_13(%rip), %ymm5, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 800(%rdi)
	vpshufb .Ltile4_encodeq_soa_mask_14(%rip), %ymm4, %ymm1
	vpshufb .Ltile4_encodeq_soa_mask_15(%rip), %ymm5, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 928(%rdi)
	vmovdqu 1472(%rsi), %ymm0
	vmovdqu 1344(%rsi), %ymm3
	vperm2i128 $32, %ymm3, %ymm0, %ymm4
	vperm2i128 $49, %ymm3, %ymm0, %ymm5
	vpshufb .Ltile4_encodeq_soa_mask_12(%rip), %ymm4, %ymm1
	vpshufb .Ltile4_encodeq_soa_mask_13(%rip), %ymm5, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 832(%rdi)
	vpshufb .Ltile4_encodeq_soa_mask_14(%rip), %ymm4, %ymm1
	vpshufb .Ltile4_encodeq_soa_mask_15(%rip), %ymm5, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 960(%rdi)
	vmovdqu 1504(%rsi), %ymm0
	vmovdqu 1376(%rsi), %ymm3
	vperm2i128 $32, %ymm3, %ymm0, %ymm4
	vperm2i128 $49, %ymm3, %ymm0, %ymm5
	vpshufb .Ltile4_encodeq_soa_mask_12(%rip), %ymm4, %ymm1
	vpshufb .Ltile4_encodeq_soa_mask_13(%rip), %ymm5, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 864(%rdi)
	vpshufb .Ltile4_encodeq_soa_mask_14(%rip), %ymm4, %ymm1
	vpshufb .Ltile4_encodeq_soa_mask_15(%rip), %ymm5, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 992(%rdi)
	vmovdqu 768(%rsi), %ymm0
	vmovdqu 896(%rsi), %ymm3
	vperm2i128 $32, %ymm3, %ymm0, %ymm4
	vperm2i128 $49, %ymm3, %ymm0, %ymm5
	vpshufb .Ltile4_encodeq_soa_mask_0(%rip), %ymm4, %ymm1
	vpshufb .Ltile4_encodeq_soa_mask_1(%rip), %ymm5, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 1024(%rdi)
	vpshufb .Ltile4_encodeq_soa_mask_2(%rip), %ymm4, %ymm1
	vpshufb .Ltile4_encodeq_soa_mask_3(%rip), %ymm5, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 1152(%rdi)
	vmovdqu 800(%rsi), %ymm0
	vmovdqu 928(%rsi), %ymm3
	vperm2i128 $32, %ymm3, %ymm0, %ymm4
	vperm2i128 $49, %ymm3, %ymm0, %ymm5
	vpshufb .Ltile4_encodeq_soa_mask_0(%rip), %ymm4, %ymm1
	vpshufb .Ltile4_encodeq_soa_mask_1(%rip), %ymm5, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 1056(%rdi)
	vpshufb .Ltile4_encodeq_soa_mask_2(%rip), %ymm4, %ymm1
	vpshufb .Ltile4_encodeq_soa_mask_3(%rip), %ymm5, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 1184(%rdi)
	vmovdqu 832(%rsi), %ymm0
	vmovdqu 960(%rsi), %ymm3
	vperm2i128 $32, %ymm3, %ymm0, %ymm4
	vperm2i128 $49, %ymm3, %ymm0, %ymm5
	vpshufb .Ltile4_encodeq_soa_mask_0(%rip), %ymm4, %ymm1
	vpshufb .Ltile4_encodeq_soa_mask_1(%rip), %ymm5, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 1088(%rdi)
	vpshufb .Ltile4_encodeq_soa_mask_2(%rip), %ymm4, %ymm1
	vpshufb .Ltile4_encodeq_soa_mask_3(%rip), %ymm5, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 1216(%rdi)
	vmovdqu 864(%rsi), %ymm0
	vmovdqu 992(%rsi), %ymm3
	vperm2i128 $32, %ymm3, %ymm0, %ymm4
	vperm2i128 $49, %ymm3, %ymm0, %ymm5
	vpshufb .Ltile4_encodeq_soa_mask_0(%rip), %ymm4, %ymm1
	vpshufb .Ltile4_encodeq_soa_mask_1(%rip), %ymm5, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 1120(%rdi)
	vpshufb .Ltile4_encodeq_soa_mask_2(%rip), %ymm4, %ymm1
	vpshufb .Ltile4_encodeq_soa_mask_3(%rip), %ymm5, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 1248(%rdi)
	vmovdqu 384(%rsi), %ymm0
	vmovdqu 256(%rsi), %ymm3
	vperm2i128 $32, %ymm3, %ymm0, %ymm4
	vperm2i128 $49, %ymm3, %ymm0, %ymm5
	vpshufb .Ltile4_encodeq_soa_mask_4(%rip), %ymm4, %ymm1
	vpshufb .Ltile4_encodeq_soa_mask_5(%rip), %ymm5, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 1280(%rdi)
	vpshufb .Ltile4_encodeq_soa_mask_6(%rip), %ymm4, %ymm1
	vpshufb .Ltile4_encodeq_soa_mask_7(%rip), %ymm5, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 1408(%rdi)
	vmovdqu 416(%rsi), %ymm0
	vmovdqu 288(%rsi), %ymm3
	vperm2i128 $32, %ymm3, %ymm0, %ymm4
	vperm2i128 $49, %ymm3, %ymm0, %ymm5
	vpshufb .Ltile4_encodeq_soa_mask_4(%rip), %ymm4, %ymm1
	vpshufb .Ltile4_encodeq_soa_mask_5(%rip), %ymm5, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 1312(%rdi)
	vpshufb .Ltile4_encodeq_soa_mask_6(%rip), %ymm4, %ymm1
	vpshufb .Ltile4_encodeq_soa_mask_7(%rip), %ymm5, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 1440(%rdi)
	vmovdqu 448(%rsi), %ymm0
	vmovdqu 320(%rsi), %ymm3
	vperm2i128 $32, %ymm3, %ymm0, %ymm4
	vperm2i128 $49, %ymm3, %ymm0, %ymm5
	vpshufb .Ltile4_encodeq_soa_mask_4(%rip), %ymm4, %ymm1
	vpshufb .Ltile4_encodeq_soa_mask_5(%rip), %ymm5, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 1344(%rdi)
	vpshufb .Ltile4_encodeq_soa_mask_6(%rip), %ymm4, %ymm1
	vpshufb .Ltile4_encodeq_soa_mask_7(%rip), %ymm5, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 1472(%rdi)
	vmovdqu 480(%rsi), %ymm0
	vmovdqu 352(%rsi), %ymm3
	vperm2i128 $32, %ymm3, %ymm0, %ymm4
	vperm2i128 $49, %ymm3, %ymm0, %ymm5
	vpshufb .Ltile4_encodeq_soa_mask_4(%rip), %ymm4, %ymm1
	vpshufb .Ltile4_encodeq_soa_mask_5(%rip), %ymm5, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 1376(%rdi)
	vpshufb .Ltile4_encodeq_soa_mask_6(%rip), %ymm4, %ymm1
	vpshufb .Ltile4_encodeq_soa_mask_7(%rip), %ymm5, %ymm2
	vpor %ymm2, %ymm1, %ymm1
	vmovdqu %ymm1, 1504(%rdi)
	.endm

	.macro TILE4_SOA_TO_OFFICIAL_PACK_BLOCK_0
	vmovdqu 0(%rsi), %ymm8
	vmovdqu 128(%rsi), %ymm9
	vperm2i128 $32, %ymm9, %ymm8, %ymm10
	vperm2i128 $49, %ymm9, %ymm8, %ymm11
	vpshufb .Ltile4_encodeq_soa_mask_0(%rip), %ymm10, %ymm12
	vpshufb .Ltile4_encodeq_soa_mask_1(%rip), %ymm11, %ymm13
	vpor %ymm13, %ymm12, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_2(%rip), %ymm10, %ymm12
	vpshufb .Ltile4_encodeq_soa_mask_3(%rip), %ymm11, %ymm13
	vpor %ymm13, %ymm12, %ymm4
	vmovdqu 32(%rsi), %ymm8
	vmovdqu 160(%rsi), %ymm9
	vperm2i128 $32, %ymm9, %ymm8, %ymm10
	vperm2i128 $49, %ymm9, %ymm8, %ymm11
	vpshufb .Ltile4_encodeq_soa_mask_0(%rip), %ymm10, %ymm12
	vpshufb .Ltile4_encodeq_soa_mask_1(%rip), %ymm11, %ymm13
	vpor %ymm13, %ymm12, %ymm1
	vpshufb .Ltile4_encodeq_soa_mask_2(%rip), %ymm10, %ymm12
	vpshufb .Ltile4_encodeq_soa_mask_3(%rip), %ymm11, %ymm13
	vpor %ymm13, %ymm12, %ymm5
	vmovdqu 64(%rsi), %ymm8
	vmovdqu 192(%rsi), %ymm9
	vperm2i128 $32, %ymm9, %ymm8, %ymm10
	vperm2i128 $49, %ymm9, %ymm8, %ymm11
	vpshufb .Ltile4_encodeq_soa_mask_0(%rip), %ymm10, %ymm12
	vpshufb .Ltile4_encodeq_soa_mask_1(%rip), %ymm11, %ymm13
	vpor %ymm13, %ymm12, %ymm2
	vpshufb .Ltile4_encodeq_soa_mask_2(%rip), %ymm10, %ymm12
	vpshufb .Ltile4_encodeq_soa_mask_3(%rip), %ymm11, %ymm13
	vpor %ymm13, %ymm12, %ymm6
	vmovdqu 96(%rsi), %ymm8
	vmovdqu 224(%rsi), %ymm9
	vperm2i128 $32, %ymm9, %ymm8, %ymm10
	vperm2i128 $49, %ymm9, %ymm8, %ymm11
	vpshufb .Ltile4_encodeq_soa_mask_0(%rip), %ymm10, %ymm12
	vpshufb .Ltile4_encodeq_soa_mask_1(%rip), %ymm11, %ymm13
	vpor %ymm13, %ymm12, %ymm3
	vpshufb .Ltile4_encodeq_soa_mask_2(%rip), %ymm10, %ymm12
	vpshufb .Ltile4_encodeq_soa_mask_3(%rip), %ymm11, %ymm13
	vpor %ymm13, %ymm12, %ymm7
	.endm

	.macro TILE4_SOA_TO_OFFICIAL_PACK_BLOCK_1
	vmovdqu 1152(%rsi), %ymm8
	vmovdqu 1024(%rsi), %ymm9
	vperm2i128 $32, %ymm9, %ymm8, %ymm10
	vperm2i128 $49, %ymm9, %ymm8, %ymm11
	vpshufb .Ltile4_encodeq_soa_mask_4(%rip), %ymm10, %ymm12
	vpshufb .Ltile4_encodeq_soa_mask_5(%rip), %ymm11, %ymm13
	vpor %ymm13, %ymm12, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_6(%rip), %ymm10, %ymm12
	vpshufb .Ltile4_encodeq_soa_mask_7(%rip), %ymm11, %ymm13
	vpor %ymm13, %ymm12, %ymm4
	vmovdqu 1184(%rsi), %ymm8
	vmovdqu 1056(%rsi), %ymm9
	vperm2i128 $32, %ymm9, %ymm8, %ymm10
	vperm2i128 $49, %ymm9, %ymm8, %ymm11
	vpshufb .Ltile4_encodeq_soa_mask_4(%rip), %ymm10, %ymm12
	vpshufb .Ltile4_encodeq_soa_mask_5(%rip), %ymm11, %ymm13
	vpor %ymm13, %ymm12, %ymm1
	vpshufb .Ltile4_encodeq_soa_mask_6(%rip), %ymm10, %ymm12
	vpshufb .Ltile4_encodeq_soa_mask_7(%rip), %ymm11, %ymm13
	vpor %ymm13, %ymm12, %ymm5
	vmovdqu 1216(%rsi), %ymm8
	vmovdqu 1088(%rsi), %ymm9
	vperm2i128 $32, %ymm9, %ymm8, %ymm10
	vperm2i128 $49, %ymm9, %ymm8, %ymm11
	vpshufb .Ltile4_encodeq_soa_mask_4(%rip), %ymm10, %ymm12
	vpshufb .Ltile4_encodeq_soa_mask_5(%rip), %ymm11, %ymm13
	vpor %ymm13, %ymm12, %ymm2
	vpshufb .Ltile4_encodeq_soa_mask_6(%rip), %ymm10, %ymm12
	vpshufb .Ltile4_encodeq_soa_mask_7(%rip), %ymm11, %ymm13
	vpor %ymm13, %ymm12, %ymm6
	vmovdqu 1248(%rsi), %ymm8
	vmovdqu 1120(%rsi), %ymm9
	vperm2i128 $32, %ymm9, %ymm8, %ymm10
	vperm2i128 $49, %ymm9, %ymm8, %ymm11
	vpshufb .Ltile4_encodeq_soa_mask_4(%rip), %ymm10, %ymm12
	vpshufb .Ltile4_encodeq_soa_mask_5(%rip), %ymm11, %ymm13
	vpor %ymm13, %ymm12, %ymm3
	vpshufb .Ltile4_encodeq_soa_mask_6(%rip), %ymm10, %ymm12
	vpshufb .Ltile4_encodeq_soa_mask_7(%rip), %ymm11, %ymm13
	vpor %ymm13, %ymm12, %ymm7
	.endm

	.macro TILE4_SOA_TO_OFFICIAL_PACK_BLOCK_2
	vmovdqu 512(%rsi), %ymm8
	vmovdqu 640(%rsi), %ymm9
	vperm2i128 $32, %ymm9, %ymm8, %ymm10
	vperm2i128 $49, %ymm9, %ymm8, %ymm11
	vpshufb .Ltile4_encodeq_soa_mask_8(%rip), %ymm10, %ymm12
	vpshufb .Ltile4_encodeq_soa_mask_9(%rip), %ymm11, %ymm13
	vpor %ymm13, %ymm12, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_10(%rip), %ymm10, %ymm12
	vpshufb .Ltile4_encodeq_soa_mask_11(%rip), %ymm11, %ymm13
	vpor %ymm13, %ymm12, %ymm4
	vmovdqu 544(%rsi), %ymm8
	vmovdqu 672(%rsi), %ymm9
	vperm2i128 $32, %ymm9, %ymm8, %ymm10
	vperm2i128 $49, %ymm9, %ymm8, %ymm11
	vpshufb .Ltile4_encodeq_soa_mask_8(%rip), %ymm10, %ymm12
	vpshufb .Ltile4_encodeq_soa_mask_9(%rip), %ymm11, %ymm13
	vpor %ymm13, %ymm12, %ymm1
	vpshufb .Ltile4_encodeq_soa_mask_10(%rip), %ymm10, %ymm12
	vpshufb .Ltile4_encodeq_soa_mask_11(%rip), %ymm11, %ymm13
	vpor %ymm13, %ymm12, %ymm5
	vmovdqu 576(%rsi), %ymm8
	vmovdqu 704(%rsi), %ymm9
	vperm2i128 $32, %ymm9, %ymm8, %ymm10
	vperm2i128 $49, %ymm9, %ymm8, %ymm11
	vpshufb .Ltile4_encodeq_soa_mask_8(%rip), %ymm10, %ymm12
	vpshufb .Ltile4_encodeq_soa_mask_9(%rip), %ymm11, %ymm13
	vpor %ymm13, %ymm12, %ymm2
	vpshufb .Ltile4_encodeq_soa_mask_10(%rip), %ymm10, %ymm12
	vpshufb .Ltile4_encodeq_soa_mask_11(%rip), %ymm11, %ymm13
	vpor %ymm13, %ymm12, %ymm6
	vmovdqu 608(%rsi), %ymm8
	vmovdqu 736(%rsi), %ymm9
	vperm2i128 $32, %ymm9, %ymm8, %ymm10
	vperm2i128 $49, %ymm9, %ymm8, %ymm11
	vpshufb .Ltile4_encodeq_soa_mask_8(%rip), %ymm10, %ymm12
	vpshufb .Ltile4_encodeq_soa_mask_9(%rip), %ymm11, %ymm13
	vpor %ymm13, %ymm12, %ymm3
	vpshufb .Ltile4_encodeq_soa_mask_10(%rip), %ymm10, %ymm12
	vpshufb .Ltile4_encodeq_soa_mask_11(%rip), %ymm11, %ymm13
	vpor %ymm13, %ymm12, %ymm7
	.endm

	.macro TILE4_SOA_TO_OFFICIAL_PACK_BLOCK_3
	vmovdqu 1408(%rsi), %ymm8
	vmovdqu 1280(%rsi), %ymm9
	vperm2i128 $32, %ymm9, %ymm8, %ymm10
	vperm2i128 $49, %ymm9, %ymm8, %ymm11
	vpshufb .Ltile4_encodeq_soa_mask_12(%rip), %ymm10, %ymm12
	vpshufb .Ltile4_encodeq_soa_mask_13(%rip), %ymm11, %ymm13
	vpor %ymm13, %ymm12, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_14(%rip), %ymm10, %ymm12
	vpshufb .Ltile4_encodeq_soa_mask_15(%rip), %ymm11, %ymm13
	vpor %ymm13, %ymm12, %ymm4
	vmovdqu 1440(%rsi), %ymm8
	vmovdqu 1312(%rsi), %ymm9
	vperm2i128 $32, %ymm9, %ymm8, %ymm10
	vperm2i128 $49, %ymm9, %ymm8, %ymm11
	vpshufb .Ltile4_encodeq_soa_mask_12(%rip), %ymm10, %ymm12
	vpshufb .Ltile4_encodeq_soa_mask_13(%rip), %ymm11, %ymm13
	vpor %ymm13, %ymm12, %ymm1
	vpshufb .Ltile4_encodeq_soa_mask_14(%rip), %ymm10, %ymm12
	vpshufb .Ltile4_encodeq_soa_mask_15(%rip), %ymm11, %ymm13
	vpor %ymm13, %ymm12, %ymm5
	vmovdqu 1472(%rsi), %ymm8
	vmovdqu 1344(%rsi), %ymm9
	vperm2i128 $32, %ymm9, %ymm8, %ymm10
	vperm2i128 $49, %ymm9, %ymm8, %ymm11
	vpshufb .Ltile4_encodeq_soa_mask_12(%rip), %ymm10, %ymm12
	vpshufb .Ltile4_encodeq_soa_mask_13(%rip), %ymm11, %ymm13
	vpor %ymm13, %ymm12, %ymm2
	vpshufb .Ltile4_encodeq_soa_mask_14(%rip), %ymm10, %ymm12
	vpshufb .Ltile4_encodeq_soa_mask_15(%rip), %ymm11, %ymm13
	vpor %ymm13, %ymm12, %ymm6
	vmovdqu 1504(%rsi), %ymm8
	vmovdqu 1376(%rsi), %ymm9
	vperm2i128 $32, %ymm9, %ymm8, %ymm10
	vperm2i128 $49, %ymm9, %ymm8, %ymm11
	vpshufb .Ltile4_encodeq_soa_mask_12(%rip), %ymm10, %ymm12
	vpshufb .Ltile4_encodeq_soa_mask_13(%rip), %ymm11, %ymm13
	vpor %ymm13, %ymm12, %ymm3
	vpshufb .Ltile4_encodeq_soa_mask_14(%rip), %ymm10, %ymm12
	vpshufb .Ltile4_encodeq_soa_mask_15(%rip), %ymm11, %ymm13
	vpor %ymm13, %ymm12, %ymm7
	.endm

	.macro TILE4_SOA_TO_OFFICIAL_PACK_BLOCK_4
	vmovdqu 768(%rsi), %ymm8
	vmovdqu 896(%rsi), %ymm9
	vperm2i128 $32, %ymm9, %ymm8, %ymm10
	vperm2i128 $49, %ymm9, %ymm8, %ymm11
	vpshufb .Ltile4_encodeq_soa_mask_0(%rip), %ymm10, %ymm12
	vpshufb .Ltile4_encodeq_soa_mask_1(%rip), %ymm11, %ymm13
	vpor %ymm13, %ymm12, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_2(%rip), %ymm10, %ymm12
	vpshufb .Ltile4_encodeq_soa_mask_3(%rip), %ymm11, %ymm13
	vpor %ymm13, %ymm12, %ymm4
	vmovdqu 800(%rsi), %ymm8
	vmovdqu 928(%rsi), %ymm9
	vperm2i128 $32, %ymm9, %ymm8, %ymm10
	vperm2i128 $49, %ymm9, %ymm8, %ymm11
	vpshufb .Ltile4_encodeq_soa_mask_0(%rip), %ymm10, %ymm12
	vpshufb .Ltile4_encodeq_soa_mask_1(%rip), %ymm11, %ymm13
	vpor %ymm13, %ymm12, %ymm1
	vpshufb .Ltile4_encodeq_soa_mask_2(%rip), %ymm10, %ymm12
	vpshufb .Ltile4_encodeq_soa_mask_3(%rip), %ymm11, %ymm13
	vpor %ymm13, %ymm12, %ymm5
	vmovdqu 832(%rsi), %ymm8
	vmovdqu 960(%rsi), %ymm9
	vperm2i128 $32, %ymm9, %ymm8, %ymm10
	vperm2i128 $49, %ymm9, %ymm8, %ymm11
	vpshufb .Ltile4_encodeq_soa_mask_0(%rip), %ymm10, %ymm12
	vpshufb .Ltile4_encodeq_soa_mask_1(%rip), %ymm11, %ymm13
	vpor %ymm13, %ymm12, %ymm2
	vpshufb .Ltile4_encodeq_soa_mask_2(%rip), %ymm10, %ymm12
	vpshufb .Ltile4_encodeq_soa_mask_3(%rip), %ymm11, %ymm13
	vpor %ymm13, %ymm12, %ymm6
	vmovdqu 864(%rsi), %ymm8
	vmovdqu 992(%rsi), %ymm9
	vperm2i128 $32, %ymm9, %ymm8, %ymm10
	vperm2i128 $49, %ymm9, %ymm8, %ymm11
	vpshufb .Ltile4_encodeq_soa_mask_0(%rip), %ymm10, %ymm12
	vpshufb .Ltile4_encodeq_soa_mask_1(%rip), %ymm11, %ymm13
	vpor %ymm13, %ymm12, %ymm3
	vpshufb .Ltile4_encodeq_soa_mask_2(%rip), %ymm10, %ymm12
	vpshufb .Ltile4_encodeq_soa_mask_3(%rip), %ymm11, %ymm13
	vpor %ymm13, %ymm12, %ymm7
	.endm

	.macro TILE4_SOA_TO_OFFICIAL_PACK_BLOCK_5
	vmovdqu 384(%rsi), %ymm8
	vmovdqu 256(%rsi), %ymm9
	vperm2i128 $32, %ymm9, %ymm8, %ymm10
	vperm2i128 $49, %ymm9, %ymm8, %ymm11
	vpshufb .Ltile4_encodeq_soa_mask_4(%rip), %ymm10, %ymm12
	vpshufb .Ltile4_encodeq_soa_mask_5(%rip), %ymm11, %ymm13
	vpor %ymm13, %ymm12, %ymm0
	vpshufb .Ltile4_encodeq_soa_mask_6(%rip), %ymm10, %ymm12
	vpshufb .Ltile4_encodeq_soa_mask_7(%rip), %ymm11, %ymm13
	vpor %ymm13, %ymm12, %ymm4
	vmovdqu 416(%rsi), %ymm8
	vmovdqu 288(%rsi), %ymm9
	vperm2i128 $32, %ymm9, %ymm8, %ymm10
	vperm2i128 $49, %ymm9, %ymm8, %ymm11
	vpshufb .Ltile4_encodeq_soa_mask_4(%rip), %ymm10, %ymm12
	vpshufb .Ltile4_encodeq_soa_mask_5(%rip), %ymm11, %ymm13
	vpor %ymm13, %ymm12, %ymm1
	vpshufb .Ltile4_encodeq_soa_mask_6(%rip), %ymm10, %ymm12
	vpshufb .Ltile4_encodeq_soa_mask_7(%rip), %ymm11, %ymm13
	vpor %ymm13, %ymm12, %ymm5
	vmovdqu 448(%rsi), %ymm8
	vmovdqu 320(%rsi), %ymm9
	vperm2i128 $32, %ymm9, %ymm8, %ymm10
	vperm2i128 $49, %ymm9, %ymm8, %ymm11
	vpshufb .Ltile4_encodeq_soa_mask_4(%rip), %ymm10, %ymm12
	vpshufb .Ltile4_encodeq_soa_mask_5(%rip), %ymm11, %ymm13
	vpor %ymm13, %ymm12, %ymm2
	vpshufb .Ltile4_encodeq_soa_mask_6(%rip), %ymm10, %ymm12
	vpshufb .Ltile4_encodeq_soa_mask_7(%rip), %ymm11, %ymm13
	vpor %ymm13, %ymm12, %ymm6
	vmovdqu 480(%rsi), %ymm8
	vmovdqu 352(%rsi), %ymm9
	vperm2i128 $32, %ymm9, %ymm8, %ymm10
	vperm2i128 $49, %ymm9, %ymm8, %ymm11
	vpshufb .Ltile4_encodeq_soa_mask_4(%rip), %ymm10, %ymm12
	vpshufb .Ltile4_encodeq_soa_mask_5(%rip), %ymm11, %ymm13
	vpor %ymm13, %ymm12, %ymm3
	vpshufb .Ltile4_encodeq_soa_mask_6(%rip), %ymm10, %ymm12
	vpshufb .Ltile4_encodeq_soa_mask_7(%rip), %ymm11, %ymm13
	vpor %ymm13, %ymm12, %ymm7
	.endm

	.pushsection .rodata
	.p2align 5
.Ltile4_encodeq_soa_mask_0:
	.byte 14,15,128,128,128,128,4,5,128,128,0,1,128,128,2,3,14,15,128,128,128,128,4,5,128,128,0,1,128,128,2,3
	.p2align 5
.Ltile4_encodeq_soa_mask_1:
	.byte 128,128,14,15,12,13,128,128,8,9,128,128,10,11,128,128,128,128,14,15,12,13,128,128,8,9,128,128,10,11,128,128
	.p2align 5
.Ltile4_encodeq_soa_mask_2:
	.byte 6,7,128,128,128,128,12,13,128,128,8,9,128,128,10,11,6,7,128,128,128,128,12,13,128,128,8,9,128,128,10,11
	.p2align 5
.Ltile4_encodeq_soa_mask_3:
	.byte 128,128,6,7,4,5,128,128,0,1,128,128,2,3,128,128,128,128,6,7,4,5,128,128,0,1,128,128,2,3,128,128
	.p2align 5
.Ltile4_encodeq_soa_mask_4:
	.byte 0,1,128,128,2,3,128,128,4,5,128,128,6,7,128,128,4,5,128,128,6,7,128,128,2,3,128,128,128,128,8,9
	.p2align 5
.Ltile4_encodeq_soa_mask_5:
	.byte 128,128,0,1,128,128,2,3,128,128,4,5,128,128,6,7,128,128,4,5,128,128,6,7,128,128,2,3,0,1,128,128
	.p2align 5
.Ltile4_encodeq_soa_mask_6:
	.byte 8,9,128,128,10,11,128,128,12,13,128,128,14,15,128,128,12,13,128,128,14,15,128,128,10,11,128,128,128,128,0,1
	.p2align 5
.Ltile4_encodeq_soa_mask_7:
	.byte 128,128,8,9,128,128,10,11,128,128,12,13,128,128,14,15,128,128,12,13,128,128,14,15,128,128,10,11,8,9,128,128
	.p2align 5
.Ltile4_encodeq_soa_mask_8:
	.byte 128,128,10,11,8,9,128,128,128,128,14,15,12,13,128,128,128,128,10,11,8,9,128,128,128,128,14,15,12,13,128,128
	.p2align 5
.Ltile4_encodeq_soa_mask_9:
	.byte 2,3,128,128,128,128,8,9,6,7,128,128,128,128,12,13,2,3,128,128,128,128,8,9,6,7,128,128,128,128,12,13
	.p2align 5
.Ltile4_encodeq_soa_mask_10:
	.byte 128,128,2,3,0,1,128,128,128,128,6,7,4,5,128,128,128,128,2,3,0,1,128,128,128,128,6,7,4,5,128,128
	.p2align 5
.Ltile4_encodeq_soa_mask_11:
	.byte 10,11,128,128,128,128,0,1,14,15,128,128,128,128,4,5,10,11,128,128,128,128,0,1,14,15,128,128,128,128,4,5
	.p2align 5
.Ltile4_encodeq_soa_mask_12:
	.byte 128,128,12,13,128,128,14,15,128,128,10,11,8,9,128,128,128,128,10,11,8,9,128,128,128,128,14,15,12,13,128,128
	.p2align 5
.Ltile4_encodeq_soa_mask_13:
	.byte 4,5,128,128,6,7,128,128,2,3,128,128,128,128,8,9,2,3,128,128,128,128,8,9,6,7,128,128,128,128,12,13
	.p2align 5
.Ltile4_encodeq_soa_mask_14:
	.byte 128,128,4,5,128,128,6,7,128,128,2,3,0,1,128,128,128,128,2,3,0,1,128,128,128,128,6,7,4,5,128,128
	.p2align 5
.Ltile4_encodeq_soa_mask_15:
	.byte 12,13,128,128,14,15,128,128,10,11,128,128,128,128,0,1,10,11,128,128,128,128,0,1,14,15,128,128,128,128,4,5
	.popsection
