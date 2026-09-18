/* P36 -- where the inverse transform's cycles go.
 *
 * P34 closed the forward: its 9.96% static multiply advantage cashed out as
 * 9.04% measured, both sides at the same distance above their issue floor.
 * The inverse does not behave that way.  Static advantage is 11.95% and the
 * measured advantage is 0.3%, so one side is much further from its floor than
 * the other.  This finds out which stage owns the gap.
 */
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

/* official */
void poly_invntt_scale(int16_t *r);
void poly_crepmod3(int16_t *r);
/* GT driver variants, one stage removed each */
typedef void (*inv6)(int16_t *, const int16_t *, const int16_t *,
                     const int16_t *, const int16_t *, const int16_t *);
void inv_full(int16_t *, const int16_t *, const int16_t *, const int16_t *, const int16_t *, const int16_t *);
void inv_no_i9(int16_t *, const int16_t *, const int16_t *, const int16_t *, const int16_t *, const int16_t *);
void inv_no_main(int16_t *, const int16_t *, const int16_t *, const int16_t *, const int16_t *, const int16_t *);
void inv_no_tail(int16_t *, const int16_t *, const int16_t *, const int16_t *, const int16_t *, const int16_t *);
void inv_no_crep(int16_t *, const int16_t *, const int16_t *, const int16_t *, const int16_t *, const int16_t *);
void inv_no_wipe(int16_t *, const int16_t *, const int16_t *, const int16_t *, const int16_t *, const int16_t *);
void inv_skeleton(int16_t *, const int16_t *, const int16_t *, const int16_t *, const int16_t *, const int16_t *);
/* floors */
void floor_inv_gt_asm(void);
void floor_inv_off_asm(void);
void floor_i9_asm(int16_t *w, const int16_t *r);      /* mix x16 */
void floor_i16_asm(int16_t *w, const int16_t *r);     /* mix x8  */

static int16_t in[NTRUPLUS_N] __attribute__((aligned(64)));
static int16_t out[NTRUPLUS_N] __attribute__((aligned(64)));
static int16_t offbuf[NTRUPLUS_N] __attribute__((aligned(64)));

#define RUN(fn) fn(out, in, &invntt9_constants[0][0][0][0][0], \
                   &invntt16_constants[0][0], &invntt16_main_constants[0][0], \
                   &invntt16_tail_constants[0][0])

static void c_full(void)      { RUN(inv_full); }
static void c_no_i9(void)     { RUN(inv_no_i9); }
static void c_no_main(void)   { RUN(inv_no_main); }
static void c_no_tail(void)   { RUN(inv_no_tail); }
static void c_no_crep(void)   { RUN(inv_no_crep); }
static void c_no_wipe(void)   { RUN(inv_no_wipe); }
static void c_skeleton(void)  { RUN(inv_skeleton); }
static void c_off(void)       { poly_invntt_scale(offbuf); poly_crepmod3(offbuf); }
static void c_off_inv(void)   { poly_invntt_scale(offbuf); }
static void c_off_crep(void)  { poly_crepmod3(offbuf); }
/* the probes reach offset 2256 on both pointers; give them room */
static int16_t pad[2048] __attribute__((aligned(64)));
static int16_t src[2048] __attribute__((aligned(64)));
static void c_fi9(void)       { floor_i9_asm(pad, src); }
static void c_fi16(void)      { floor_i16_asm(pad, src); }
static void c_empty(void)     { __asm__ volatile("" ::: "memory"); }

struct cand { const char *name; void (*f)(void); double best; };
static struct cand C[] = {
    {"empty loop body",                                c_empty,            1e18},
    {"official invntt_scale + crepmod3",               c_off,              1e18},
    {"  official poly_invntt_scale",                   c_off_inv,          1e18},
    {"  official poly_crepmod3",                       c_off_crep,         1e18},
    {"GT invntt_ternary_asm (whole)",                  c_full,             1e18},
    {"  minus packed_i9 x16",                          c_no_i9,            1e18},
    {"  minus invntt16_asm x8",                        c_no_main,          1e18},
    {"  minus invntt16_tail_asm",                      c_no_tail,          1e18},
    {"  minus crepmod3_ternary_asm",                   c_no_crep,          1e18},
    {"  minus the 2304-byte wipe",                     c_no_wipe,          1e18},
    {"  driver skeleton only (all stages removed)",    c_skeleton,         1e18},
    {"floor: GT multiply multiset (2557 ops)",         floor_inv_gt_asm,   1e18},
    {"floor: official multiply multiset (2904 ops)",   floor_inv_off_asm,  1e18},
    {"floor: packed_i9 instruction mix x16",           c_fi9,              1e18},
    {"floor: invntt16_asm instruction mix x8",         c_fi16,             1e18},
};
#define NC ((int)(sizeof C / sizeof C[0]))

static double one(void (*f)(void), int R)
{
    uint64_t a = rd();
    for (int i = 0; i < R; i++) f();
    return (double)(rd() - a) / R;
}

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
        in[i] = (int16_t)((int)(s % 4915) - 2457);   /* inside the 2497 contract */
    }
    memcpy(offbuf, in, sizeof in);
    for (int i = 0; i < 2048; i++) src[i] = in[i % NTRUPLUS_N];

    for (int i = 0; i < NC; i++) for (int w = 0; w < 200; w++) C[i].f();
    const int R = 2000, PASSES = 30;
    for (int p = 0; p < PASSES; p++)
        for (int i = 0; i < NC; i++) {
            double v = one(C[i].f, R);
            if (v < C[i].best) C[i].best = v;
        }

    double e = C[0].best;
    for (int i = 1; i < NC; i++)
        printf("  %-48s %9.1f\n", C[i].name, C[i].best - e);

    double off = C[1].best - e, gt = C[4].best - e, skel = C[10].best - e;
    double i9   = gt - (C[5].best - e);
    double main = gt - (C[6].best - e);
    double tail = gt - (C[7].best - e);
    double crep = gt - (C[8].best - e);
    double wipe = gt - (C[9].best - e);
    double fgt = C[11].best - e, foff = C[12].best - e;

    printf("\n--- GT stage attribution ---\n");
    printf("  packed_i9 x16          %8.1f   (%6.1f each, floor %.1f)\n", i9, i9/16, 57*2.0);
    printf("  invntt16_asm x8        %8.1f   (%6.1f each, floor %.1f)\n", main, main/8, 151*2.0);
    printf("  invntt16_tail_asm      %8.1f   (floor %.1f)\n", tail, 149*2.0);
    printf("  crepmod3_ternary_asm   %8.1f   (floor %.1f)\n", crep, 288*2.0);
    printf("  the 2304-byte wipe     %8.1f\n", wipe);
    printf("  driver skeleton        %8.1f   (address arithmetic, 26 bl/ret, prologue)\n", skel);
    printf("  stages + skeleton      %8.1f   vs whole %8.1f\n",
           i9 + main + tail + crep + wipe + skel, gt);

    printf("\n--- versus the official ---\n");
    printf("  GT       %8.1f   floor %8.1f   %5.1f%% of floor   overhead %7.1f\n",
           gt, fgt, 100.0*fgt/gt, gt - fgt);
    printf("  official %8.1f   floor %8.1f   %5.1f%% of floor   overhead %7.1f\n",
           off, foff, 100.0*foff/off, off - foff);
    printf("  static advantage 11.95%%, measured %.2f%%\n", 100.0*(gt-off)/off);
    printf("  if GT reached the official's efficiency: %.1f  (a further %.1f)\n",
           fgt / (foff/off), gt - fgt / (foff/off));

    double fi9 = C[13].best - e, fi16 = C[14].best - e;
    printf("\n--- the two big stages against their INSTRUCTION-MIX floor ---\n");
    printf("  packed_i9 x16      %8.1f   mix floor %8.1f   %5.1f%%   headroom %7.1f\n",
           i9, fi9, 100.0*fi9/i9, i9 - fi9);
    printf("  invntt16_asm x8    %8.1f   mix floor %8.1f   %5.1f%%   headroom %7.1f\n",
           main, fi16, 100.0*fi16/main, main - fi16);
    printf("  (multiply-only floors were %.1f and %.1f, i.e. not the binding resource)\n",
           16*57*2.0, 8*151*2.0);
    return 0;
}
