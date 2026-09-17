/* Cost of multi-source TBL on the A76: can one tbl4 replace a transpose? */
#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <unistd.h>
#include <linux/perf_event.h>
#include <sys/syscall.h>
#include <sys/ioctl.h>
static int fd;
static uint64_t rd(void){uint64_t v; if(read(fd,&v,8)!=8)_exit(3); return v;}
#define M8(op) op(0) op(1) op(2) op(3) op(4) op(5) op(6) op(7)
#define T1(i) "tbl v"#i".16b, {v16.16b}, v24.16b\n"
#define T2(i) "tbl v"#i".16b, {v16.16b, v17.16b}, v24.16b\n"
#define T3(i) "tbl v"#i".16b, {v16.16b, v17.16b, v18.16b}, v24.16b\n"
#define T4(i) "tbl v"#i".16b, {v16.16b, v17.16b, v18.16b, v19.16b}, v24.16b\n"
#define BODY(x) "1:\n" x "subs %w0, %w0, #1\nb.ne 1b\n"
#define RUN(name,x,per) do { int n=200000; \
  for(int w=0;w<2;w++){ uint64_t a=rd(); \
    __asm__ volatile(BODY(x):"+r"(n)::"v0","v1","v2","v3","v4","v5","v6","v7", \
      "v16","v17","v18","v19","v24","cc"); uint64_t b=rd(); n=200000; \
    if(w) printf("  %-22s %6.3f cycles per op\n", name, (double)(b-a)/200000.0/(per)); } } while(0)
int main(void){
    struct perf_event_attr at={0}; at.size=sizeof at; at.type=PERF_TYPE_HARDWARE;
    at.config=PERF_COUNT_HW_CPU_CYCLES; at.exclude_kernel=1; at.exclude_hv=1;
    fd=syscall(__NR_perf_event_open,&at,0,-1,-1,0);
    if(fd<0){perror("perf");return 2;}
    ioctl(fd,PERF_EVENT_IOC_ENABLE,0);
    printf("8 independent chains\n\n");
    RUN("tbl, 1 source",  M8(T1), 8);
    RUN("tbl, 2 sources", M8(T2), 8);
    RUN("tbl, 3 sources", M8(T3), 8);
    RUN("tbl, 4 sources", M8(T4), 8);
    return 0;
}
