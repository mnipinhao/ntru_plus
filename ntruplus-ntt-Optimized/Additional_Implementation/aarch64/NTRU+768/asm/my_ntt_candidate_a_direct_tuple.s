#ifdef __APPLE__
.equ MY_NTT_DARWIN_NO_WEAK, 1
#endif
.equ MY_NTT_DIRECT_TUPLE, 1
.equ MY_NTT_NO_POLY_ALIAS, 1
.include "asm/my_ntt.s"
