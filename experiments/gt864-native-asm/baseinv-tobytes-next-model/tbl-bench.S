.text
.macro INIT
    movi v0.16b, #1
    movi v1.16b, #2
    movi v2.16b, #3
    movi v16.16b, #1
    movi v17.16b, #2
    movi v18.16b, #3
    movi v19.16b, #4
.endm
.macro BODY2
    tbl v20.16b, {v0.16b-v1.16b}, v16.16b
    tbl v21.16b, {v0.16b-v1.16b}, v17.16b
    tbl v22.16b, {v0.16b-v1.16b}, v18.16b
    tbl v23.16b, {v0.16b-v1.16b}, v19.16b
    tbl v24.16b, {v0.16b-v1.16b}, v16.16b
    tbl v25.16b, {v0.16b-v1.16b}, v17.16b
    tbl v26.16b, {v0.16b-v1.16b}, v18.16b
    tbl v27.16b, {v0.16b-v1.16b}, v19.16b
    tbl v28.16b, {v0.16b-v1.16b}, v16.16b
    tbl v29.16b, {v0.16b-v1.16b}, v17.16b
    tbl v30.16b, {v0.16b-v1.16b}, v18.16b
    tbl v31.16b, {v0.16b-v1.16b}, v19.16b
    tbl v20.16b, {v0.16b-v1.16b}, v16.16b
    tbl v21.16b, {v0.16b-v1.16b}, v17.16b
    tbl v22.16b, {v0.16b-v1.16b}, v18.16b
    tbl v23.16b, {v0.16b-v1.16b}, v19.16b
.endm
.macro BODY3
    tbl v20.16b, {v0.16b-v2.16b}, v16.16b
    tbl v21.16b, {v0.16b-v2.16b}, v17.16b
    tbl v22.16b, {v0.16b-v2.16b}, v18.16b
    tbl v23.16b, {v0.16b-v2.16b}, v19.16b
    tbl v24.16b, {v0.16b-v2.16b}, v16.16b
    tbl v25.16b, {v0.16b-v2.16b}, v17.16b
    tbl v26.16b, {v0.16b-v2.16b}, v18.16b
    tbl v27.16b, {v0.16b-v2.16b}, v19.16b
    tbl v28.16b, {v0.16b-v2.16b}, v16.16b
    tbl v29.16b, {v0.16b-v2.16b}, v17.16b
    tbl v30.16b, {v0.16b-v2.16b}, v18.16b
    tbl v31.16b, {v0.16b-v2.16b}, v19.16b
    tbl v20.16b, {v0.16b-v2.16b}, v16.16b
    tbl v21.16b, {v0.16b-v2.16b}, v17.16b
    tbl v22.16b, {v0.16b-v2.16b}, v18.16b
    tbl v23.16b, {v0.16b-v2.16b}, v19.16b
.endm
.global tbl_empty
tbl_empty:
1:  subs x0,x0,#1
    b.ne 1b
    ret
.global tbl2_throughput
tbl2_throughput:
    INIT
1:  BODY2
    subs x0,x0,#1
    b.ne 1b
    ret
.global tbl3_throughput
tbl3_throughput:
    INIT
1:  BODY3
    subs x0,x0,#1
    b.ne 1b
    ret
.global tbl2_latency
tbl2_latency:
    INIT
    mov v20.16b,v16.16b
1:  .rept 16
    tbl v20.16b,{v0.16b-v1.16b},v20.16b
    .endr
    subs x0,x0,#1
    b.ne 1b
    ret
.global tbl3_latency
tbl3_latency:
    INIT
    mov v20.16b,v16.16b
1:  .rept 16
    tbl v20.16b,{v0.16b-v2.16b},v20.16b
    .endr
    subs x0,x0,#1
    b.ne 1b
    ret
