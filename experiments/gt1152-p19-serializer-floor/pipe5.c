/* Floor for the tbl4 scheme: no transpose at all.
 * 16 canonical (add+umin), 8 zip widen, 8 umlal/umlal2, 8 tbl4, 8 ldr, 16 st. */
#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <unistd.h>
#include <linux/perf_event.h>
#include <sys/syscall.h>
#include <sys/ioctl.h>
static int fd;
static uint64_t rd(void){uint64_t v; if(read(fd,&v,8)!=8)_exit(3); return v;}
static uint8_t buf[8192];
#define R8(op) op(0) op(1) op(2) op(3) op(4) op(5) op(6) op(7)
#define R4(op) op(0) op(1) op(2) op(3)
#define ADDV(i) "add v"#i".8h, v"#i".8h, v14.8h\n"
#define UMIN(i) "umin v"#i".8h, v"#i".8h, v14.8h\n"
#define ZP1(i)  "zip1 v"#i".8h, v"#i".8h, v14.8h\n"
#define ZP2(i)  "zip2 v"#i".8h, v"#i".8h, v14.8h\n"
#define UML1(i) "umlal v"#i".4s, v13.4h, v15.h[0]\n"
#define UML2(i) "umlal2 v"#i".4s, v13.8h, v15.h[0]\n"
#define TBL4(i) "tbl v"#i".16b, {v16.16b, v17.16b, v18.16b, v19.16b}, v12.16b\n"
#define LDR(i)  "ldr q"#i", [%1, #" LD##i "]\n"
#define LD0 "0"
#define LD1 "16"
#define LD2 "32"
#define LD3 "48"
#define LD4 "64"
#define LD5 "80"
#define LD6 "96"
#define LD7 "112"
#define STRD(i) "str d"#i", [%1, #" ST##i "]\n"
#define ST0 "128"
#define ST1 "192"
#define ST2 "256"
#define ST3 "320"
#define ST4 "384"
#define ST5 "448"
#define ST6 "512"
#define ST7 "576"
#define ST1S(i) "st1 {v"#i".s}[2], [%2]\n"
int main(void){
    struct perf_event_attr at={0}; at.size=sizeof at; at.type=PERF_TYPE_HARDWARE;
    at.config=PERF_COUNT_HW_CPU_CYCLES; at.exclude_kernel=1; at.exclude_hv=1;
    fd=syscall(__NR_perf_event_open,&at,0,-1,-1,0);
    if(fd<0){perror("perf");return 2;}
    ioctl(fd,PERF_EVENT_IOC_ENABLE,0);
    uint8_t *p=buf,*q=buf+4096; int n;
    for(int w=0;w<2;w++){
        n=200000; uint64_t a=rd();
        __asm__ volatile("1:\n"
            R8(ADDV) R8(UMIN) R4(ZP1) R4(ZP2) R4(UML1) R4(UML2)
            R8(TBL4) R8(LDR) R8(STRD) R8(ST1S)
            "subs %w0, %w0, #1\nb.ne 1b\n"
            : "+r"(n) : "r"(p), "r"(q)
            : "v0","v1","v2","v3","v4","v5","v6","v7","v12","v13","v14","v15",
              "v16","v17","v18","v19","memory","cc");
        uint64_t b=rd();
        if(w){ double c=(double)(b-a)/200000.0;
            printf("tbl4 scheme, one pair : %6.2f cycles   x18 = %4.0f\n", c, c*18);
            printf("transpose scheme      :  44.00 cycles   x18 =  792\n");
            printf("measured tobytes_small:                 x18 =  878\n"); }
    }
    return 0;
}
