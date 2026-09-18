/* P37 -- did flattening the driver actually pay? */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <linux/perf_event.h>
#include <sys/syscall.h>
#include <sys/ioctl.h>
#include "params.h"
#include "inverse_tables.h"
#include "inverse16_tables.h"

static int fd;
static uint64_t rd(void) { uint64_t v; if (read(fd, &v, 8) != 8) _exit(3); return v; }

void invntt_ternary_asm(int16_t *, const int16_t *, const int16_t *, const int16_t *, const int16_t *, const int16_t *);
void invntt_ternary_ref(int16_t *, const int16_t *, const int16_t *, const int16_t *, const int16_t *, const int16_t *);
void skel_ref(int16_t *, const int16_t *, const int16_t *, const int16_t *, const int16_t *, const int16_t *);
void skel_flat(int16_t *, const int16_t *, const int16_t *, const int16_t *, const int16_t *, const int16_t *);

#define ARGS &invntt9_constants[0][0][0][0][0], &invntt16_constants[0][0], \
             &invntt16_main_constants[0][0], &invntt16_tail_constants[0][0]
static int16_t in[NTRUPLUS_N] __attribute__((aligned(64)));
static int16_t out[NTRUPLUS_N] __attribute__((aligned(64)));

static void c_ref(void)   { invntt_ternary_ref(out, in, ARGS); }
static void c_flat(void)  { invntt_ternary_asm(out, in, ARGS); }
static void c_sref(void)  { skel_ref(out, in, ARGS); }
static void c_sflat(void) { skel_flat(out, in, ARGS); }
static void c_empty(void) { __asm__ volatile("" ::: "memory"); }

struct cand { const char *name; void (*f)(void); double best; };
static struct cand C[] = {
    {"empty loop body",                   c_empty, 1e18},
    {"driver: loop nest (shipped)",       c_ref,   1e18},
    {"driver: flattened",                 c_flat,  1e18},
    {"  skeleton, loop nest",             c_sref,  1e18},
    {"  skeleton, flattened",             c_sflat, 1e18},
};
#define NC ((int)(sizeof C / sizeof C[0]))

static double one(void (*f)(void), int R)
{ uint64_t a = rd(); for (int i = 0; i < R; i++) f(); return (double)(rd() - a) / R; }

int main(void)
{
    struct perf_event_attr at = {0};
    at.size = sizeof at; at.type = PERF_TYPE_HARDWARE;
    at.config = PERF_COUNT_HW_CPU_CYCLES; at.exclude_kernel = 1; at.exclude_hv = 1;
    fd = syscall(__NR_perf_event_open, &at, 0, -1, -1, 0);
    if (fd < 0) { perror("perf_event_open"); return 2; }
    ioctl(fd, PERF_EVENT_IOC_ENABLE, 0);

    uint64_t s = 88172645463325252ULL;
    for (int i = 0; i < NTRUPLUS_N; i++) {
        s ^= s << 13; s ^= s >> 7; s ^= s << 17;
        in[i] = (int16_t)((int)(s % 4995) - 2497);
    }
    for (int i = 0; i < NC; i++) for (int w = 0; w < 200; w++) C[i].f();
    const int R = 2000, PASSES = 30;
    for (int p = 0; p < PASSES; p++)
        for (int i = 0; i < NC; i++) {
            double v = one(C[i].f, R);
            if (v < C[i].best) C[i].best = v;
        }
    double e = C[0].best;
    for (int i = 1; i < NC; i++) printf("  %-34s %9.1f\n", C[i].name, C[i].best - e);
    double ref = C[1].best - e, flat = C[2].best - e;
    double sref = C[3].best - e, sflat = C[4].best - e;
    printf("\n  skeleton  %.1f -> %.1f   (-%.1f)\n", sref, sflat, sref - sflat);
    printf("  whole     %.1f -> %.1f   (-%.1f, %.2f%%)\n",
           ref, flat, ref - flat, 100.0 * (flat - ref) / ref);
    return 0;
}
