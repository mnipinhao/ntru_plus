/* P135: frombytes_encap_pairs against the production poly_frombytes_encap:
 * canonical encodings, random bytes, one out-of-range coefficient at every
 * position; the input ends at a guard page. */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>
#include "params.h"
#include "poly.h"
int poly_frombytes_encap(poly *out, const uint8_t in[NTRUPLUS_POLYBYTES]);
int frombytes_encap_pairs(int16_t out[768], const uint8_t in[1152]);
static uint32_t s = 20260924u;
static uint32_t rnd(void) { s ^= s << 13; s ^= s >> 17; s ^= s << 5; return s; }
static void encode(uint8_t *b, const int *c) { for (int k = 0; k < 384; k++) { int a = c[2*k], d = c[2*k+1];
    b[3*k] = a & 0xff; b[3*k+1] = (a >> 8) | ((d & 0xf) << 4); b[3*k+2] = d >> 4; } }
int main(void)
{
    long pg = sysconf(_SC_PAGESIZE);
    uint8_t *m = mmap(0, 2 * pg, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANON, -1, 0);
    mprotect(m + pg, pg, PROT_NONE);
    uint8_t *in = m + pg - NTRUPLUS_POLYBYTES;
    int bad = 0, rej = 0, c[768];
    for (int t = 0; t < 200000; t++) {
        if (t % 2) for (int i = 0; i < NTRUPLUS_POLYBYTES; i++) in[i] = rnd();
        else { for (int i = 0; i < 768; i++) c[i] = rnd() % 3457; encode(in, c); }
        poly r1; int16_t r2[768];
        int e1 = poly_frombytes_encap(&r1, in), e2 = frombytes_encap_pairs(r2, in); rej += e1;
        if (e1 != e2 || (!e1 && memcmp(r1.coeffs, r2, sizeof r2))) if (bad++ < 3) printf("mismatch at %d: %d vs %d\n", t, e1, e2);
    }
    int single = 0;
    for (int pos = 0; pos < 768; pos++) {
        for (int i = 0; i < 768; i++) c[i] = rnd() % 3457;
        c[pos] = 3457 + (int)(rnd() % (4096 - 3457)); encode(in, c);
        poly r1; int16_t r2[768];
        if (poly_frombytes_encap(&r1, in) == 1 && frombytes_encap_pairs(r2, in) == 1) single++;
    }
    printf("200000 trials: %d mismatches (%d rejected); single out-of-range coefficient rejected by both at %d/768 positions\n", bad, rej, single);
    return bad != 0 || single != 768;
}
