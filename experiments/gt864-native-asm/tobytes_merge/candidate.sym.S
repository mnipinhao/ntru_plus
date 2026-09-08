.text
.global byte_merge_row
byte_merge_row:
// live-in: x0-x4 as specified in kernel-contract.yml.
// live-out: exact output memory; no coefficient scratch.
// range: normalized bytes; producer accepts signed int16.
// reserved registers: x18-x30; outer wrapper preserves d8-d15.
byte_merge_row_slothy_start:
    ldr Q<p0lo>, [x1, #0]
    add x5, x1, #16
    ldr D<p0hi>, [x5]
    ldr Q<p1lo>, [x2, #0]
    add x5, x2, #16
    ldr D<p1hi>, [x5]
    ldr Q<p2lo>, [x3, #0]
    add x5, x3, #16
    ldr D<p2hi>, [x5]
    ldr Q<idx0>, [x4, #0]
    tbl V<part0>.16b, {V<p0lo>.16b, V<p0hi>.16b}, V<idx0>.16b
    ldr Q<idx1>, [x4, #16]
    tbl V<part1>.16b, {V<p1lo>.16b, V<p1hi>.16b}, V<idx1>.16b
    ldr Q<idx2>, [x4, #32]
    tbl V<part2>.16b, {V<p2lo>.16b, V<p2hi>.16b}, V<idx2>.16b
    orr V<out0>.16b, V<part0>.16b, V<part1>.16b
    orr V<out0>.16b, V<out0>.16b, V<part2>.16b
    str Q<out0>, [x0, #0]
    ldr Q<idx3>, [x4, #48]
    tbl V<part3>.16b, {V<p0lo>.16b, V<p0hi>.16b}, V<idx3>.16b
    ldr Q<idx4>, [x4, #64]
    tbl V<part4>.16b, {V<p1lo>.16b, V<p1hi>.16b}, V<idx4>.16b
    ldr Q<idx5>, [x4, #80]
    tbl V<part5>.16b, {V<p2lo>.16b, V<p2hi>.16b}, V<idx5>.16b
    orr V<out1>.16b, V<part3>.16b, V<part4>.16b
    orr V<out1>.16b, V<out1>.16b, V<part5>.16b
    str Q<out1>, [x0, #16]
    ldr Q<idx6>, [x4, #96]
    tbl V<part6>.16b, {V<p0lo>.16b, V<p0hi>.16b}, V<idx6>.16b
    ldr Q<idx7>, [x4, #112]
    tbl V<part7>.16b, {V<p1lo>.16b, V<p1hi>.16b}, V<idx7>.16b
    ldr Q<idx8>, [x4, #128]
    tbl V<part8>.16b, {V<p2lo>.16b, V<p2hi>.16b}, V<idx8>.16b
    orr V<out2>.16b, V<part6>.16b, V<part7>.16b
    orr V<out2>.16b, V<out2>.16b, V<part8>.16b
    str Q<out2>, [x0, #32]
    ldr Q<idx9>, [x4, #144]
    tbl V<part9>.16b, {V<p0lo>.16b, V<p0hi>.16b}, V<idx9>.16b
    ldr Q<idx10>, [x4, #160]
    tbl V<part10>.16b, {V<p1lo>.16b, V<p1hi>.16b}, V<idx10>.16b
    ldr Q<idx11>, [x4, #176]
    tbl V<part11>.16b, {V<p2lo>.16b, V<p2hi>.16b}, V<idx11>.16b
    orr V<out3>.16b, V<part9>.16b, V<part10>.16b
    orr V<out3>.16b, V<out3>.16b, V<part11>.16b
    str Q<out3>, [x0, #48]
    ldr Q<idx12>, [x4, #192]
    tbl V<part12>.16b, {V<p0lo>.16b, V<p0hi>.16b}, V<idx12>.16b
    ldr Q<idx13>, [x4, #208]
    tbl V<part13>.16b, {V<p1lo>.16b, V<p1hi>.16b}, V<idx13>.16b
    ldr Q<idx14>, [x4, #224]
    tbl V<part14>.16b, {V<p2lo>.16b, V<p2hi>.16b}, V<idx14>.16b
    orr V<out4>.16b, V<part12>.16b, V<part13>.16b
    orr V<out4>.16b, V<out4>.16b, V<part14>.16b
    str D<out4>, [x0, #64]
byte_merge_row_slothy_end:
    ret
