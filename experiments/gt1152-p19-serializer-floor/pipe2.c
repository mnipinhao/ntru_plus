/* True A76 throughput of the exact operations the codec issues. */
#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <unistd.h>
#include <linux/perf_event.h>
#include <sys/syscall.h>
#include <sys/ioctl.h>
static int fd;
static uint64_t rd(void){uint64_t v; if(read(fd,&v,8)!=8)_exit(3); return v;}
#define M12(op) op(0) op(1) op(2) op(3) op(4) op(5) op(6) op(7) op(8) op(9) op(10) op(11)
#define TBL(i)  "tbl v"#i".16b, {v28.16b}, v29.16b\n"
#define TRN(i)  "trn1 v"#i".8h, v"#i".8h, v28.8h\n"
#define ZIP(i)  "zip1 v"#i".8h, v"#i".8h, v28.8h\n"
#define UMIN(i) "umin v"#i".8h, v"#i".8h, v28.8h\n"
#define UML(i)  "umlal2 v"#i".4s, v28.8h, v15.h[0]\n"
#define ADD(i)  "add v"#i".8h, v"#i".8h, v28.8h\n"
#define UZP(i)  "uzp1 v"#i".8h, v"#i".8h, v28.8h\n"
#define USH(i)  "ushr v"#i".4s, v"#i".4s, #12\n"
#define AND(i)  "and v"#i".16b, v"#i".16b, v28.16b\n"
#define CMHI(i) "cmhi v"#i".8h, v"#i".8h, v28.8h\n"
#define BODY(x) "1:\n" x "subs %w0, %w0, #1\nb.ne 1b\n"
#define RUN(name, x, per) do { int n=200000; \
    for(int w=0;w<2;w++){ uint64_t a=rd(); \
      __asm__ volatile(BODY(x) : "+r"(n) :: "v0","v1","v2","v3","v4","v5","v6","v7", \
        "v8","v9","v10","v11","v15","v28","v29","cc"); uint64_t b=rd(); n=200000; \
      if(w) printf("  %-30s %6.3f\n", name, (double)(b-a)/200000.0/(per)); } } while(0)
int main(void){
    struct perf_event_attr at={0}; at.size=sizeof at; at.type=PERF_TYPE_HARDWARE;
    at.config=PERF_COUNT_HW_CPU_CYCLES; at.exclude_kernel=1; at.exclude_hv=1;
    fd=syscall(__NR_perf_event_open,&at,0,-1,-1,0);
    if(fd<0){perror("perf");return 2;}
    ioctl(fd,PERF_EVENT_IOC_ENABLE,0);
    printf("cycles per op, 12 independent chains\n\n");
    RUN("tbl (1 source reg)",  M12(TBL), 12);
    RUN("trn1",                M12(TRN), 12);
    RUN("zip1",                M12(ZIP), 12);
    RUN("uzp1",                M12(UZP), 12);
    RUN("umin",                M12(UMIN), 12);
    RUN("add",                 M12(ADD), 12);
    RUN("and",                 M12(AND), 12);
    RUN("cmhi",                M12(CMHI), 12);
    RUN("ushr",                M12(USH), 12);
    RUN("umlal2",              M12(UML), 12);
    printf("\nmixes (cycles per op over the whole body)\n");
    RUN("tbl x12 + trn1 x12",  M12(TBL) M12(TRN), 24);
    RUN("umlal2 x12 + trn1 x12", M12(UML) M12(TRN), 24);
    RUN("ushr x12 + and x12",  M12(USH) M12(AND), 24);
    return 0;
}
