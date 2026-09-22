// Kernel: KERNEL_ID
// Scheme: NTRU+ or HAETAE
// Platform: AArch64 Neon
// Input representation:
// Output representation:
// Coefficient bounds before:
// Coefficient bounds after:
// Constants:
// Live-in:
// Live-out:
// Reserved physical registers:
//
// Fill this from a checked kernel-contract.yml and instruction-dag.yml.
// Existing region replacement also requires baseline-contract.yml.
// Keep this source clean and dataflow-oriented. Do not hand-schedule final code.

.text
.align 4
.global KERNEL_NAME
.type KERNEL_NAME, %function

KERNEL_NAME:
    // ABI inputs:
    // x0 = input/output pointer placeholder
    // x1 = input pointer placeholder
    // x2 = constants pointer placeholder
    //
    // Keep prologue, epilogue, and ABI scaffolding outside Slothy region unless
    // the contract explicitly includes them.

    // setup / ABI movement if needed

slothy_start_KERNEL_ID:
    // Clean symbolic instruction-selection-level code.
    // No premature hand scheduling.
    // No physical temp registers unless explicitly allowed.
    // live-in:
    // live-out:
    // reserved physical registers:
    // range:
    // const:
    // memory:

    ldr     Q<v_a0>, [x0]
    ldr     Q<v_a1>, [x1]
    add     V<v_sum0>.8h, V<v_a0>.8h, V<v_a1>.8h
    str     Q<v_sum0>, [x0]

slothy_end_KERNEL_ID:
    ret

.size KERNEL_NAME, .-KERNEL_NAME
