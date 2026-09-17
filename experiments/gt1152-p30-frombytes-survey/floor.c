/* The exact per-pair instruction mix of frombytes, all chains independent.
 * Three variants isolate what the permutation and the V1-pinned shift cost. */
#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <unistd.h>
#include <linux/perf_event.h>
#include <sys/syscall.h>
#include <sys/ioctl.h>
static int fd;
static uint64_t rd(void){uint64_t v;if(read(fd,&v,8)!=8)_exit(3);return v;}
static uint8_t buf[8192];
#define R8(op) op(0) op(1) op(2) op(3) op(4) op(5) op(6) op(7)
#define R4(op) op(0) op(1) op(2) op(3)
#define TBL(i)  "tbl v"#i".16b, {v13.16b}, v12.16b\n"
#define USHR(i) "ushr v"#i".4s, v"#i".4s, #12\n"
#define UZP(i)  "uzp1 v"#i".8h, v"#i".8h, v14.8h\n"
#define AND(i)  "and v"#i".16b, v"#i".16b, v14.16b\n"
#define UMAX(i) "umax v"#i".8h, v"#i".8h, v14.8h\n"
#define USHL(i) "ushl v"#i".8h, v"#i".8h, v15.8h\n"
#define TRN1(i) "trn1 v"#i".8h, v"#i".8h, v14.8h\n"
#define TRN2(i) "trn2 v"#i".4s, v"#i".4s, v14.4s\n"
#define ZIP1(i) "zip1 v"#i".2d, v"#i".2d, v14.2d\n"
#define ZIP2(i) "zip2 v"#i".2d, v"#i".2d, v14.2d\n"
#define LDR(i)  "ldr q"#i", [%1, #" LD##i "]\n"
#define LD0 "0"
#define LD1 "16"
#define LD2 "32"
#define LD3 "48"
#define LD4 "64"
#define LD5 "80"
#define LD6 "96"
#define LD7 "112"
#define STR(i)  "str q"#i", [%1, #" ST##i "]\n"
#define ST0 "256"
#define ST1 "272"
#define ST2 "288"
#define ST3 "304"
#define ST4 "320"
#define ST5 "336"
#define ST6 "352"
#define ST7 "368"
#define LDH(i)  "ldrh w10, [%2, #" LD##i "]\n"

#define CLOB "v0","v1","v2","v3","v4","v5","v6","v7","v12","v13","v14","v15","w10","memory","cc"
#define RUN(name, body, per) do { int n=200000; \
    for(int w=0;w<2;w++){ uint64_t a=rd(); \
      __asm__ volatile("1:\n" body "subs %w0, %w0, #1\nb.ne 1b\n" \
        : "+r"(n) : "r"(p), "r"(q) : CLOB); uint64_t b=rd(); n=200000; \
      if(w) printf("  %-42s %6.2f cycles/pair  x18 = %5.0f\n", name, \
                   (double)(b-a)/200000.0, (double)(b-a)/200000.0*18); } } while(0)

#define UNPACK  R8(LDR) R8(TBL) R8(USHR) R8(UZP) R8(AND) R8(UMAX) R8(LDH)
#define TRANSPOSE R8(TRN1) R8(TRN2) R4(ZIP1) R4(ZIP2)
#define STORES  R8(STR)

int main(void){
    struct perf_event_attr at={0}; at.size=sizeof at; at.type=PERF_TYPE_HARDWARE;
    at.config=PERF_COUNT_HW_CPU_CYCLES; at.exclude_kernel=1; at.exclude_hv=1;
    fd=syscall(__NR_perf_event_open,&at,0,-1,-1,0);
    if(fd<0){perror("perf");return 2;}
    ioctl(fd,PERF_EVENT_IOC_ENABLE,0);
    uint8_t *p=buf, *q=buf+4096;
    printf("issue-limited floors, chains independent\n\n");
    RUN("full frombytes mix", UNPACK TRANSPOSE STORES, 1);
    RUN("  without the 24-op transpose", UNPACK STORES, 1);
    RUN("  without the 8 V1-pinned ushr", R8(LDR) R8(TBL) R8(UZP) R8(AND) R8(UMAX) R8(LDH) TRANSPOSE STORES, 1);
    RUN("  without the 8 offset-table loads", R8(LDR) R8(TBL) R8(USHR) R8(UZP) R8(AND) R8(UMAX) TRANSPOSE STORES, 1);
    printf("\n");
    RUN("proposed: one tbl + per-lane ushl + and",
         R8(LDR) R8(TBL) R8(USHL) R8(AND) R8(UMAX) R8(LDH) TRANSPOSE STORES, 1);
    printf("\nmeasured frombytes: 723 standalone (P19), 731/call in the KEM\n");
    return 0;
}
