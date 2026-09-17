/* P12 (natural-order scratch) against P18 (permutation in registers). */
#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <linux/perf_event.h>
#include <sys/syscall.h>
#include <sys/ioctl.h>

#define N 1152
#define PB 1728
void tobytes_full_asm(uint8_t*, const int16_t*);
void tobytes_small_asm(uint8_t*, const int16_t*);
int  tobytes_compare_asm(const uint8_t*, const int16_t*);
int  frombytes_asm(int16_t*, const uint8_t*);
void old_tobytes_full_asm(uint8_t*, const int16_t*);
void old_tobytes_small_asm(uint8_t*, const int16_t*);
int  old_tobytes_compare_asm(const uint8_t*, const int16_t*);
int  old_frombytes_asm(int16_t*, const uint8_t*);

static int fd;
static uint64_t rd(void){uint64_t v; if(read(fd,&v,8)!=8)_exit(3); return v;}
static int16_t gt[N], back[N], back2[N];
static uint8_t wire[PB], wire2[PB];
static volatile int sink;

#define BENCH(label, expr) do {                                   \
    for (int i = 0; i < 100; i++) { expr; }                       \
    uint64_t a = rd();                                            \
    for (int i = 0; i < R; i++) { expr; }                         \
    printf("  %-24s %8.1f\n", label, (double)(rd()-a)/R);         \
} while (0)

int main(void){
    struct perf_event_attr at={0}; at.size=sizeof at; at.type=PERF_TYPE_HARDWARE;
    at.config=PERF_COUNT_HW_CPU_CYCLES; at.exclude_kernel=1; at.exclude_hv=1;
    fd=syscall(__NR_perf_event_open,&at,0,-1,-1,0);
    if(fd<0){perror("perf");return 2;}
    ioctl(fd,PERF_EVENT_IOC_ENABLE,0);

    for(int i=0;i<N;i++) gt[i]=(int16_t)((i*37)%3457);

    /* agreement first: the two codecs must be indistinguishable */
    int bad=0;
    old_tobytes_full_asm(wire,gt);  tobytes_full_asm(wire2,gt);
    bad += memcmp(wire,wire2,PB)!=0;
    old_tobytes_small_asm(wire,gt); tobytes_small_asm(wire2,gt);
    bad += memcmp(wire,wire2,PB)!=0;
    bad += (old_frombytes_asm(back,wire)!=frombytes_asm(back2,wire));
    bad += memcmp(back,back2,sizeof back)!=0;
    bad += (old_tobytes_compare_asm(wire,gt)!=tobytes_compare_asm(wire,gt));
    wire[777]^=0x20;
    bad += (old_tobytes_compare_asm(wire,gt)!=tobytes_compare_asm(wire,gt));
    wire[777]^=0x20;
    printf("agreement: %s\n\n", bad? "FAIL":"pass");
    if(bad) return 1;

    const int R=20000;
    printf("cycles per call, %d reps\n\n", R);
    printf("P12, natural-order scratch\n");
    BENCH("tobytes_full",    old_tobytes_full_asm(wire,gt));
    BENCH("tobytes_small",   old_tobytes_small_asm(wire,gt));
    BENCH("tobytes_compare", sink=old_tobytes_compare_asm(wire,gt));
    BENCH("frombytes",       sink=old_frombytes_asm(back,wire));
    printf("\nP18, permutation in registers\n");
    BENCH("tobytes_full",    tobytes_full_asm(wire,gt));
    BENCH("tobytes_small",   tobytes_small_asm(wire,gt));
    BENCH("tobytes_compare", sink=tobytes_compare_asm(wire,gt));
    BENCH("frombytes",       sink=frombytes_asm(back,wire));
    return 0;
}
