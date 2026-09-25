/* 96 KiB of distinct instructions (as bench/aarch64/gt-production/bench_icache_thrash.S). */
.text
.p2align 6
.global icache_thrash
.type icache_thrash, %function
icache_thrash:
    .rept 24576
    nop
    .endr
    ret
.size icache_thrash, .-icache_thrash
.section .note.GNU-stack,"",%progbits
