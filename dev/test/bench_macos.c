/*
 * NTRU+1152 kernel benchmark for macOS/arm64.
 *
 * There is no perf_event here, and PMCCNTR_EL0 is not readable from userspace,
 * so cycles are derived rather than counted: a chain of dependent scalar adds
 * retires exactly one per cycle on every core this would run on, which turns a
 * nanosecond measurement into a clock estimate, and that converts the kernel
 * timings.  The clock is reported so the conversion can be checked.
 *
 * QOS_CLASS_USER_INTERACTIVE biases the thread onto a performance core, which
 * matters on a hybrid part: the E-cores would otherwise produce a different and
 * meaningless number.
 */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#include <pthread.h>
#include <time.h>
#include "base_tables.h"

#define N 1152
#define Q 3457
#ifndef HAVE_M1
#define HAVE_M1 0
#endif

void basemul_rinv_kernel(int16_t *, const int16_t *, const int16_t *, const int16_t *);
#if HAVE_M1
void basemul_rinv_kernel_b(int16_t *, const int16_t *, const int16_t *, const int16_t *);
#endif
void basemul_rinv_asm(int16_t *, const int16_t *, const int16_t *);

static uint64_t now_ns(void) { return clock_gettime_nsec_np(CLOCK_UPTIME_RAW); }

/*
 * One dependent add retires per cycle, so a long chain turns nanoseconds into
 * cycles.  Two unroll factors are measured and differenced, which cancels the
 * loop's own compare and branch: with A adds per iteration costing tA and B
 * costing tB, the clock is (A - B) / (tA - tB) and the overhead drops out.
 */
#define ADD10 "add x9,x9,#1\n add x9,x9,#1\n add x9,x9,#1\n add x9,x9,#1\n add x9,x9,#1\n" \
              "add x9,x9,#1\n add x9,x9,#1\n add x9,x9,#1\n add x9,x9,#1\n add x9,x9,#1\n"
#define ADD100 ADD10 ADD10 ADD10 ADD10 ADD10 ADD10 ADD10 ADD10 ADD10 ADD10

static double chain_ns(int wide)
{
    const int R = 50000;
    register uint64_t x __asm__("x9") = 0;
    uint64_t t0 = now_ns();
    for (int i = 0; i < R; i++) {
        if (wide) __asm__ volatile(ADD100 ADD100 : "+r"(x));
        else      __asm__ volatile(ADD100        : "+r"(x));
    }
    return (double)(now_ns() - t0) / R;
}

/*
 * The two chain lengths are measured alternately and each reduced to its
 * minimum.  Taken in sequence instead, the clock ramps between them and the
 * difference is contaminated -- that produced 4.06 GHz on a part whose P-core
 * tops out at 3.5.
 */
static double measure_ghz(void)
{
    double lo = 1e18, hi = 1e18;
    for (int i = 0; i < 40; i++) {
        double a1 = chain_ns(1), a0 = chain_ns(0);
        if (a1 < hi) hi = a1;
        if (a0 < lo) lo = a0;
    }
    return 100.0 / (hi - lo);
}

static int16_t a[N], b[N], o1[N], o2[N];
static uint64_t s = 0x2545F4914F6CDD1Dull;
static uint64_t rnd(void){s^=s<<13;s^=s>>7;s^=s<<17;return s;}

typedef void (*kfn)(int16_t *, const int16_t *, const int16_t *);

/*
 * Both candidates are measured alternately and each reduced to its minimum.
 * Run one after the other instead and the second meets a different frequency
 * state: that produced a two-fold swing between consecutive invocations.
 */
static void bench_all(kfn *f, int n, double g, double *out)
{
    const int R = 20000;
    for (int i = 0; i < n; i++) out[i] = 1e18;
    for (int i = 0; i < 2000; i++) for (int j = 0; j < n; j++) f[j](o2, a, b);
    for (int t = 0; t < 25; t++)
        for (int j = 0; j < n; j++) {
            uint64_t t0 = now_ns();
            for (int i = 0; i < R; i++) f[j](o2, a, b);
            double ns = (double)(now_ns() - t0) / R;
            if (ns < out[j]) out[j] = ns;
        }
    for (int i = 0; i < n; i++) out[i] *= g;
}

static void kernel(int16_t *o, const int16_t *x, const int16_t *y)
{ basemul_rinv_kernel(o, x, y, &basemul_zetas[0][0]); }
#if HAVE_M1
static void kernel_b(int16_t *o, const int16_t *x, const int16_t *y)
{ basemul_rinv_kernel_b(o, x, y, &basemul_zetas[0][0]); }
#else
static void kernel_b(int16_t *o, const int16_t *x, const int16_t *y) { (void)o;(void)x;(void)y; }
#endif

int main(void)
{
    int qos = pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE, 0);
    printf("QoS request (0 = accepted): %d\n", qos);

    for (int i = 0; i < N; i++) { a[i] = (int16_t)(rnd() % 4096); b[i] = (int16_t)(rnd() % 4096); }

    kfn cand[3] = {basemul_rinv_asm, kernel, kernel_b};
    const char *name[3] = {"intrinsics C", "SLOTHY, cortex_a76", "SLOTHY, apple_m1_firestorm"};
    int ncand = HAVE_M1 ? 3 : 2;

    basemul_rinv_asm(o1, a, b);
    int bad = 0, worst = 0;
    for (int c = 1; c < ncand; c++) {
        cand[c](o2, a, b);
        for (int i = 0; i < N; i++) {
            if (o1[i] != o2[i] && ((o1[i] - o2[i]) % Q + Q) % Q) bad++;
            int v = o2[i] < 0 ? -o2[i] : o2[i];
            if (v > worst) worst = v;
        }
    }
    printf("agreement with the C oracle: %s   max |out| %d\n", bad ? "FAIL" : "pass", worst);

    double g = measure_ghz();
    printf("derived clock: %.2f GHz\n\n", g);
    double r[3];
    bench_all(cand, ncand, g, r);
    for (int i = 0; i < ncand; i++)
        printf("  %-28s %8.1f cycles   %7.1f ns\n", name[i], r[i], r[i] / g);
    return bad != 0;
}
