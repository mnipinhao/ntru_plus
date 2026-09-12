#ifdef __APPLE__
#define p11_route_ternary _p11_route_ternary
#endif
.text
.p2align 4
.global p11_route_ternary
p11_route_ternary:
mov w9, #1728
dup v0.8h, w9
mov w9, #-1728
dup v1.8h, w9
mov w9, #10923
dup v2.8h, w9
movi v3.8h, #3
add x1, x1, #1488
add x7, x2, #1784
add x0, x0, #1674
mov x8, #32
mov x12, #2
.Lp11a1_route_loop:
// live-in: x0 descending natural output, x1 descending in-place main records, x7 descending tail stream
// live-out: 27 ternary coefficients and all pointers moved to the preceding block
// coefficient range: raw abs4577 -> adjusted abs4576 -> ternary abs1
// reserved physical registers: v0-v3, x8, x18-x30, sp
// no spill and no secret-dependent branch or address
p11a1_route32_slothy_start:
ldr Q<c0>, [x1, #0]
ldr Q<c1>, [x1, #16]
ldr Q<c2>, [x1, #32]
sub x1, x1, #48
cmgt V<h0>.8h, V<c0>.8h, v0.8h
cmgt V<l0>.8h, v1.8h, V<c0>.8h
cmgt V<h1>.8h, V<c1>.8h, v0.8h
cmgt V<l1>.8h, v1.8h, V<c1>.8h
cmgt V<h2>.8h, V<c2>.8h, v0.8h
cmgt V<l2>.8h, v1.8h, V<c2>.8h
add V<c0>.8h, V<c0>.8h, V<h0>.8h
add V<c1>.8h, V<c1>.8h, V<h1>.8h
add V<c2>.8h, V<c2>.8h, V<h2>.8h
sub V<c0>.8h, V<c0>.8h, V<l0>.8h
sub V<c1>.8h, V<c1>.8h, V<l1>.8h
sub V<c2>.8h, V<c2>.8h, V<l2>.8h
sqrdmulh V<h0>.8h, V<c0>.8h, v2.8h
sqrdmulh V<h1>.8h, V<c1>.8h, v2.8h
sqrdmulh V<h2>.8h, V<c2>.8h, v2.8h
mls V<c0>.8h, V<h0>.8h, v3.8h
mls V<c1>.8h, V<h1>.8h, v3.8h
mls V<c2>.8h, V<h2>.8h, v3.8h
st3 {V<c0>.8h, V<c1>.8h, V<c2>.8h}, [x0], #48
ldr D<tail>, [x7]
sub x7, x7, #8
cmgt V<th>.8h, V<tail>.8h, v0.8h
cmgt V<tl>.8h, v1.8h, V<tail>.8h
add V<tail>.8h, V<tail>.8h, V<th>.8h
sub V<tail>.8h, V<tail>.8h, V<tl>.8h
sqrdmulh V<th>.8h, V<tail>.8h, v2.8h
mls V<tail>.8h, V<th>.8h, v3.8h
st1 {V<tail>.h}[0], [x0], x12
st1 {V<tail>.h}[1], [x0], x12
st1 {V<tail>.h}[2], [x0], x12
sub x0, x0, #108
p11a1_route32_slothy_end:
subs x8, x8, #1
b.ne .Lp11a1_route_loop
ret
