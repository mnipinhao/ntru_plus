.text

.global gt864_p6b_route_frontier
gt864_p6b_route_frontier:
// P6-B route frontier.
// live-in: x2 public index, x3 synthetic seed, x4 synthetic sink.
// live-out: Q<s0>..Q<s19> and repaired Q<b0> plus Q<b1>..Q<b8>.
// range: retained bytes 0..255; B route values are signed int16.
// reserved physical registers: x18, sp, xzr; vectors may use v0-v31.
// Q<s0>..Q<s19> are the two saved pairs plus already-packed A.  The TBL is
// destructive, so its public index is the only additional live vector.
gt864_p6b_route_frontier_slothy_start:
    ldr Q<s0>, [x3, #0]
    ldr Q<s1>, [x3, #16]
    ldr Q<s2>, [x3, #32]
    ldr Q<s3>, [x3, #48]
    ldr Q<s4>, [x3, #64]
    ldr Q<s5>, [x3, #80]
    ldr Q<s6>, [x3, #96]
    ldr Q<s7>, [x3, #112]
    ldr Q<s8>, [x3, #128]
    ldr Q<s9>, [x3, #144]
    ldr Q<s10>, [x3, #160]
    ldr Q<s11>, [x3, #176]
    ldr Q<s12>, [x3, #192]
    ldr Q<s13>, [x3, #208]
    ldr Q<s14>, [x3, #224]
    ldr Q<s15>, [x3, #240]
    ldr Q<s16>, [x3, #256]
    ldr Q<s17>, [x3, #272]
    ldr Q<s18>, [x3, #288]
    ldr Q<s19>, [x3, #304]
    ldr Q<b0>, [x3, #320]
    ldr Q<b1>, [x3, #336]
    ldr Q<b2>, [x3, #352]
    ldr Q<b3>, [x3, #368]
    ldr Q<b4>, [x3, #384]
    ldr Q<b5>, [x3, #400]
    ldr Q<b6>, [x3, #416]
    ldr Q<b7>, [x3, #432]
    ldr Q<b8>, [x3, #448]
    ldr Q<idx>, [x2]
    tbl V<b0>.16b, {V<b0>.16b}, V<idx>.16b
    str Q<s0>, [x4, #0]
    str Q<s1>, [x4, #16]
    str Q<s2>, [x4, #32]
    str Q<s3>, [x4, #48]
    str Q<s4>, [x4, #64]
    str Q<s5>, [x4, #80]
    str Q<s6>, [x4, #96]
    str Q<s7>, [x4, #112]
    str Q<s8>, [x4, #128]
    str Q<s9>, [x4, #144]
    str Q<s10>, [x4, #160]
    str Q<s11>, [x4, #176]
    str Q<s12>, [x4, #192]
    str Q<s13>, [x4, #208]
    str Q<s14>, [x4, #224]
    str Q<s15>, [x4, #240]
    str Q<s16>, [x4, #256]
    str Q<s17>, [x4, #272]
    str Q<s18>, [x4, #288]
    str Q<s19>, [x4, #304]
    str Q<b0>, [x4, #320]
    str Q<b1>, [x4, #336]
    str Q<b2>, [x4, #352]
    str Q<b3>, [x4, #368]
    str Q<b4>, [x4, #384]
    str Q<b5>, [x4, #400]
    str Q<b6>, [x4, #416]
    str Q<b7>, [x4, #432]
    str Q<b8>, [x4, #448]
gt864_p6b_route_frontier_slothy_end:
    ret

.global gt864_p6b_full_normalize_frontier
gt864_p6b_full_normalize_frontier:
// P6-B full-normalization frontier.
// live-in: x2 public constants, x3 synthetic seed, x4 synthetic sink.
// live-out: Q<s0>..Q<s19>, canonical Q<b0>, Q<b1>..Q<b8>, Q<q>, Q<recip>.
// range: B producer int16 becomes canonical 0..3456; saved bytes stay 0..255.
// reserved physical registers: x18, sp, xzr; vectors may use v0-v31.
// q and reciprocal9 remain live for later rows, while Q<quot> is the single
// transient at the exact 32-register peak.
gt864_p6b_full_normalize_frontier_slothy_start:
    ldr Q<s0>, [x3, #0]
    ldr Q<s1>, [x3, #16]
    ldr Q<s2>, [x3, #32]
    ldr Q<s3>, [x3, #48]
    ldr Q<s4>, [x3, #64]
    ldr Q<s5>, [x3, #80]
    ldr Q<s6>, [x3, #96]
    ldr Q<s7>, [x3, #112]
    ldr Q<s8>, [x3, #128]
    ldr Q<s9>, [x3, #144]
    ldr Q<s10>, [x3, #160]
    ldr Q<s11>, [x3, #176]
    ldr Q<s12>, [x3, #192]
    ldr Q<s13>, [x3, #208]
    ldr Q<s14>, [x3, #224]
    ldr Q<s15>, [x3, #240]
    ldr Q<s16>, [x3, #256]
    ldr Q<s17>, [x3, #272]
    ldr Q<s18>, [x3, #288]
    ldr Q<s19>, [x3, #304]
    ldr Q<b0>, [x3, #320]
    ldr Q<b1>, [x3, #336]
    ldr Q<b2>, [x3, #352]
    ldr Q<b3>, [x3, #368]
    ldr Q<b4>, [x3, #384]
    ldr Q<b5>, [x3, #400]
    ldr Q<b6>, [x3, #416]
    ldr Q<b7>, [x3, #432]
    ldr Q<b8>, [x3, #448]
    ldr Q<q>, [x2, #0]
    ldr Q<recip>, [x2, #16]
    sqrdmulh V<quot>.8h, V<b0>.8h, V<recip>.8h
    mls V<b0>.8h, V<quot>.8h, V<q>.8h
    sshr V<quot>.8h, V<b0>.8h, #15
    and V<quot>.16b, V<quot>.16b, V<q>.16b
    add V<b0>.8h, V<b0>.8h, V<quot>.8h
    str Q<s0>, [x4, #0]
    str Q<s1>, [x4, #16]
    str Q<s2>, [x4, #32]
    str Q<s3>, [x4, #48]
    str Q<s4>, [x4, #64]
    str Q<s5>, [x4, #80]
    str Q<s6>, [x4, #96]
    str Q<s7>, [x4, #112]
    str Q<s8>, [x4, #128]
    str Q<s9>, [x4, #144]
    str Q<s10>, [x4, #160]
    str Q<s11>, [x4, #176]
    str Q<s12>, [x4, #192]
    str Q<s13>, [x4, #208]
    str Q<s14>, [x4, #224]
    str Q<s15>, [x4, #240]
    str Q<s16>, [x4, #256]
    str Q<s17>, [x4, #272]
    str Q<s18>, [x4, #288]
    str Q<s19>, [x4, #304]
    str Q<b0>, [x4, #320]
    str Q<b1>, [x4, #336]
    str Q<b2>, [x4, #352]
    str Q<b3>, [x4, #368]
    str Q<b4>, [x4, #384]
    str Q<b5>, [x4, #400]
    str Q<b6>, [x4, #416]
    str Q<b7>, [x4, #432]
    str Q<b8>, [x4, #448]
    str Q<q>, [x4, #464]
    str Q<recip>, [x4, #480]
gt864_p6b_full_normalize_frontier_slothy_end:
    ret
