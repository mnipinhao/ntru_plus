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
mov x8, #16
.Lp11a3_route_loop:
// live-in: x0 descending output, x1 in-place main records, x7 tail stream
// live-out: 27 ternary coefficients and all pointers moved to the preceding block
// coefficient range: raw abs4577 -> adjusted abs4576 -> ternary abs1
// reserved physical registers: v0-v3, x8, x18-x30, sp
// no spill and no secret-dependent branch or address
// Two descending records share one loop branch; symbolic values remain distinct.
p11a3_route64_slothy_start:
ldr Q<c0a>, [x1, #0]
ldr Q<c1a>, [x1, #16]
ldr Q<c2a>, [x1, #32]
sub x1, x1, #48
ldr D<taila>, [x7]
sub x7, x7, #8
cmgt V<h0a>.8h, V<c0a>.8h, v0.8h
cmgt V<l0a>.8h, v1.8h, V<c0a>.8h
cmgt V<h1a>.8h, V<c1a>.8h, v0.8h
cmgt V<l1a>.8h, v1.8h, V<c1a>.8h
cmgt V<h2a>.8h, V<c2a>.8h, v0.8h
cmgt V<l2a>.8h, v1.8h, V<c2a>.8h
add V<c0a>.8h, V<c0a>.8h, V<h0a>.8h
add V<c1a>.8h, V<c1a>.8h, V<h1a>.8h
add V<c2a>.8h, V<c2a>.8h, V<h2a>.8h
sub V<c0a>.8h, V<c0a>.8h, V<l0a>.8h
sub V<c1a>.8h, V<c1a>.8h, V<l1a>.8h
sub V<c2a>.8h, V<c2a>.8h, V<l2a>.8h
sqrdmulh V<h0a>.8h, V<c0a>.8h, v2.8h
sqrdmulh V<h1a>.8h, V<c1a>.8h, v2.8h
sqrdmulh V<h2a>.8h, V<c2a>.8h, v2.8h
mls V<c0a>.8h, V<h0a>.8h, v3.8h
mls V<c1a>.8h, V<h1a>.8h, v3.8h
mls V<c2a>.8h, V<h2a>.8h, v3.8h
cmgt V<tha>.8h, V<taila>.8h, v0.8h
cmgt V<tla>.8h, v1.8h, V<taila>.8h
add V<taila>.8h, V<taila>.8h, V<tha>.8h
sub V<taila>.8h, V<taila>.8h, V<tla>.8h
sqrdmulh V<tha>.8h, V<taila>.8h, v2.8h
mls V<taila>.8h, V<tha>.8h, v3.8h
ext V<tailouta>.16b, V<c2a>.16b, V<taila>.16b, #14
add X<tailptra>, x0, #46
st3 {V<c0a>.8h, V<c1a>.8h, V<c2a>.8h}, [x0]
str D<tailouta>, [X<tailptra>, #0]
sub x0, x0, #54
ldr Q<c0b>, [x1, #0]
ldr Q<c1b>, [x1, #16]
ldr Q<c2b>, [x1, #32]
sub x1, x1, #48
ldr D<tailb>, [x7]
sub x7, x7, #8
cmgt V<h0b>.8h, V<c0b>.8h, v0.8h
cmgt V<l0b>.8h, v1.8h, V<c0b>.8h
cmgt V<h1b>.8h, V<c1b>.8h, v0.8h
cmgt V<l1b>.8h, v1.8h, V<c1b>.8h
cmgt V<h2b>.8h, V<c2b>.8h, v0.8h
cmgt V<l2b>.8h, v1.8h, V<c2b>.8h
add V<c0b>.8h, V<c0b>.8h, V<h0b>.8h
add V<c1b>.8h, V<c1b>.8h, V<h1b>.8h
add V<c2b>.8h, V<c2b>.8h, V<h2b>.8h
sub V<c0b>.8h, V<c0b>.8h, V<l0b>.8h
sub V<c1b>.8h, V<c1b>.8h, V<l1b>.8h
sub V<c2b>.8h, V<c2b>.8h, V<l2b>.8h
sqrdmulh V<h0b>.8h, V<c0b>.8h, v2.8h
sqrdmulh V<h1b>.8h, V<c1b>.8h, v2.8h
sqrdmulh V<h2b>.8h, V<c2b>.8h, v2.8h
mls V<c0b>.8h, V<h0b>.8h, v3.8h
mls V<c1b>.8h, V<h1b>.8h, v3.8h
mls V<c2b>.8h, V<h2b>.8h, v3.8h
cmgt V<thb>.8h, V<tailb>.8h, v0.8h
cmgt V<tlb>.8h, v1.8h, V<tailb>.8h
add V<tailb>.8h, V<tailb>.8h, V<thb>.8h
sub V<tailb>.8h, V<tailb>.8h, V<tlb>.8h
sqrdmulh V<thb>.8h, V<tailb>.8h, v2.8h
mls V<tailb>.8h, V<thb>.8h, v3.8h
ext V<tailoutb>.16b, V<c2b>.16b, V<tailb>.16b, #14
add X<tailptrb>, x0, #46
st3 {V<c0b>.8h, V<c1b>.8h, V<c2b>.8h}, [x0]
str D<tailoutb>, [X<tailptrb>, #0]
sub x0, x0, #54
p11a3_route64_slothy_end:
subs x8, x8, #1
b.ne .Lp11a3_route_loop
ret
