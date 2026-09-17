/* The exact per-pair instruction mix of tobytes_small, all chains independent.
 * This is the issue-limited floor: same ops, same counts, zero dependencies. */
#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <unistd.h>
#include <linux/perf_event.h>
#include <sys/syscall.h>
#include <sys/ioctl.h>
static int fd;
static uint64_t rd(void){uint64_t v; if(read(fd,&v,8)!=8)_exit(3); return v;}
static uint8_t buf[4096];

/* 12 zip1, 4 zip2, 8 trn1, 8 trn2, 8 umin, 8 add, 8 tbl, 8 umlal2 = 64 vector
 * ops; plus 8 str d and 8 st1 .s[2], and 8 ldr q. */
#define R8(op)  op(0) op(1) op(2) op(3) op(4) op(5) op(6) op(7)
#define R4(op)  op(0) op(1) op(2) op(3)
#define ZIP1(i) "zip1 v"#i".8h, v"#i".8h, v14.8h\n"
#define ZIP1b(i)"zip1 v"#i".4s, v"#i".4s, v14.4s\n"
#define ZIP2(i) "zip2 v"#i".2d, v"#i".2d, v14.2d\n"
#define TRN1(i) "trn1 v"#i".8h, v"#i".8h, v14.8h\n"
#define TRN2(i) "trn2 v"#i".4s, v"#i".4s, v14.4s\n"
#define UMIN(i) "umin v"#i".8h, v"#i".8h, v14.8h\n"
#define ADDV(i) "add v"#i".8h, v"#i".8h, v14.8h\n"
#define TBL(i)  "tbl v"#i".16b, {v13.16b}, v12.16b\n"
#define UML(i)  "umlal2 v"#i".4s, v13.8h, v15.h[0]\n"
#define LDR(i)  "ldr q"#i", [%1, #" LDOFF##i "]\n"
#define LDOFF0 "0"
#define LDOFF1 "16"
#define LDOFF2 "32"
#define LDOFF3 "48"
#define LDOFF4 "64"
#define LDOFF5 "80"
#define LDOFF6 "96"
#define LDOFF7 "112"
#define STRD(i) "str d"#i", [%1, #" STOFF##i "]\n"
#define STOFF0 "128"
#define STOFF1 "192"
#define STOFF2 "256"
#define STOFF3 "320"
#define STOFF4 "384"
#define STOFF5 "448"
#define STOFF6 "512"
#define STOFF7 "576"
#define ST1S(i) "st1 {v"#i".s}[2], [%2]\n"

int main(void){
    struct perf_event_attr at={0}; at.size=sizeof at; at.type=PERF_TYPE_HARDWARE;
    at.config=PERF_COUNT_HW_CPU_CYCLES; at.exclude_kernel=1; at.exclude_hv=1;
    fd=syscall(__NR_perf_event_open,&at,0,-1,-1,0);
    if(fd<0){perror("perf");return 2;}
    ioctl(fd,PERF_EVENT_IOC_ENABLE,0);
    uint8_t *p = buf, *q = buf + 2048;
    int n;
    for (int w = 0; w < 2; w++) {
        n = 200000;
        uint64_t a = rd();
        __asm__ volatile("1:\n"
            R8(ZIP1) R4(ZIP1b) R4(ZIP2) R8(TRN1) R8(TRN2)
            R8(UMIN) R8(ADDV) R8(TBL) R8(UML)
            R8(LDR) R8(STRD) R8(ST1S)
            "subs %w0, %w0, #1\nb.ne 1b\n"
            : "+r"(n) : "r"(p), "r"(q)
            : "v0","v1","v2","v3","v4","v5","v6","v7","v12","v13","v14","v15","memory","cc");
        uint64_t b = rd();
        if (w) {
            double c = (double)(b-a)/200000.0;
            printf("one pair, issue-limited floor : %6.2f cycles\n", c);
            printf("x18 pairs                     : %6.0f cycles\n", c*18);
            printf("measured tobytes_small        :  878.0 cycles\n");
            printf("utilisation                   : %6.1f%%\n", 100*c*18/878.0);
        }
    }
    return 0;
}
