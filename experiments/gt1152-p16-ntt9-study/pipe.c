/* Does the A76 really issue one vector multiply every 2 cycles, on one pipe? */
#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <unistd.h>
#include <linux/perf_event.h>
#include <sys/syscall.h>
#include <sys/ioctl.h>
static int fd;
static uint64_t rd(void){uint64_t v; if(read(fd,&v,8)!=8)_exit(3); return v;}

/* 12 independent chains, so latency never binds -- this measures throughput. */
#define M12(op) op(0) op(1) op(2) op(3) op(4) op(5) op(6) op(7) op(8) op(9) op(10) op(11)
#define SQ(i) "sqrdmulh v"#i".8h, v"#i".8h, v30.8h\n"
#define MU(i) "mul v"#i".8h, v"#i".8h, v30.8h\n"
#define AD(i) "add v"#i".8h, v"#i".8h, v30.8h\n"
#define TR(i) "trn1 v"#i".8h, v"#i".8h, v30.8h\n"
#define BODY(x) "1:\n" x "subs %w0, %w0, #1\nb.ne 1b\n"

#define RUN(name, x, per)                                                   \
    do { int n = 200000;                                                    \
        for (int w = 0; w < 2; w++) {                                       \
            uint64_t a = rd();                                              \
            __asm__ volatile(BODY(x) : "+r"(n) :: "v0","v1","v2","v3","v4", \
                "v5","v6","v7","v8","v9","v10","v11","v30","cc");           \
            uint64_t b = rd(); n = 200000;                                  \
            if (w) printf("  %-28s %6.3f cycles per op\n", name,            \
                          (double)(b-a)/200000.0/(per));                    \
        } } while (0)

int main(void){
    struct perf_event_attr at={0}; at.size=sizeof at; at.type=PERF_TYPE_HARDWARE;
    at.config=PERF_COUNT_HW_CPU_CYCLES; at.exclude_kernel=1; at.exclude_hv=1;
    fd=syscall(__NR_perf_event_open,&at,0,-1,-1,0);
    if(fd<0){perror("perf");return 2;}
    ioctl(fd,PERF_EVENT_IOC_ENABLE,0);
    printf("throughput, 12 independent chains per iteration\n\n");
    RUN("sqrdmulh x12",            M12(SQ), 12);
    RUN("mul x12",                 M12(MU), 12);
    RUN("add x12",                 M12(AD), 12);
    RUN("trn1 x12",                M12(TR), 12);
    RUN("sqrdmulh x12 + add x12",  M12(SQ) M12(AD), 12);   /* per multiply */
    RUN("sqrdmulh x12 + trn1 x12", M12(SQ) M12(TR), 12);   /* per multiply */
    return 0;
}
