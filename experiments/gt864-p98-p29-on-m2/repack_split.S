#ifdef __APPLE__
#define repack_asm _repack_asm
#endif
.text
.global repack_asm
repack_asm:
        mov x7, #2
rp0_slothy_start:
        ldr q24, [x2, #0]
        ldr q25, [x2, #64]
        ldr q26, [x2, #128]
        ldr q0, [x1, #0]
        ldr q1, [x1, #256]
        ldr q2, [x1, #512]
        ldr q3, [x1, #768]
        ldr q4, [x1, #1024]
        ldr q5, [x1, #1280]
        zip1 v16.2d, v0.2d, v1.2d
        zip2 v19.2d, v0.2d, v1.2d
        zip1 v17.2d, v2.2d, v3.2d
        zip2 v20.2d, v2.2d, v3.2d
        zip1 v18.2d, v4.2d, v5.2d
        zip2 v21.2d, v4.2d, v5.2d
        add  x3, x0, #0
        st3  {v16.8h, v17.8h, v18.8h}, [x3]
        add  x5, x0, #48
        st1  {v24.h}[0], [x5], x7
        st1  {v25.h}[0], [x5], x7
        st1  {v26.h}[0], [x5]
        add  x3, x0, #54
        st3  {v19.8h, v20.8h, v21.8h}, [x3]
        add  x5, x0, #102
        st1  {v24.h}[1], [x5], x7
        st1  {v25.h}[1], [x5], x7
        st1  {v26.h}[1], [x5]
        ldr q0, [x1, #16]
        ldr q1, [x1, #272]
        ldr q2, [x1, #528]
        ldr q3, [x1, #784]
        ldr q4, [x1, #1040]
        ldr q5, [x1, #1296]
        zip1 v16.2d, v0.2d, v1.2d
        zip2 v19.2d, v0.2d, v1.2d
        zip1 v17.2d, v2.2d, v3.2d
        zip2 v20.2d, v2.2d, v3.2d
        zip1 v18.2d, v4.2d, v5.2d
        zip2 v21.2d, v4.2d, v5.2d
        add  x3, x0, #108
        st3  {v16.8h, v17.8h, v18.8h}, [x3]
        add  x5, x0, #156
        st1  {v24.h}[2], [x5], x7
        st1  {v25.h}[2], [x5], x7
        st1  {v26.h}[2], [x5]
        add  x3, x0, #162
        st3  {v19.8h, v20.8h, v21.8h}, [x3]
        add  x5, x0, #210
        st1  {v24.h}[3], [x5], x7
        st1  {v25.h}[3], [x5], x7
        st1  {v26.h}[3], [x5]
        ldr q0, [x1, #32]
        ldr q1, [x1, #288]
        ldr q2, [x1, #544]
        ldr q3, [x1, #800]
        ldr q4, [x1, #1056]
        ldr q5, [x1, #1312]
        zip1 v16.2d, v0.2d, v1.2d
        zip2 v19.2d, v0.2d, v1.2d
        zip1 v17.2d, v2.2d, v3.2d
        zip2 v20.2d, v2.2d, v3.2d
        zip1 v18.2d, v4.2d, v5.2d
        zip2 v21.2d, v4.2d, v5.2d
        add  x3, x0, #216
        st3  {v16.8h, v17.8h, v18.8h}, [x3]
        add  x5, x0, #264
        st1  {v24.h}[4], [x5], x7
        st1  {v25.h}[4], [x5], x7
        st1  {v26.h}[4], [x5]
        add  x3, x0, #270
        st3  {v19.8h, v20.8h, v21.8h}, [x3]
        add  x5, x0, #318
        st1  {v24.h}[5], [x5], x7
        st1  {v25.h}[5], [x5], x7
        st1  {v26.h}[5], [x5]
        ldr q0, [x1, #48]
        ldr q1, [x1, #304]
        ldr q2, [x1, #560]
        ldr q3, [x1, #816]
        ldr q4, [x1, #1072]
        ldr q5, [x1, #1328]
        zip1 v16.2d, v0.2d, v1.2d
        zip2 v19.2d, v0.2d, v1.2d
        zip1 v17.2d, v2.2d, v3.2d
        zip2 v20.2d, v2.2d, v3.2d
        zip1 v18.2d, v4.2d, v5.2d
        zip2 v21.2d, v4.2d, v5.2d
        add  x3, x0, #324
        st3  {v16.8h, v17.8h, v18.8h}, [x3]
        add  x5, x0, #372
        st1  {v24.h}[6], [x5], x7
        st1  {v25.h}[6], [x5], x7
        st1  {v26.h}[6], [x5]
        add  x3, x0, #378
        st3  {v19.8h, v20.8h, v21.8h}, [x3]
        add  x5, x0, #426
        st1  {v24.h}[7], [x5], x7
        st1  {v25.h}[7], [x5], x7
        st1  {v26.h}[7], [x5]
rp0_slothy_end:
rp1_slothy_start:
        ldr q24, [x2, #16]
        ldr q25, [x2, #80]
        ldr q26, [x2, #144]
        ldr q0, [x1, #64]
        ldr q1, [x1, #320]
        ldr q2, [x1, #576]
        ldr q3, [x1, #832]
        ldr q4, [x1, #1088]
        ldr q5, [x1, #1344]
        zip1 v16.2d, v0.2d, v1.2d
        zip2 v19.2d, v0.2d, v1.2d
        zip1 v17.2d, v2.2d, v3.2d
        zip2 v20.2d, v2.2d, v3.2d
        zip1 v18.2d, v4.2d, v5.2d
        zip2 v21.2d, v4.2d, v5.2d
        add  x3, x0, #432
        st3  {v16.8h, v17.8h, v18.8h}, [x3]
        add  x5, x0, #480
        st1  {v24.h}[0], [x5], x7
        st1  {v25.h}[0], [x5], x7
        st1  {v26.h}[0], [x5]
        add  x3, x0, #486
        st3  {v19.8h, v20.8h, v21.8h}, [x3]
        add  x5, x0, #534
        st1  {v24.h}[1], [x5], x7
        st1  {v25.h}[1], [x5], x7
        st1  {v26.h}[1], [x5]
        ldr q0, [x1, #80]
        ldr q1, [x1, #336]
        ldr q2, [x1, #592]
        ldr q3, [x1, #848]
        ldr q4, [x1, #1104]
        ldr q5, [x1, #1360]
        zip1 v16.2d, v0.2d, v1.2d
        zip2 v19.2d, v0.2d, v1.2d
        zip1 v17.2d, v2.2d, v3.2d
        zip2 v20.2d, v2.2d, v3.2d
        zip1 v18.2d, v4.2d, v5.2d
        zip2 v21.2d, v4.2d, v5.2d
        add  x3, x0, #540
        st3  {v16.8h, v17.8h, v18.8h}, [x3]
        add  x5, x0, #588
        st1  {v24.h}[2], [x5], x7
        st1  {v25.h}[2], [x5], x7
        st1  {v26.h}[2], [x5]
        add  x3, x0, #594
        st3  {v19.8h, v20.8h, v21.8h}, [x3]
        add  x5, x0, #642
        st1  {v24.h}[3], [x5], x7
        st1  {v25.h}[3], [x5], x7
        st1  {v26.h}[3], [x5]
        ldr q0, [x1, #96]
        ldr q1, [x1, #352]
        ldr q2, [x1, #608]
        ldr q3, [x1, #864]
        ldr q4, [x1, #1120]
        ldr q5, [x1, #1376]
        zip1 v16.2d, v0.2d, v1.2d
        zip2 v19.2d, v0.2d, v1.2d
        zip1 v17.2d, v2.2d, v3.2d
        zip2 v20.2d, v2.2d, v3.2d
        zip1 v18.2d, v4.2d, v5.2d
        zip2 v21.2d, v4.2d, v5.2d
        add  x3, x0, #648
        st3  {v16.8h, v17.8h, v18.8h}, [x3]
        add  x5, x0, #696
        st1  {v24.h}[4], [x5], x7
        st1  {v25.h}[4], [x5], x7
        st1  {v26.h}[4], [x5]
        add  x3, x0, #702
        st3  {v19.8h, v20.8h, v21.8h}, [x3]
        add  x5, x0, #750
        st1  {v24.h}[5], [x5], x7
        st1  {v25.h}[5], [x5], x7
        st1  {v26.h}[5], [x5]
        ldr q0, [x1, #112]
        ldr q1, [x1, #368]
        ldr q2, [x1, #624]
        ldr q3, [x1, #880]
        ldr q4, [x1, #1136]
        ldr q5, [x1, #1392]
        zip1 v16.2d, v0.2d, v1.2d
        zip2 v19.2d, v0.2d, v1.2d
        zip1 v17.2d, v2.2d, v3.2d
        zip2 v20.2d, v2.2d, v3.2d
        zip1 v18.2d, v4.2d, v5.2d
        zip2 v21.2d, v4.2d, v5.2d
        add  x3, x0, #756
        st3  {v16.8h, v17.8h, v18.8h}, [x3]
        add  x5, x0, #804
        st1  {v24.h}[6], [x5], x7
        st1  {v25.h}[6], [x5], x7
        st1  {v26.h}[6], [x5]
        add  x3, x0, #810
        st3  {v19.8h, v20.8h, v21.8h}, [x3]
        add  x5, x0, #858
        st1  {v24.h}[7], [x5], x7
        st1  {v25.h}[7], [x5], x7
        st1  {v26.h}[7], [x5]
rp1_slothy_end:
rp2_slothy_start:
        ldr q24, [x2, #32]
        ldr q25, [x2, #96]
        ldr q26, [x2, #160]
        ldr q0, [x1, #128]
        ldr q1, [x1, #384]
        ldr q2, [x1, #640]
        ldr q3, [x1, #896]
        ldr q4, [x1, #1152]
        ldr q5, [x1, #1408]
        zip1 v16.2d, v0.2d, v1.2d
        zip2 v19.2d, v0.2d, v1.2d
        zip1 v17.2d, v2.2d, v3.2d
        zip2 v20.2d, v2.2d, v3.2d
        zip1 v18.2d, v4.2d, v5.2d
        zip2 v21.2d, v4.2d, v5.2d
        add  x3, x0, #864
        st3  {v16.8h, v17.8h, v18.8h}, [x3]
        add  x5, x0, #912
        st1  {v24.h}[0], [x5], x7
        st1  {v25.h}[0], [x5], x7
        st1  {v26.h}[0], [x5]
        add  x3, x0, #918
        st3  {v19.8h, v20.8h, v21.8h}, [x3]
        add  x5, x0, #966
        st1  {v24.h}[1], [x5], x7
        st1  {v25.h}[1], [x5], x7
        st1  {v26.h}[1], [x5]
        ldr q0, [x1, #144]
        ldr q1, [x1, #400]
        ldr q2, [x1, #656]
        ldr q3, [x1, #912]
        ldr q4, [x1, #1168]
        ldr q5, [x1, #1424]
        zip1 v16.2d, v0.2d, v1.2d
        zip2 v19.2d, v0.2d, v1.2d
        zip1 v17.2d, v2.2d, v3.2d
        zip2 v20.2d, v2.2d, v3.2d
        zip1 v18.2d, v4.2d, v5.2d
        zip2 v21.2d, v4.2d, v5.2d
        add  x3, x0, #972
        st3  {v16.8h, v17.8h, v18.8h}, [x3]
        add  x5, x0, #1020
        st1  {v24.h}[2], [x5], x7
        st1  {v25.h}[2], [x5], x7
        st1  {v26.h}[2], [x5]
        add  x3, x0, #1026
        st3  {v19.8h, v20.8h, v21.8h}, [x3]
        add  x5, x0, #1074
        st1  {v24.h}[3], [x5], x7
        st1  {v25.h}[3], [x5], x7
        st1  {v26.h}[3], [x5]
        ldr q0, [x1, #160]
        ldr q1, [x1, #416]
        ldr q2, [x1, #672]
        ldr q3, [x1, #928]
        ldr q4, [x1, #1184]
        ldr q5, [x1, #1440]
        zip1 v16.2d, v0.2d, v1.2d
        zip2 v19.2d, v0.2d, v1.2d
        zip1 v17.2d, v2.2d, v3.2d
        zip2 v20.2d, v2.2d, v3.2d
        zip1 v18.2d, v4.2d, v5.2d
        zip2 v21.2d, v4.2d, v5.2d
        add  x3, x0, #1080
        st3  {v16.8h, v17.8h, v18.8h}, [x3]
        add  x5, x0, #1128
        st1  {v24.h}[4], [x5], x7
        st1  {v25.h}[4], [x5], x7
        st1  {v26.h}[4], [x5]
        add  x3, x0, #1134
        st3  {v19.8h, v20.8h, v21.8h}, [x3]
        add  x5, x0, #1182
        st1  {v24.h}[5], [x5], x7
        st1  {v25.h}[5], [x5], x7
        st1  {v26.h}[5], [x5]
        ldr q0, [x1, #176]
        ldr q1, [x1, #432]
        ldr q2, [x1, #688]
        ldr q3, [x1, #944]
        ldr q4, [x1, #1200]
        ldr q5, [x1, #1456]
        zip1 v16.2d, v0.2d, v1.2d
        zip2 v19.2d, v0.2d, v1.2d
        zip1 v17.2d, v2.2d, v3.2d
        zip2 v20.2d, v2.2d, v3.2d
        zip1 v18.2d, v4.2d, v5.2d
        zip2 v21.2d, v4.2d, v5.2d
        add  x3, x0, #1188
        st3  {v16.8h, v17.8h, v18.8h}, [x3]
        add  x5, x0, #1236
        st1  {v24.h}[6], [x5], x7
        st1  {v25.h}[6], [x5], x7
        st1  {v26.h}[6], [x5]
        add  x3, x0, #1242
        st3  {v19.8h, v20.8h, v21.8h}, [x3]
        add  x5, x0, #1290
        st1  {v24.h}[7], [x5], x7
        st1  {v25.h}[7], [x5], x7
        st1  {v26.h}[7], [x5]
rp2_slothy_end:
rp3_slothy_start:
        ldr q24, [x2, #48]
        ldr q25, [x2, #112]
        ldr q26, [x2, #176]
        ldr q0, [x1, #192]
        ldr q1, [x1, #448]
        ldr q2, [x1, #704]
        ldr q3, [x1, #960]
        ldr q4, [x1, #1216]
        ldr q5, [x1, #1472]
        zip1 v16.2d, v0.2d, v1.2d
        zip2 v19.2d, v0.2d, v1.2d
        zip1 v17.2d, v2.2d, v3.2d
        zip2 v20.2d, v2.2d, v3.2d
        zip1 v18.2d, v4.2d, v5.2d
        zip2 v21.2d, v4.2d, v5.2d
        add  x3, x0, #1296
        st3  {v16.8h, v17.8h, v18.8h}, [x3]
        add  x5, x0, #1344
        st1  {v24.h}[0], [x5], x7
        st1  {v25.h}[0], [x5], x7
        st1  {v26.h}[0], [x5]
        add  x3, x0, #1350
        st3  {v19.8h, v20.8h, v21.8h}, [x3]
        add  x5, x0, #1398
        st1  {v24.h}[1], [x5], x7
        st1  {v25.h}[1], [x5], x7
        st1  {v26.h}[1], [x5]
        ldr q0, [x1, #208]
        ldr q1, [x1, #464]
        ldr q2, [x1, #720]
        ldr q3, [x1, #976]
        ldr q4, [x1, #1232]
        ldr q5, [x1, #1488]
        zip1 v16.2d, v0.2d, v1.2d
        zip2 v19.2d, v0.2d, v1.2d
        zip1 v17.2d, v2.2d, v3.2d
        zip2 v20.2d, v2.2d, v3.2d
        zip1 v18.2d, v4.2d, v5.2d
        zip2 v21.2d, v4.2d, v5.2d
        add  x3, x0, #1404
        st3  {v16.8h, v17.8h, v18.8h}, [x3]
        add  x5, x0, #1452
        st1  {v24.h}[2], [x5], x7
        st1  {v25.h}[2], [x5], x7
        st1  {v26.h}[2], [x5]
        add  x3, x0, #1458
        st3  {v19.8h, v20.8h, v21.8h}, [x3]
        add  x5, x0, #1506
        st1  {v24.h}[3], [x5], x7
        st1  {v25.h}[3], [x5], x7
        st1  {v26.h}[3], [x5]
        ldr q0, [x1, #224]
        ldr q1, [x1, #480]
        ldr q2, [x1, #736]
        ldr q3, [x1, #992]
        ldr q4, [x1, #1248]
        ldr q5, [x1, #1504]
        zip1 v16.2d, v0.2d, v1.2d
        zip2 v19.2d, v0.2d, v1.2d
        zip1 v17.2d, v2.2d, v3.2d
        zip2 v20.2d, v2.2d, v3.2d
        zip1 v18.2d, v4.2d, v5.2d
        zip2 v21.2d, v4.2d, v5.2d
        add  x3, x0, #1512
        st3  {v16.8h, v17.8h, v18.8h}, [x3]
        add  x5, x0, #1560
        st1  {v24.h}[4], [x5], x7
        st1  {v25.h}[4], [x5], x7
        st1  {v26.h}[4], [x5]
        add  x3, x0, #1566
        st3  {v19.8h, v20.8h, v21.8h}, [x3]
        add  x5, x0, #1614
        st1  {v24.h}[5], [x5], x7
        st1  {v25.h}[5], [x5], x7
        st1  {v26.h}[5], [x5]
        ldr q0, [x1, #240]
        ldr q1, [x1, #496]
        ldr q2, [x1, #752]
        ldr q3, [x1, #1008]
        ldr q4, [x1, #1264]
        ldr q5, [x1, #1520]
        zip1 v16.2d, v0.2d, v1.2d
        zip2 v19.2d, v0.2d, v1.2d
        zip1 v17.2d, v2.2d, v3.2d
        zip2 v20.2d, v2.2d, v3.2d
        zip1 v18.2d, v4.2d, v5.2d
        zip2 v21.2d, v4.2d, v5.2d
        add  x3, x0, #1620
        st3  {v16.8h, v17.8h, v18.8h}, [x3]
        add  x5, x0, #1668
        st1  {v24.h}[6], [x5], x7
        st1  {v25.h}[6], [x5], x7
        st1  {v26.h}[6], [x5]
        add  x3, x0, #1674
        st3  {v19.8h, v20.8h, v21.8h}, [x3]
        add  x5, x0, #1722
        st1  {v24.h}[7], [x5], x7
        st1  {v25.h}[7], [x5], x7
        st1  {v26.h}[7], [x5]
rp3_slothy_end:
    ret
