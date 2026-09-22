/* Same 1024 bytes written four ways.  If a store costs per instruction, the
 * multi-register ST1 forms win in proportion; if it costs per 16-byte chunk,
 * they are all the same.  x0 buffer, x1 repeat count. */
#ifdef __APPLE__
#define st_q1 _st_q1
#define st_q2 _st_q2
#define st_q3 _st_q3
#define st_q4 _st_q4
#endif
.text
.macro BODY name, n
.global \name
\name:
1:
.if \n == 1
    .irp k,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63
    str q0, [x0, #16*\k]
    .endr
.endif
.if \n == 2
    .irp k,0,2,4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36,38,40,42,44,46,48,50,52,54,56,58,60,62
    add x2, x0, #16*\k
    st1 {v0.8h, v1.8h}, [x2]
    .endr
.endif
.if \n == 3
    .irp k,0,3,6,9,12,15,18,21,24,27,30,33,36,39,42,45,48,51,54,57,60
    add x2, x0, #16*\k
    st1 {v0.8h, v1.8h, v2.8h}, [x2]
    .endr
    str q0, [x0, #16*63]
.endif
.if \n == 4
    .irp k,0,4,8,12,16,20,24,28,32,36,40,44,48,52,56,60
    add x2, x0, #16*\k
    st1 {v0.8h, v1.8h, v2.8h, v3.8h}, [x2]
    .endr
.endif
    subs x1, x1, #1
    b.ne 1b
    ret
.endm
BODY st_q1, 1
BODY st_q2, 2
BODY st_q3, 3
BODY st_q4, 4
