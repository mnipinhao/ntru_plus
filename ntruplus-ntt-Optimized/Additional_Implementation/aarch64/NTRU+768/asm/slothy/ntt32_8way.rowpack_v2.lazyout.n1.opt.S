/*
 * Opt-in lazy-output wrapper for the rowpack-v2 NTT32 experimental kernel.
 *
 * The included kernel defaults to final stage345 canonical reduction.  This
 * wrapper flips only that output-tail contract so local experiments can measure
 * the cost and downstream range impact without changing the default full
 * pipeline provider.
 */

    .equ NTT32_ROWPACK_V2_LAZY_OUTPUT, 1
    .include "asm/slothy/ntt32_8way.rowpack_v2.n1.opt.s"
