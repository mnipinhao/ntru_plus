/* 96 KiB of distinct instructions: executing it evicts the KEM from the L1I and L2. */
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
