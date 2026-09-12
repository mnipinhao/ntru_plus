#ifdef __APPLE__
.text
.p2align 4
.global _test_p10_num_pair
_test_p10_num_pair:
    mov w8, #3457
    dup v30.8h, w8
    mov w8, #-12929
    dup v31.8h, w8
    b p10_num_pair

.p2align 4
.global _test_p10_finish_tile
_test_p10_finish_tile:
    mov w8, #3457
    dup v30.8h, w8
    mov w8, #-12929
    dup v31.8h, w8
    b p10_finish_tile

.p2align 4
.global _test_p10_inverse3
_test_p10_inverse3:
    b p10_inverse3
#endif
