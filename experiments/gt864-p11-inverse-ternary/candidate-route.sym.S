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
add x2, x1, #256
add x3, x1, #512
add x4, x1, #768
add x5, x1, #1024
add x6, x1, #1280
add x7, x1, #1536
mov x8, #32
mov x12, #2
.Lp11_route_loop:
// live-in: x0 output, x1-x7 scratch streams, x12 lane increment, v0-v3 constants
// live-out: 27 ternary coefficients and all pointers advanced by one block
// coefficient range: raw abs4577 -> adjusted abs4576 -> ternary abs1
// reserved physical registers: v0-v3, x8, x18-x30, sp
// no spill and no secret-dependent branch or address
p11_route32_slothy_start:
ldr D<c0>, [x1], #8
ldr x9, [x2], #8
ins V<c0>.d[1], x9
ldr D<c1>, [x3], #8
ldr x10, [x4], #8
ins V<c1>.d[1], x10
ldr D<c2>, [x5], #8
ldr x11, [x6], #8
ins V<c2>.d[1], x11
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
ldr D<tail>, [x7], #8
cmgt V<th>.8h, V<tail>.8h, v0.8h
cmgt V<tl>.8h, v1.8h, V<tail>.8h
add V<tail>.8h, V<tail>.8h, V<th>.8h
sub V<tail>.8h, V<tail>.8h, V<tl>.8h
sqrdmulh V<th>.8h, V<tail>.8h, v2.8h
mls V<tail>.8h, V<th>.8h, v3.8h
st1 {V<tail>.h}[0], [x0], x12
st1 {V<tail>.h}[1], [x0], x12
st1 {V<tail>.h}[2], [x0], x12
p11_route32_slothy_end:
subs x8, x8, #1
b.ne .Lp11_route_loop
ret
