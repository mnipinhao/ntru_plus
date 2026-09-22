// Fragment: load twiddles with public post-increment addressing.
// Use only when kernel-contract.yml records pointer updates and alignment.
// live-in: x1 twiddle pointer
// live-out: V<z0>.8h, V<z1>.8h, V<z2>.8h, V<z3>.8h, updated x1
// reserved physical registers: contract-defined only
// range: constants carry contract-defined representation bounds
// memory: public x1 post-increment loads only

slothy_start_twiddle_postinc_load:
    ldr     Q<z0>, [x1], #16
    ldr     Q<z1>, [x1], #16
    ldr     Q<z2>, [x1], #16
    ldr     Q<z3>, [x1], #16
slothy_end_twiddle_postinc_load:
