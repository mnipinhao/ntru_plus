.text
.align 6

.global wave29_icache_thrash
.type wave29_icache_thrash, %function
wave29_icache_thrash:
    /* Benchmark-only: execute 96 KiB of distinct instructions on the pinned core. */
    .rept 24576
    nop
    .endr
    ret
.size wave29_icache_thrash, .-wave29_icache_thrash
