#ifdef __APPLE__
#define gt864_crepmod3_raw _gt864_crepmod3_raw
#endif
.text
.p2align 4
.global gt864_crepmod3_raw
gt864_crepmod3_raw:
mov w4, #1728
dup v0.8h, w4
mov w4, #-1728
dup v1.8h, w4
mov w4, #10923
dup v2.8h, w4
movi v3.8h, #3
mov x8, #27
.Lp8_loop:
// live-in: x0 v0 v1 v2 v3; live-out: memory and same inputs
// range: raw abs<=4577 -> ternary; reserved registers: v0-v3 v8-v15 x8
p8_slothy_start:
ldr Q<a0>, [x0, #0]
cmgt V<h0>.8h, V<a0>.8h, v0.8h
cmgt V<l0>.8h, v1.8h, V<a0>.8h
add V<y0>.8h, V<a0>.8h, V<h0>.8h
sub V<y0>.8h, V<y0>.8h, V<l0>.8h
sqrdmulh V<quotient0>.8h, V<y0>.8h, v2.8h
mls V<y0>.8h, V<quotient0>.8h, v3.8h
str Q<y0>, [x0, #0]
ldr Q<a1>, [x0, #16]
cmgt V<h1>.8h, V<a1>.8h, v0.8h
cmgt V<l1>.8h, v1.8h, V<a1>.8h
add V<y1>.8h, V<a1>.8h, V<h1>.8h
sub V<y1>.8h, V<y1>.8h, V<l1>.8h
sqrdmulh V<quotient1>.8h, V<y1>.8h, v2.8h
mls V<y1>.8h, V<quotient1>.8h, v3.8h
str Q<y1>, [x0, #16]
ldr Q<a2>, [x0, #32]
cmgt V<h2>.8h, V<a2>.8h, v0.8h
cmgt V<l2>.8h, v1.8h, V<a2>.8h
add V<y2>.8h, V<a2>.8h, V<h2>.8h
sub V<y2>.8h, V<y2>.8h, V<l2>.8h
sqrdmulh V<quotient2>.8h, V<y2>.8h, v2.8h
mls V<y2>.8h, V<quotient2>.8h, v3.8h
str Q<y2>, [x0, #32]
ldr Q<a3>, [x0, #48]
cmgt V<h3>.8h, V<a3>.8h, v0.8h
cmgt V<l3>.8h, v1.8h, V<a3>.8h
add V<y3>.8h, V<a3>.8h, V<h3>.8h
sub V<y3>.8h, V<y3>.8h, V<l3>.8h
sqrdmulh V<quotient3>.8h, V<y3>.8h, v2.8h
mls V<y3>.8h, V<quotient3>.8h, v3.8h
str Q<y3>, [x0, #48]
p8_slothy_end:
add x0, x0, #64
subs x8, x8, #1
b.ne .Lp8_loop
ret
