	.macro TILE4_STORE_AOS_CHUNK_0
	vmovq %xmm11, 0(%rdi)
	vpextrq $1, %xmm11, 1112(%rdi)
	vextracti128 $1, %ymm11, %xmm6
	vmovq %xmm6, 688(%rdi)
	vpextrq $1, %xmm6, 8(%rdi)
	vmovq %xmm12, 1120(%rdi)
	vpextrq $1, %xmm12, 696(%rdi)
	vextracti128 $1, %ymm12, %xmm6
	vmovq %xmm6, 16(%rdi)
	vpextrq $1, %xmm6, 1128(%rdi)
	vmovq %xmm13, 704(%rdi)
	vpextrq $1, %xmm13, 24(%rdi)
	vextracti128 $1, %ymm13, %xmm6
	vmovq %xmm6, 1136(%rdi)
	vpextrq $1, %xmm6, 712(%rdi)
	vmovq %xmm14, 32(%rdi)
	vpextrq $1, %xmm14, 1144(%rdi)
	vextracti128 $1, %ymm14, %xmm6
	vmovq %xmm6, 720(%rdi)
	vpextrq $1, %xmm6, 40(%rdi)
	vmovq %xmm7, 1152(%rdi)
	vpextrq $1, %xmm7, 728(%rdi)
	vextracti128 $1, %ymm7, %xmm6
	vmovq %xmm6, 48(%rdi)
	vpextrq $1, %xmm6, 1160(%rdi)
	vmovq %xmm8, 736(%rdi)
	vpextrq $1, %xmm8, 56(%rdi)
	vextracti128 $1, %ymm8, %xmm6
	vmovq %xmm6, 1168(%rdi)
	vpextrq $1, %xmm6, 744(%rdi)
	vmovq %xmm9, 64(%rdi)
	vpextrq $1, %xmm9, 1176(%rdi)
	vextracti128 $1, %ymm9, %xmm6
	vmovq %xmm6, 752(%rdi)
	vpextrq $1, %xmm6, 72(%rdi)
	vmovq %xmm10, 1184(%rdi)
	vpextrq $1, %xmm10, 760(%rdi)
	vextracti128 $1, %ymm10, %xmm6
	vmovq %xmm6, 80(%rdi)
	vpextrq $1, %xmm6, 1192(%rdi)
	.endm

	.macro TILE4_STORE_AOS_CHUNK_1
	vmovq %xmm11, 512(%rdi)
	vpextrq $1, %xmm11, 88(%rdi)
	vextracti128 $1, %ymm11, %xmm6
	vmovq %xmm6, 1200(%rdi)
	vpextrq $1, %xmm6, 520(%rdi)
	vmovq %xmm12, 96(%rdi)
	vpextrq $1, %xmm12, 1208(%rdi)
	vextracti128 $1, %ymm12, %xmm6
	vmovq %xmm6, 528(%rdi)
	vpextrq $1, %xmm6, 104(%rdi)
	vmovq %xmm13, 1216(%rdi)
	vpextrq $1, %xmm13, 536(%rdi)
	vextracti128 $1, %ymm13, %xmm6
	vmovq %xmm6, 112(%rdi)
	vpextrq $1, %xmm6, 1224(%rdi)
	vmovq %xmm14, 544(%rdi)
	vpextrq $1, %xmm14, 120(%rdi)
	vextracti128 $1, %ymm14, %xmm6
	vmovq %xmm6, 1232(%rdi)
	vpextrq $1, %xmm6, 552(%rdi)
	vmovq %xmm7, 128(%rdi)
	vpextrq $1, %xmm7, 1240(%rdi)
	vextracti128 $1, %ymm7, %xmm6
	vmovq %xmm6, 560(%rdi)
	vpextrq $1, %xmm6, 136(%rdi)
	vmovq %xmm8, 1248(%rdi)
	vpextrq $1, %xmm8, 568(%rdi)
	vextracti128 $1, %ymm8, %xmm6
	vmovq %xmm6, 144(%rdi)
	vpextrq $1, %xmm6, 1256(%rdi)
	vmovq %xmm9, 576(%rdi)
	vpextrq $1, %xmm9, 152(%rdi)
	vextracti128 $1, %ymm9, %xmm6
	vmovq %xmm6, 1264(%rdi)
	vpextrq $1, %xmm6, 584(%rdi)
	vmovq %xmm10, 160(%rdi)
	vpextrq $1, %xmm10, 1272(%rdi)
	vextracti128 $1, %ymm10, %xmm6
	vmovq %xmm6, 592(%rdi)
	vpextrq $1, %xmm6, 168(%rdi)
	.endm

	.macro TILE4_STORE_AOS_CHUNK_2
	vmovq %xmm11, 1024(%rdi)
	vpextrq $1, %xmm11, 600(%rdi)
	vextracti128 $1, %ymm11, %xmm6
	vmovq %xmm6, 176(%rdi)
	vpextrq $1, %xmm6, 1032(%rdi)
	vmovq %xmm12, 608(%rdi)
	vpextrq $1, %xmm12, 184(%rdi)
	vextracti128 $1, %ymm12, %xmm6
	vmovq %xmm6, 1040(%rdi)
	vpextrq $1, %xmm6, 616(%rdi)
	vmovq %xmm13, 192(%rdi)
	vpextrq $1, %xmm13, 1048(%rdi)
	vextracti128 $1, %ymm13, %xmm6
	vmovq %xmm6, 624(%rdi)
	vpextrq $1, %xmm6, 200(%rdi)
	vmovq %xmm14, 1056(%rdi)
	vpextrq $1, %xmm14, 632(%rdi)
	vextracti128 $1, %ymm14, %xmm6
	vmovq %xmm6, 208(%rdi)
	vpextrq $1, %xmm6, 1064(%rdi)
	vmovq %xmm7, 640(%rdi)
	vpextrq $1, %xmm7, 216(%rdi)
	vextracti128 $1, %ymm7, %xmm6
	vmovq %xmm6, 1072(%rdi)
	vpextrq $1, %xmm6, 648(%rdi)
	vmovq %xmm8, 224(%rdi)
	vpextrq $1, %xmm8, 1080(%rdi)
	vextracti128 $1, %ymm8, %xmm6
	vmovq %xmm6, 656(%rdi)
	vpextrq $1, %xmm6, 232(%rdi)
	vmovq %xmm9, 1088(%rdi)
	vpextrq $1, %xmm9, 664(%rdi)
	vextracti128 $1, %ymm9, %xmm6
	vmovq %xmm6, 240(%rdi)
	vpextrq $1, %xmm6, 1096(%rdi)
	vmovq %xmm10, 672(%rdi)
	vpextrq $1, %xmm10, 248(%rdi)
	vextracti128 $1, %ymm10, %xmm6
	vmovq %xmm6, 1104(%rdi)
	vpextrq $1, %xmm6, 680(%rdi)
	.endm

	.macro TILE4_STORE_AOS_CHUNK_3
	vmovq %xmm11, 256(%rdi)
	vpextrq $1, %xmm11, 1368(%rdi)
	vextracti128 $1, %ymm11, %xmm6
	vmovq %xmm6, 944(%rdi)
	vpextrq $1, %xmm6, 264(%rdi)
	vmovq %xmm12, 1376(%rdi)
	vpextrq $1, %xmm12, 952(%rdi)
	vextracti128 $1, %ymm12, %xmm6
	vmovq %xmm6, 272(%rdi)
	vpextrq $1, %xmm6, 1384(%rdi)
	vmovq %xmm13, 960(%rdi)
	vpextrq $1, %xmm13, 280(%rdi)
	vextracti128 $1, %ymm13, %xmm6
	vmovq %xmm6, 1392(%rdi)
	vpextrq $1, %xmm6, 968(%rdi)
	vmovq %xmm14, 288(%rdi)
	vpextrq $1, %xmm14, 1400(%rdi)
	vextracti128 $1, %ymm14, %xmm6
	vmovq %xmm6, 976(%rdi)
	vpextrq $1, %xmm6, 296(%rdi)
	vmovq %xmm7, 1408(%rdi)
	vpextrq $1, %xmm7, 984(%rdi)
	vextracti128 $1, %ymm7, %xmm6
	vmovq %xmm6, 304(%rdi)
	vpextrq $1, %xmm6, 1416(%rdi)
	vmovq %xmm8, 992(%rdi)
	vpextrq $1, %xmm8, 312(%rdi)
	vextracti128 $1, %ymm8, %xmm6
	vmovq %xmm6, 1424(%rdi)
	vpextrq $1, %xmm6, 1000(%rdi)
	vmovq %xmm9, 320(%rdi)
	vpextrq $1, %xmm9, 1432(%rdi)
	vextracti128 $1, %ymm9, %xmm6
	vmovq %xmm6, 1008(%rdi)
	vpextrq $1, %xmm6, 328(%rdi)
	vmovq %xmm10, 1440(%rdi)
	vpextrq $1, %xmm10, 1016(%rdi)
	vextracti128 $1, %ymm10, %xmm6
	vmovq %xmm6, 336(%rdi)
	vpextrq $1, %xmm6, 1448(%rdi)
	.endm

	.macro TILE4_STORE_AOS_CHUNK_4
	vmovq %xmm11, 768(%rdi)
	vpextrq $1, %xmm11, 344(%rdi)
	vextracti128 $1, %ymm11, %xmm6
	vmovq %xmm6, 1456(%rdi)
	vpextrq $1, %xmm6, 776(%rdi)
	vmovq %xmm12, 352(%rdi)
	vpextrq $1, %xmm12, 1464(%rdi)
	vextracti128 $1, %ymm12, %xmm6
	vmovq %xmm6, 784(%rdi)
	vpextrq $1, %xmm6, 360(%rdi)
	vmovq %xmm13, 1472(%rdi)
	vpextrq $1, %xmm13, 792(%rdi)
	vextracti128 $1, %ymm13, %xmm6
	vmovq %xmm6, 368(%rdi)
	vpextrq $1, %xmm6, 1480(%rdi)
	vmovq %xmm14, 800(%rdi)
	vpextrq $1, %xmm14, 376(%rdi)
	vextracti128 $1, %ymm14, %xmm6
	vmovq %xmm6, 1488(%rdi)
	vpextrq $1, %xmm6, 808(%rdi)
	vmovq %xmm7, 384(%rdi)
	vpextrq $1, %xmm7, 1496(%rdi)
	vextracti128 $1, %ymm7, %xmm6
	vmovq %xmm6, 816(%rdi)
	vpextrq $1, %xmm6, 392(%rdi)
	vmovq %xmm8, 1504(%rdi)
	vpextrq $1, %xmm8, 824(%rdi)
	vextracti128 $1, %ymm8, %xmm6
	vmovq %xmm6, 400(%rdi)
	vpextrq $1, %xmm6, 1512(%rdi)
	vmovq %xmm9, 832(%rdi)
	vpextrq $1, %xmm9, 408(%rdi)
	vextracti128 $1, %ymm9, %xmm6
	vmovq %xmm6, 1520(%rdi)
	vpextrq $1, %xmm6, 840(%rdi)
	vmovq %xmm10, 416(%rdi)
	vpextrq $1, %xmm10, 1528(%rdi)
	vextracti128 $1, %ymm10, %xmm6
	vmovq %xmm6, 848(%rdi)
	vpextrq $1, %xmm6, 424(%rdi)
	.endm

	.macro TILE4_STORE_AOS_CHUNK_5
	vmovq %xmm11, 1280(%rdi)
	vpextrq $1, %xmm11, 856(%rdi)
	vextracti128 $1, %ymm11, %xmm6
	vmovq %xmm6, 432(%rdi)
	vpextrq $1, %xmm6, 1288(%rdi)
	vmovq %xmm12, 864(%rdi)
	vpextrq $1, %xmm12, 440(%rdi)
	vextracti128 $1, %ymm12, %xmm6
	vmovq %xmm6, 1296(%rdi)
	vpextrq $1, %xmm6, 872(%rdi)
	vmovq %xmm13, 448(%rdi)
	vpextrq $1, %xmm13, 1304(%rdi)
	vextracti128 $1, %ymm13, %xmm6
	vmovq %xmm6, 880(%rdi)
	vpextrq $1, %xmm6, 456(%rdi)
	vmovq %xmm14, 1312(%rdi)
	vpextrq $1, %xmm14, 888(%rdi)
	vextracti128 $1, %ymm14, %xmm6
	vmovq %xmm6, 464(%rdi)
	vpextrq $1, %xmm6, 1320(%rdi)
	vmovq %xmm7, 896(%rdi)
	vpextrq $1, %xmm7, 472(%rdi)
	vextracti128 $1, %ymm7, %xmm6
	vmovq %xmm6, 1328(%rdi)
	vpextrq $1, %xmm6, 904(%rdi)
	vmovq %xmm8, 480(%rdi)
	vpextrq $1, %xmm8, 1336(%rdi)
	vextracti128 $1, %ymm8, %xmm6
	vmovq %xmm6, 912(%rdi)
	vpextrq $1, %xmm6, 488(%rdi)
	vmovq %xmm9, 1344(%rdi)
	vpextrq $1, %xmm9, 920(%rdi)
	vextracti128 $1, %ymm9, %xmm6
	vmovq %xmm6, 496(%rdi)
	vpextrq $1, %xmm6, 1352(%rdi)
	vmovq %xmm10, 928(%rdi)
	vpextrq $1, %xmm10, 504(%rdi)
	vextracti128 $1, %ymm10, %xmm6
	vmovq %xmm6, 1360(%rdi)
	vpextrq $1, %xmm6, 936(%rdi)
	.endm

