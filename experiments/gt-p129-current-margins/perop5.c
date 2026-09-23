/*
 * M2 Pro per-operation harness with a software frequency gate.
 *
 * Apple silicon exposes no P-state control: there is no cpufreq interface and
 * `taskpolicy` can only demote.  The clock therefore cannot be locked, so this
 * harness makes it observable and discards anything not measured at the top.
 *
 *   witness   a serial chain of 10 `add`s per iteration.  Each add has
 *             one-cycle latency and the chain is dependent, so its elapsed
 *             time is exactly (iterations * 10) core cycles: a direct clock
 *             reading.  Measured immediately after each operation batch.
 *   gate      a batch counts only if its witness came within GATE of the
 *             fastest witness of the session.  This is what replaces a
 *             hardware frequency lock; `accepted` reports how many survived.
 *   warm-up   the DVFS ramp on this part runs for about three seconds under
 *             load (2688 MHz at the first reading, plateauing near 3500), so
 *             warm-up is time-driven, not a fixed iteration count.
 *   order     the three operations round-robin inside the repeat loop, so
 *             drift during the session is charged equally to all three.
 *
 * Nothing on the timing path is floating point.  Upstream's `CE/f1600.S` and
 * `asm/pack.s` write v8-v15 without saving them, which AAPCS64 forbids; a
 * harness holding a timer in that range reads back `-inf`.  Times and the
 * witness are unsigned integers throughout and are converted only at print,
 * after the last call, so the official trees are measured exactly as shipped.
 */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#if defined(__APPLE__)
#include <pthread.h>
#include <sys/qos.h>
#endif
#include "api.h"

void rb_seed(void);

#if defined(__APPLE__)
#include <mach/mach_time.h>
static inline uint64_t nsec(void){ return clock_gettime_nsec_np(CLOCK_UPTIME_RAW); }
#else
static inline uint64_t nsec(void){ struct timespec t; clock_gettime(CLOCK_MONOTONIC,&t);
  return (uint64_t)t.tv_sec*1000000000ull + (uint64_t)t.tv_nsec; }
#endif

#define R      401     /* many short batches: on a loaded machine the gate rejects most */
#define N      100     /* short enough to fall inside a quiet window          */
#define WIT    50000   /* witness iterations: 500k cycles, ~145us          */
#define GATE_N 98      /* accept within GATE_N/100 of the fastest witness   */
#define WARM_NS 3000000000ull

static uint8_t pk[CRYPTO_PUBLICKEYBYTES],sk[CRYPTO_SECRETKEYBYTES];
static uint8_t ct[CRYPTO_CIPHERTEXTBYTES],ss[CRYPTO_BYTES],got[CRYPTO_BYTES];
static volatile unsigned sink;

/* elapsed ns for WIT*10 dependent cycles; smaller is a higher clock */
static uint64_t witness(void)
{
    uint64_t x = 0, t0 = nsec();
    for (long i = 0; i < WIT; i++)
        __asm__ volatile(
            "add %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\n"
            "add %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\nadd %0,%0,#1\n"
            : "+r"(x));
    uint64_t dt = nsec() - t0;
    sink += (unsigned)x;
    return dt ? dt : 1;
}

static void one(int op)
{
    if (op == 0) { crypto_kem_keypair(pk,sk); sink += sk[0]; }
    else if (op == 1) { crypto_kem_enc(ct,ss,pk); sink += ct[0]; }
    else { crypto_kem_dec(got,ct,sk); sink += got[0]; }
}

int main(int argc, char **argv)
{
    const char *tag = argc > 1 ? argv[1] : "?";
#if defined(__APPLE__)
    pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE, 0);
#endif

    rb_seed();
    if (crypto_kem_keypair(pk,sk) || crypto_kem_enc(ct,ss,pk)
        || crypto_kem_dec(got,ct,sk) || memcmp(ss,got,CRYPTO_BYTES)) {
        fprintf(stderr,"%s: selftest failed\n",tag); return 1;
    }

    uint64_t wfast = UINT64_MAX;          /* fastest witness = top clock */
    uint64_t t_start = nsec();
    int stable = 0;
    for (int w = 0; w < 4000; w++) {
        rb_seed(); for (int op = 0; op < 3; op++) for (int k = 0; k < N; k++) one(op);
        uint64_t d = witness();
        if (d < wfast) { wfast = d; stable = 0; } else stable++;
        if (stable >= 5 && nsec() - t_start > WARM_NS) break;
    }

    uint64_t best[3] = {UINT64_MAX,UINT64_MAX,UINT64_MAX};
    uint64_t wslow = 0;
    int acc[3] = {0,0,0};
    for (int r = 0; r < R; r++) {
        for (int op = 0; op < 3; op++) {
            rb_seed();                       /* identical key sequence per batch */
            uint64_t t0 = nsec();
            for (int k = 0; k < N; k++) one(op);
            uint64_t dt = nsec() - t0;
            uint64_t d = witness();
            if (d < wfast) wfast = d;
            if (d > wslow) wslow = d;
            if (d * GATE_N <= wfast * 100) { acc[op]++; if (dt < best[op]) best[op] = dt; }
        }
    }
    double mhz_hi = (double)(WIT*10) / (double)wfast * 1000.0;
    double mhz_lo = (double)(WIT*10) / (double)wslow * 1000.0;
    printf("%s keygen %.0f encaps %.0f decaps %.0f "
           "clock_ceiling %.0f clock_low %.0f accepted %d/%d %d/%d %d/%d\n",
           tag, (double)best[0]/N, (double)best[1]/N, (double)best[2]/N,
           mhz_hi, mhz_lo, acc[0],R, acc[1],R, acc[2],R);
    return 0;
}
