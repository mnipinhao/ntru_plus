.text
.global gt864_p6_register_frontier
gt864_p6_register_frontier:
// Allocation-only hard gate.  Synthetic loads seed the exact 31-value vector
// frontier; they are not proposed production memory accesses.  Every seeded
// value is declared a Slothy live-out by optimize.py.
// live-in: x0 output, x2 public row index, x3 synthetic frontier seed.
// live-out: Q<h0>..Q<h12>, Q<a0>..Q<a7>, Q<aninth>, Q<b0>..Q<b7>,
// Q<bninth>, and Q<row0>.
// range: retained bytes are 0..255; route coefficients are signed int16.
// reserved physical registers: x18, sp and xzr; vector allocation uses v0-v31.
gt864_p6_register_frontier_slothy_start:
    ldr Q<h0>, [x3, #0]
    ldr Q<h1>, [x3, #16]
    ldr Q<h2>, [x3, #32]
    ldr Q<h3>, [x3, #48]
    ldr Q<h4>, [x3, #64]
    ldr Q<h5>, [x3, #80]
    ldr Q<h6>, [x3, #96]
    ldr Q<h7>, [x3, #112]
    ldr Q<h8>, [x3, #128]
    ldr Q<h9>, [x3, #144]
    ldr Q<h10>, [x3, #160]
    ldr Q<h11>, [x3, #176]
    ldr Q<h12>, [x3, #192]
    ldr Q<a0>, [x3, #208]
    ldr Q<a1>, [x3, #224]
    ldr Q<a2>, [x3, #240]
    ldr Q<a3>, [x3, #256]
    ldr Q<a4>, [x3, #272]
    ldr Q<a5>, [x3, #288]
    ldr Q<a6>, [x3, #304]
    ldr Q<a7>, [x3, #320]
    ldr Q<aninth>, [x3, #336]
    ldr Q<b0>, [x3, #352]
    ldr Q<b1>, [x3, #368]
    ldr Q<b2>, [x3, #384]
    ldr Q<b3>, [x3, #400]
    ldr Q<b4>, [x3, #416]
    ldr Q<b5>, [x3, #432]
    ldr Q<b6>, [x3, #448]
    ldr Q<b7>, [x3, #464]
    ldr Q<bninth>, [x3, #480]
    orr V<row0>.16b, V<a0>.16b, V<a0>.16b
    ins V<row0>.h[0], V<aninth>.h[0]
    ldr Q<idx0>, [x2]
    tbl V<row0>.16b, {V<row0>.16b}, V<idx0>.16b
    // Synthetic live-out stores make the 31 frontier values remain live past
    // row0.  Reordering is disabled in this allocation-only gate.
    str Q<h0>, [x4, #0]
    str Q<h1>, [x4, #16]
    str Q<h2>, [x4, #32]
    str Q<h3>, [x4, #48]
    str Q<h4>, [x4, #64]
    str Q<h5>, [x4, #80]
    str Q<h6>, [x4, #96]
    str Q<h7>, [x4, #112]
    str Q<h8>, [x4, #128]
    str Q<h9>, [x4, #144]
    str Q<h10>, [x4, #160]
    str Q<h11>, [x4, #176]
    str Q<h12>, [x4, #192]
    str Q<a0>, [x4, #208]
    str Q<a1>, [x4, #224]
    str Q<a2>, [x4, #240]
    str Q<a3>, [x4, #256]
    str Q<a4>, [x4, #272]
    str Q<a5>, [x4, #288]
    str Q<a6>, [x4, #304]
    str Q<a7>, [x4, #320]
    str Q<aninth>, [x4, #336]
    str Q<b0>, [x4, #352]
    str Q<b1>, [x4, #368]
    str Q<b2>, [x4, #384]
    str Q<b3>, [x4, #400]
    str Q<b4>, [x4, #416]
    str Q<b5>, [x4, #432]
    str Q<b6>, [x4, #448]
    str Q<b7>, [x4, #464]
    str Q<bninth>, [x4, #480]
    str Q<row0>, [x0]
gt864_p6_register_frontier_slothy_end:
    ret
