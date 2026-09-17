/*
 * Component profiler for NTRU+1152: GT versus the official SUPERCOP leaf.
 *
 * Adapted from bench/aarch64/gt864-production-profile/harness.c.  Sizes are
 * 1152's (pk/ct 1728, sk 3488), and the component set spans both APIs, which
 * differ: GT has basemul_rinv, tobytes_small/compare and a fused
 * invntt_ternary; the official has a separate invntt plus crepmod3.
 *
 * Four shared objects are loaded: each implementation plain, and each built
 * with its poly and hash calls redirected through timing wrappers.  The plain
 * pair gives whole-operation numbers; the instrumented pair gives attribution,
 * and is checked to produce identical outputs first.
 */
#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <dlfcn.h>
#include <linux/perf_event.h>
#include <sys/syscall.h>
#include <sys/ioctl.h>
#include "ids.h"

#define PKB 1728
#define SKB 3488
#define CTB 1728
#define SSB 32

typedef int (*keyfn)(uint8_t *, uint8_t *);
typedef int (*encfn)(uint8_t *, uint8_t *, const uint8_t *);
typedef int (*decfn)(uint8_t *, const uint8_t *, const uint8_t *);
struct api { keyfn key; encfn enc; decfn dec; };
struct counts { uint64_t n, v[3]; };

static int fd;
static uint64_t rng = 1, totals[NCOMP], calls[NCOMP];
static int profiling;
static double overhead;
static volatile unsigned sink;

/* Deterministic, so both implementations see identical inputs. */
void randombytes(uint8_t *out, size_t n)
{
    for (size_t i = 0; i < n; i++) {
        rng ^= rng << 13; rng ^= rng >> 7; rng ^= rng << 17;
        out[i] = (uint8_t)rng;
    }
}

static struct counts readpmu(void)
{
    struct counts c;
    if (read(fd, &c, sizeof c) != sizeof c || c.n != 3) exit(3);
    return c;
}

uint64_t prof_start(void) { return profiling ? readpmu().v[0] : 0; }
void prof_end(int i, uint64_t t)
{
    if (profiling) { totals[i] += readpmu().v[0] - t; calls[i]++; }
}

static struct api load(const char *file)
{
    void *h = dlopen(file, RTLD_NOW | RTLD_LOCAL);
    if (!h) { puts(dlerror()); exit(2); }
    struct api a;
    a.key = (keyfn)dlsym(h, "crypto_kem_keypair");
    a.enc = (encfn)dlsym(h, "crypto_kem_enc");
    a.dec = (decfn)dlsym(h, "crypto_kem_dec");
    if (!a.key || !a.enc || !a.dec) { puts("missing symbol"); exit(2); }
    return a;
}

static int counter(uint64_t config, int group)
{
    struct perf_event_attr a = {0};
    a.size = sizeof a; a.type = PERF_TYPE_HARDWARE; a.config = config;
    a.exclude_kernel = 1; a.exclude_hv = 1; a.disabled = group < 0;
    a.read_format = PERF_FORMAT_GROUP;
    return syscall(__NR_perf_event_open, &a, 0, -1, group, 0);
}

static uint8_t pk[2][PKB], sk[2][SKB], ct[2][CTB], ss[SSB];

static void setup(struct api a, int v, uint64_t seed)
{
    rng = seed;            if (a.key(pk[v], sk[v])) exit(4);
    rng = seed + 1;        if (a.enc(ct[v], ss, pk[v])) exit(4);
    uint8_t out[SSB];
    if (a.dec(out, ct[v], sk[v]) || memcmp(out, ss, SSB)) exit(4);
}

static void run(struct api a, int v, int op, uint64_t seed)
{
    rng = seed;
    int ret = op == 0 ? a.key(pk[v], sk[v])
            : op == 1 ? a.enc(ct[v], ss, pk[v])
                      : a.dec(ss, ct[v], sk[v]);
    if (ret) exit(4);
    sink += ss[0];
}

int main(int argc, char **argv)
{
    int reverse = argc > 1 ? atoi(argv[1]) : 0;
    const char *base = getenv("BASE") ? getenv("BASE") : "off";
    const char *cand = getenv("CAND") ? getenv("CAND") : "gt";
    char bn[64], cn[64], bp[64], cp[64];
    snprintf(bn, 64, "./%s.so", base);      snprintf(cn, 64, "./%s.so", cand);
    snprintf(bp, 64, "./%s-prof.so", base); snprintf(cp, 64, "./%s-prof.so", cand);
    struct api a[2] = {load(bn), load(cn)}, p[2] = {load(bp), load(cp)};

    /* The two implementations must agree on every wire value. */
    int differences = 0;
    for (int t = 0; t < 16; t++) {
        for (int v = 0; v < 2; v++) {
            setup(a[v], v, 100 + t);
            uint8_t bad[CTB], out[SSB];
            memcpy(bad, ct[v], CTB);
            bad[11 + 37 * t] ^= 128;
            if (a[v].dec(out, bad, sk[v]) == 0) exit(4);
        }
        differences += memcmp(pk[0], pk[1], PKB) != 0;
        differences += memcmp(ct[0], ct[1], CTB) != 0;
        differences += memcmp(sk[0], sk[1], SKB) != 0;
    }

    /* Instrumentation must not perturb any output. */
    for (int v = 0; v < 2; v++) {
        uint8_t spk[PKB], ssk[SKB], sct[CTB], sss[SSB];
        setup(a[v], v, 12345);
        memcpy(spk, pk[v], PKB); memcpy(ssk, sk[v], SKB);
        memcpy(sct, ct[v], CTB); memcpy(sss, ss, SSB);
        setup(p[v], v, 12345);
        if (memcmp(spk, pk[v], PKB) || memcmp(ssk, sk[v], SKB) ||
            memcmp(sct, ct[v], CTB) || memcmp(sss, ss, SSB)) exit(4);
    }
    printf("correctness=pass tampered_cases=%d instrumentation_equivalence=pass\n", 16 * 2);
    printf("cross_implementation_wire_differences=%d\n", differences);

    fd = counter(PERF_COUNT_HW_CPU_CYCLES, -1);
    int i = counter(PERF_COUNT_HW_INSTRUCTIONS, fd);
    int j = counter(PERF_COUNT_HW_BRANCH_INSTRUCTIONS, fd);
    if (fd < 0 || i < 0 || j < 0) { perror("perf"); return 2; }
    ioctl(fd, PERF_EVENT_IOC_ENABLE, PERF_IOC_FLAG_GROUP);

    const char *ops[] = {"keygen", "encaps", "decaps"};
    const char *names[] = {base, cand};

    for (int op = 0; op < 3; op++)
        for (int sample = 0; sample < 41; sample++)
            for (int pos = 0; pos < 2; pos++) {
                int v = pos ^ reverse;
                setup(a[v], v, 0xb6123001);
                int n = op == 0 ? 4 : 20;
                struct counts x = readpmu();
                for (int k = 0; k < n; k++)
                    run(a[v], v, op, 0xb6000000ULL + (uint64_t)k * 0x9e3779b1ULL);
                struct counts y = readpmu();
                printf("full,%s,%s,%.3f,%.3f,%.3f\n", ops[op], names[v],
                       (double)(y.v[0] - x.v[0]) / n,
                       (double)(y.v[1] - x.v[1]) / n,
                       (double)(y.v[2] - x.v[2]) / n);
            }

    profiling = 1;
    for (int k = 0; k < 1000; k++) { uint64_t t = prof_start(); prof_end(0, t); }
    overhead = (double)totals[0] / calls[0];
    profiling = 0;
    printf("profiler_empty_boundary_cycles=%.3f\n", overhead);

    for (int op = 0; op < 3; op++)
        for (int sample = 0; sample < 41; sample++)
            for (int pos = 0; pos < 2; pos++) {
                int v = pos ^ reverse;
                setup(p[v], v, 0xb6123001);
                memset(totals, 0, sizeof totals);
                memset(calls, 0, sizeof calls);
                profiling = 1;
                run(p[v], v, op, 0xb6000000ULL);
                profiling = 0;
                for (int c = 0; c < NCOMP; c++)
                    if (calls[c])
                        printf("profile,%s,%s,%s,%llu,%.3f\n", ops[op], names[v],
                               component_names[c], (unsigned long long)calls[c],
                               (double)totals[c] - overhead * calls[c]);
            }
    return 0;
}
