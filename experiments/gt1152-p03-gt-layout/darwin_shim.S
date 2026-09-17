/* Darwin-only alias. The NTRU+864 package targets Linux/AArch64; ntt_tail.S
 * defines only _ntt_tail_asm under __APPLE__, while ntt.S calls the unprefixed
 * name. This shim exists solely so the layout probe can run on macOS. */
#ifdef __APPLE__
.text
.p2align 2
.global ntt_tail_asm
ntt_tail_asm:
    b _ntt_tail_asm
#endif
