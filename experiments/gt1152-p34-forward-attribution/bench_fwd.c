/* P34 -- where the forward transform's cycles actually go.
 *
 * Measures, on the same core in one session:
 *   - official poly_ntt (in-place, one call)
 *   - GT ntt_asm whole, and each of its three stages separately
 *   - the issue-limited floor for each side's exact multiply multiset
 *
 * Each candidate is measured by min over alternating interleaved passes, so a
 * frequency excursion cannot land on one candidate only.
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <linux/perf_event.h>
#include <sys/syscall.h>
#include <sys/ioctl.h>

static int fd;
static uint64_t rd(void) { uint64_t v; if (read(fd, &v, 8) != 8) _exit(3); return v; }

/* official */
void poly_ntt(int16_t *r);
/* GT */
void ntt_asm(int16_t *out, const int16_t *in);
void ntt_top_asm(int16_t *scratch, const int16_t *in);
void ntt_tail_asm(int16_t *p, const int16_t *q);
void ntt9_asm(int16_t *out, const int16_t *scratch);

static int16_t in[1152] __attribute__((aligned(64)));
static int16_t out[1152] __attribute__((aligned(64)));
static int16_t scr[1152] __attribute__((aligned(64)));   /* 2304 bytes */
static int16_t offbuf[1152] __attribute__((aligned(64)));

/* ---- issue-floor probes and the ntt9 trampoline live in probes.S ---- */
void ntt9_probe(int16_t *out, const int16_t *scr);
void floor_gt_asm(void);
void floor_off_asm(void);
void floor_top_asm(int16_t *w, const int16_t *r);

/* ---- candidates ---- */
static void c_off(void)      { memcpy(offbuf, in, sizeof in); poly_ntt(offbuf); }
static void c_off_nocopy(void){ poly_ntt(offbuf); }
static void c_gt(void)       { ntt_asm(out, in); }
static void c_gt_top(void)   { ntt_top_asm(scr, in); }
static void c_gt_tail(void)  { ntt_tail_asm(scr + 1024, scr + 1024); }
static void c_gt_ntt9(void)  { ntt9_probe(out, scr); }
static void c_memcpy(void)   { memcpy(offbuf, in, sizeof in); }
static void c_empty(void)    { __asm__ volatile("" ::: "memory"); }
static void c_floor_top(void){ floor_top_asm(scr, in); }

struct cand { const char *name; void (*f)(void); double best; };
static struct cand C[] = {
    {"empty loop body",                                 c_empty,       1e18},
    {"memcpy 2304B",                                    c_memcpy,      1e18},
    {"official poly_ntt (in place)",                    c_off_nocopy,  1e18},
    {"official poly_ntt + memcpy",                      c_off,         1e18},
    {"GT ntt_asm (whole)",                              c_gt,          1e18},
    {"GT   ntt_top_asm",                                c_gt_top,      1e18},
    {"GT   ntt_tail_asm",                               c_gt_tail,     1e18},
    {"GT   ntt9_asm (via d8-d15 trampoline)",           c_gt_ntt9,     1e18},
    {"floor: GT multiply multiset (1880 ops)",          floor_gt_asm,  1e18},
    {"floor: official multiply multiset (2088 ops)",    floor_off_asm, 1e18},
    {"floor: ntt_top instruction mix (16 iters)",        c_floor_top,   1e18},
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
    for (int i = 0; i < 1152; i++) {
        s ^= s << 13; s ^= s >> 7; s ^= s << 17;
        in[i] = (int16_t)((int)(s % 7) - 3);          /* [-3,4] contract */
    }
    memcpy(offbuf, in, sizeof in);
    ntt_top_asm(scr, in);                              /* give ntt_tail/ntt9 real data */

    for (int i = 0; i < NC; i++) for (int w = 0; w < 200; w++) C[i].f();

    const int R = 2000, PASSES = 30;
    for (int p = 0; p < PASSES; p++)
        for (int i = 0; i < NC; i++) {
            double v = one(C[i].f, R);
            if (v < C[i].best) C[i].best = v;
        }

    double e = C[0].best;
    printf("empty-loop floor subtracted: %.1f cycles\n\n", e);
    for (int i = 1; i < NC; i++)
        printf("  %-50s %9.1f\n", C[i].name, C[i].best - e);

    double off = C[2].best - e, gt = C[4].best - e;
    double top = C[5].best - e, tail = C[6].best - e, n9 = C[7].best - e;
    double fgt = C[8].best - e, foff = C[9].best - e;
    printf("\n--- attribution ---\n");
    printf("  GT stages sum          %9.1f   (top %.1f + tail %.1f + ntt9 %.1f)\n",
           top + tail + n9, top, tail, n9);
    printf("  GT ntt_asm whole       %9.1f   wrapper cost %.1f\n", gt, gt - (top + tail + n9));
    printf("  official               %9.1f\n", off);
    printf("  measured delta         %9.1f   (%.2f%%)\n", off - gt, 100.0 * (gt - off) / off);
    printf("\n  GT  multiply floor     %9.1f   ntt9 vs floor  %5.1f%%   whole vs floor %5.1f%%\n",
           fgt, 100.0 * fgt * (1800.0 / 1880.0) / n9, 100.0 * fgt / gt);
    printf("  off multiply floor     %9.1f   whole vs floor %5.1f%%\n", foff, 100.0 * foff / off);
    printf("  predicted delta from multiply count alone  %9.1f\n", foff - fgt);
    printf("  overhead above own floor:  GT %.1f   official %.1f\n", gt - fgt, off - foff);
    double ftop = C[10].best - e;
    printf("\n  ntt_top   %7.1f   floor %7.1f   %5.1f%% of floor   headroom %6.1f/call\n",
           top, ftop, 100.0 * ftop / top, top - ftop);
    printf("  ntt9      %7.1f   floor %7.1f   %5.1f%% of floor   headroom %6.1f/call\n",
           n9, 3600.0 * (fgt / 3760.0), 100.0 * 3600.0 * (fgt / 3760.0) / n9, n9 - 3600.0 * (fgt / 3760.0));
    return 0;
}
