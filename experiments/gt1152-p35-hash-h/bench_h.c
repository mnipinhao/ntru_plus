/* P35 -- what hash_h actually costs, and what a fused hash_h would cost.
 *
 * P32 left hash_h on the generic sponge and justified it with "input is 176
 * bytes, a single block, where the fusion has nothing to amortize".  The first
 * correction (P34) said it was five permutations.  That was also wrong.  This
 * counts them instead of arguing, and decomposes the generic path.
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <linux/perf_event.h>
#include <sys/syscall.h>
#include <sys/ioctl.h>
#include "fips202.h"

extern unsigned long keccak_permute_calls;   /* from the instrumented fips202.c */

static int fd;
static uint64_t rd(void) { uint64_t v; if (read(fd, &v, 8) != 8) _exit(3); return v; }

void ntruplus_keccak_f1600_x1_aarch64(uint64_t *, const uint64_t *);
void ntruplus_hash_g_fused_aarch64(uint8_t *, const uint8_t *, const uint64_t *);
void ntruplus_hash_f_fused_aarch64(uint8_t *, const uint8_t *, const uint64_t *);

static const uint64_t RC[24] = {
0x0000000000000001ULL,0x0000000000008082ULL,0x800000000000808aULL,0x8000000080008000ULL,
0x000000000000808bULL,0x0000000080000001ULL,0x8000000080008081ULL,0x8000000000008009ULL,
0x000000000000008aULL,0x0000000000000088ULL,0x0000000080008009ULL,0x000000008000000aULL,
0x000000008000808bULL,0x800000000000008bULL,0x8000000000008089ULL,0x8000000000008003ULL,
0x8000000000008002ULL,0x8000000000000080ULL,0x000000000000800aULL,0x800000008000000aULL,
0x8000000080008081ULL,0x8000000000008080ULL,0x0000000080000001ULL,0x8000000080008008ULL};

#define HIN   176                 /* NTRUPLUS_N/8 + 32 */
#define HOUT  320                 /* 32 + NTRUPLUS_N/4 */
#define BIG   1728                /* NTRUPLUS_POLYBYTES */

static uint8_t msg[HIN], big[BIG], out[HOUT], st[200] __attribute__((aligned(16)));
static uint8_t gout[288], fout[32];

/* the shipped hash_h, verbatim from symmetric.c */
static void c_hash_h(void)
{
    uint8_t data[1 + HIN];
    data[0] = 0x02;
    memcpy(data + 1, msg, HIN);
    shake256(out, HOUT, data, HIN + 1);
    /* symmetric.c also secure_clear()s data; measured separately below */
}
/* the same minus the prefix copy */
static void c_nocopy(void)  { shake256(out, HOUT, msg, HIN + 1); }
/* the malloc/free pair shake256() performs internally, on its own */
static void c_mallocfree(void){ void *p = malloc(200); __asm__ volatile("" :: "r"(p) : "memory"); free(p); }
static void c_memcpy(void)  { uint8_t d[1 + HIN]; d[0] = 2; memcpy(d + 1, msg, HIN);
                              __asm__ volatile("" :: "r"(d) : "memory"); }
static void c_perm4(void)   { for (int i = 0; i < 4; i++) ntruplus_keccak_f1600_x1_aarch64((uint64_t *)st, RC); }
static void c_fused_g(void) { ntruplus_hash_g_fused_aarch64(gout, big, RC); }
static void c_fused_f(void) { ntruplus_hash_f_fused_aarch64(fout, big, RC); }
/* The cheap alternative to a fused kernel: the same generic sponge shape, but
 * over the assembly permutation the package already ships.  Four permutations,
 * a 200-byte state on the stack, no malloc. */
static uint64_t ld64(const uint8_t *x)
{
    uint64_t r = 0;
    for (int i = 0; i < 8; i++) r |= (uint64_t)x[i] << (8 * i);
    return r;
}
static void hash_h_asm_sponge(uint8_t *o, const uint8_t *m)
{
    uint64_t s[25] = {0};
    uint8_t data[1 + HIN], t[136] = {0};
    data[0] = 0x02;
    memcpy(data + 1, m, HIN);
    for (int i = 0; i < 17; i++) s[i] ^= ld64(data + 8 * i);      /* block 0 */
    ntruplus_keccak_f1600_x1_aarch64(s, RC);
    memcpy(t, data + 136, (1 + HIN) - 136);                        /* 41-byte tail */
    t[(1 + HIN) - 136] = 0x1F; t[135] |= 0x80;
    for (int i = 0; i < 17; i++) s[i] ^= ld64(t + 8 * i);
    ntruplus_keccak_f1600_x1_aarch64(s, RC);
    memcpy(o, s, 136);
    ntruplus_keccak_f1600_x1_aarch64(s, RC);
    memcpy(o + 136, s, 136);
    ntruplus_keccak_f1600_x1_aarch64(s, RC);
    memcpy(o + 272, s, HOUT - 272);
}
static uint8_t out2[HOUT];
static void c_asm_sponge(void) { hash_h_asm_sponge(out2, msg); }
/* keygen's seed expansion, the other generic-sponge site: 32 bytes in, 288
 * out = 0 absorb permutations + 3 squeeze permutations. */
static uint8_t seed[32], sbuf[288];
static void c_seed(void)    { shake256(sbuf, 288, seed, 32); }
static void c_empty(void)   { __asm__ volatile("" ::: "memory"); }

struct cand { const char *name; void (*f)(void); int perms; double best; };
static struct cand C[] = {
    {"empty loop body",                     c_empty,      0, 1e18},
    {"hash_h, generic sponge (as shipped)", c_hash_h,     4, 1e18},
    {"  ... without the prefix memcpy",     c_nocopy,     4, 1e18},
    {"  the malloc/free pair alone",        c_mallocfree, 0, 1e18},
    {"  the prefix memcpy alone",           c_memcpy,     0, 1e18},
    {"4 bare assembly permutations",        c_perm4,      4, 1e18},
    {"hash_h over the asm permutation",     c_asm_sponge, 4, 1e18},
    {"genf/geng seed expand (32 in, 288 out)", c_seed,    3, 1e18},
    {"hash_f fused (1729 in, 32 out)",      c_fused_f,   13, 1e18},
    {"hash_g fused (1729 in, 288 out)",     c_fused_g,   15, 1e18},
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

    uint64_t s = 1;
    for (int i = 0; i < BIG; i++) { s ^= s<<13; s ^= s>>7; s ^= s<<17; big[i] = (uint8_t)s; }
    memcpy(msg, big, HIN);

    /* ---- count permutations rather than reason about them ---- */
    keccak_permute_calls = 0; c_hash_h();
    unsigned long n_h = keccak_permute_calls;
    /* the cheap variant must agree with the sponge before it is timed */
    { uint8_t a[HOUT], b[HOUT], d[1 + HIN];
      d[0] = 0x02; memcpy(d + 1, msg, HIN);
      shake256(a, HOUT, d, HIN + 1);
      hash_h_asm_sponge(b, msg);
      printf("asm-sponge hash_h vs shake256: %s\n\n",
             memcmp(a, b, HOUT) ? "MISMATCH" : "identical, 320/320 bytes"); }

    printf("permutation counts, measured by instrumenting fips202.c:\n");
    printf("  hash_h  generic, %d in + 1 prefix, %d out : %lu\n", HIN, HOUT, n_h);
    printf("  (fused hash_f 13 and hash_g 15 by construction: 12 full + 1 tail"
           " absorb, then 0 / 2 squeeze)\n\n");

    for (int i = 0; i < NC; i++) for (int w = 0; w < 300; w++) C[i].f();
    const int R = 3000, PASSES = 30;
    for (int p = 0; p < PASSES; p++)
        for (int i = 0; i < NC; i++) {
            double v = one(C[i].f, R);
            if (v < C[i].best) C[i].best = v;
        }

    double e = C[0].best;
    printf("%-40s %9s %9s\n", "", "cycles", "per perm");
    for (int i = 1; i < NC; i++) {
        double v = C[i].best - e;
        if (C[i].perms) printf("  %-38s %9.1f %9.1f\n", C[i].name, v, v / C[i].perms);
        else            printf("  %-38s %9.1f %9s\n", C[i].name, v, "-");
    }

    double gen = C[1].best - e, bare4 = C[5].best - e;
    double ff = C[8].best - e, fg = C[9].best - e;   /* fused hash_f, hash_g */
    double per_squeeze = (fg - ff) / 2.0;          /* hash_g is hash_f + 2 squeeze stages */
    double per_absorb  = ff / 13.0;                /* fixed cost folds in here */
    double est = 2 * per_absorb + 2 * per_squeeze; /* hash_h: 2 absorb + 2 squeeze stages */

    printf("\n--- what a fused hash_h would cost ---\n");
    printf("  fused absorb stage   %7.1f   (hash_f / 13)\n", per_absorb);
    printf("  fused squeeze stage  %7.1f   ((hash_g - hash_f) / 2)\n", per_squeeze);
    printf("  fused hash_h = 2 absorb + 2 squeeze  = %7.1f\n", est);
    printf("  generic hash_h as shipped            = %7.1f\n", gen);
    printf("  4 bare permutations (no sponge)      = %7.1f\n", bare4);
    double simple = C[6].best - e;                   /* asm-permutation sponge */
    printf("  saving per call %7.1f   x2 calls = %7.1f\n", gen - est, 2 * (gen - est));
    printf("\n--- versus the cheap alternative ---\n");
    printf("  hash_h over the asm permutation      = %7.1f   saving %7.1f/call\n",
           simple, gen - simple);
    printf("  a fused kernel buys a further        = %7.1f/call\n", simple - est);
    printf("  so the cheap change captures           %5.1f%% of the total\n",
           100.0 * (gen - simple) / (gen - est));

    double seedc = C[7].best - e;
    keccak_permute_calls = 0; c_seed();
    printf("\n--- the other generic-sponge site ---\n");
    printf("  genf/geng seed expand  %7.1f  over %lu permutations (%.1f each)\n",
           seedc, keccak_permute_calls, seedc / keccak_permute_calls);
    printf("  same shape: still on the C permutation, 2 calls per keygen attempt\n");
    return 0;
}
