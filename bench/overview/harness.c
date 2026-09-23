/*
 * Same-ELF component profiler main (2026-09-23 AVX2 overview).
 * Build: -DOVB_ROLES='X(official) X(opt) X(gt)' (see run_overview_components.py).
 *
 * Protocol per launch (SUPERCOP cpucycles, one call per observation):
 *   setup every implementation's fixtures; preflight: with identical seeded
 *   randomness every implementation must produce byte-identical pk/sk/ct/ss
 *   and hash_f/g/h outputs (else trap).  Then for every component name (in
 *   first-seen order) and every block 0..BLOCKS-1, the implementations that
 *   provide it run in rotated order (block + slot) mod V; each slot does 4
 *   warm-up calls and OBS timed calls over OVB_BANKS banks, with the untimed
 *   prep() before each call.  Output CSV: component,role,block,obs,cycles.
 * Diagnostic only (supercop-derived), not a Native KEM measurement.
 */
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "cpucycles.h"
#include "ovb.h"
#include "params.h" /* sizes only, from the first role's tree */

#define OVB_PK NTRUPLUS_PUBLICKEYBYTES
#define OVB_SK NTRUPLUS_SECRETKEYBYTES
#define OVB_CT NTRUPLUS_CIPHERTEXTBYTES
#define OVB_SS NTRUPLUS_SSBYTES
#define OVB_POLYBYTES NTRUPLUS_POLYBYTES

#ifndef OVB_ROLES
#error "OVB_ROLES must list X(role) entries"
#endif

#define X(r) extern const ovb_impl r##_ovb_impl_desc;
OVB_ROLES
#undef X
#define X(r) {#r, &r##_ovb_impl_desc},
static const struct { const char *role; const ovb_impl *impl; } impls[] = {OVB_ROLES};
#undef X
enum { NI = sizeof impls / sizeof impls[0], BLOCKS = 12, OBS = 32, WARM = 4, MAXC = 64 };

/* ---- deterministic randombytes shared by every implementation (splitmix64) */
static uint64_t rng_state;
void ovb_rng_seed(uint64_t seed) { rng_state = seed * 0x9e3779b97f4a7c15ULL + 0x1234567ULL; }
static uint64_t next64(void) {
    uint64_t z = (rng_state += 0x9e3779b97f4a7c15ULL);
    z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL;
    z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL;
    return z ^ (z >> 31);
}
void randombytes(unsigned char *out, unsigned long long len) {
    while (len) {
        uint64_t v = next64();
        for (unsigned i = 0; i < 8 && len; i++, len--) *out++ = (unsigned char)(v >> (8 * i));
    }
}
void crypto_declassify(const void *value, unsigned long long length) { (void)value; (void)length; }

static unsigned char pk[NI][OVB_PK], sk[NI][OVB_SK], ct[NI][OVB_CT], ss[NI][OVB_SS], ss2[OVB_SS];
static uint8_t hin[OVB_POLYBYTES + 64], hout[NI][3][OVB_POLYBYTES + 64];

static void preflight(void) {
    for (unsigned s = 0; s < 8; s++) {
        for (unsigned i = 0; i < NI; i++) {
            const ovb_impl *m = impls[i].impl;
            ovb_rng_seed(77000 + s);
            if (m->keypair(pk[i], sk[i])) __builtin_trap();
            ovb_rng_seed(88000 + s);
            if (m->enc(ct[i], ss[i], pk[0])) __builtin_trap();
            if (m->dec(ss2, ct[0], sk[0]) || memcmp(ss2, ss[0], OVB_SS)) __builtin_trap();
            if (i && (memcmp(pk[i], pk[0], OVB_PK) || memcmp(sk[i], sk[0], OVB_SK) ||
                      memcmp(ct[i], ct[0], OVB_CT) || memcmp(ss[i], ss[0], OVB_SS))) {
                fprintf(stderr, "preflight: %s KEM output differs from %s (seed %u)\n",
                        impls[i].role, impls[0].role, s);
                __builtin_trap();
            }
        }
    }
    for (unsigned j = 0; j < sizeof hin; j++) hin[j] = (uint8_t)(j * 7U + 3U);
    for (unsigned i = 0; i < NI; i++) {
        memset(hout[i], 0, sizeof hout[i]);
        impls[i].impl->hash_f(hout[i][0], hin);
        impls[i].impl->hash_g(hout[i][1], hin);
        impls[i].impl->hash_h(hout[i][2], hin);
        if (i && memcmp(hout[i], hout[0], sizeof hout[0])) __builtin_trap();
    }
    fputs("preflight=pass (KEM byte-identical across roles, 8 seeds; hash_f/g/h identical)\n", stderr);
}

static const ovb_component *find(const ovb_impl *m, const char *name) {
    for (unsigned c = 0; c < m->count; c++)
        if (!strcmp(m->components[c].name, name)) return &m->components[c];
    return 0;
}

int main(void) {
    for (unsigned i = 0; i < NI; i++) impls[i].impl->setup();
    preflight();
    cpucycles_tracesetup();
    fprintf(stderr, "cpucycles=%s persecond=%lld roles=%u\n",
            cpucycles_implementation(), cpucycles_persecond(), (unsigned)NI);
    const char *names[MAXC];
    unsigned nn = 0;
    for (unsigned i = 0; i < NI; i++)
        for (unsigned c = 0; c < impls[i].impl->count; c++) {
            const char *n = impls[i].impl->components[c].name;
            unsigned k = 0;
            while (k < nn && strcmp(names[k], n)) k++;
            if (k == nn) { if (nn == MAXC) __builtin_trap(); names[nn++] = n; }
        }
    puts("component,role,block,obs,cycles");
    for (unsigned k = 0; k < nn; k++) {
        const ovb_component *have[NI];
        const char *role[NI];
        unsigned nv = 0;
        for (unsigned i = 0; i < NI; i++) {
            const ovb_component *c = find(impls[i].impl, names[k]);
            if (c) { have[nv] = c; role[nv++] = impls[i].role; }
        }
        for (unsigned block = 0; block < BLOCKS; block++)
            for (unsigned slot = 0; slot < nv; slot++) {
                unsigned v = (block + slot) % nv;
                const ovb_component *c = have[v];
                for (unsigned w = 0; w < WARM; w++) { if (c->prep) c->prep(w); c->run(w); }
                for (unsigned obs = 0; obs < OBS; obs++) {
                    unsigned bank = obs % OVB_BANKS;
                    if (c->prep) c->prep(bank);
                    long long t0 = cpucycles();
                    c->run(bank);
                    long long t1 = cpucycles();
                    printf("%s,%s,%u,%u,%lld\n", names[k], role[v], block, obs, t1 - t0);
                }
            }
    }
    return 0;
}
