/* P133: frombytes_runs against the production frombytes, on canonical
 * encodings (from tobytes) and on random bytes (malformed values included).
 * Output and return value must match, and nothing may be read past byte 1296
 * (inputs sit at the end of a page followed by a guard page). */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>
#include "params.h"
#include "poly.h"
int poly_frombytes(poly *r, const uint8_t a[NTRUPLUS_POLYBYTES]);
int frombytes_runs(int16_t out[864], const uint8_t in[1296]);
static uint32_t s = 20260924u;
static uint32_t rnd(void) { s ^= s << 13; s ^= s >> 17; s ^= s << 5; return s; }
int main(void)
{
    long pg = sysconf(_SC_PAGESIZE);
    uint8_t *m = mmap(0, 2 * pg, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANON, -1, 0);
    mprotect(m + pg, pg, PROT_NONE);                     /* guard page */
    uint8_t *in = m + pg - NTRUPLUS_POLYBYTES;          /* ends exactly at the guard */
    int bad = 0, rejects = 0;
    for (int t = 0; t < 200000; t++) {
        if (t % 2) {
            for (int i = 0; i < NTRUPLUS_POLYBYTES; i++) in[i] = rnd();
        } else {
            poly a; for (int i = 0; i < NTRUPLUS_N; i++) a.coeffs[i] = rnd() % 3457;
            poly_tobytes(in, &a);
        }
        poly r1; int16_t r2[864];
        memset(&r1, 0x55, sizeof r1); memset(r2, 0x66, sizeof r2);
        int e1 = poly_frombytes(&r1, in), e2 = frombytes_runs(r2, in);
        rejects += e1;
        if (e1 != e2 || memcmp(r1.coeffs, r2, sizeof r2)) { if (bad++ < 3) printf("mismatch at trial %d (ret %d vs %d)\n", t, e1, e2); }
    }
    /* one out-of-range coefficient at every position, in an otherwise canonical encoding */
    int single = 0;
    for (int pos = 0; pos < NTRUPLUS_N; pos++) {
        poly a; for (int i = 0; i < NTRUPLUS_N; i++) a.coeffs[i] = rnd() % 3457;
        poly_tobytes(in, &a);
        int v = 3457 + (int)(rnd() % (4096 - 3457));
        uint8_t *b = in + 3 * (pos / 2);
        if (pos % 2 == 0) { b[0] = v & 0xff; b[1] = (b[1] & 0xf0) | (v >> 8); }
        else              { b[1] = (b[1] & 0x0f) | ((v & 0xf) << 4); b[2] = v >> 4; }
        poly r1; int16_t r2[864];
        int e1 = poly_frombytes(&r1, in), e2 = frombytes_runs(r2, in);
        if (e1 == 1 && e2 == 1 && !memcmp(r1.coeffs, r2, sizeof r2)) single++;
        else if (bad++ < 3) printf("single-coefficient case %d: ret %d vs %d\n", pos, e1, e2);
    }
    printf("single out-of-range coefficient: %d/864 positions rejected by both, outputs equal\n", single);
    printf("200000 trials (half canonical, half random bytes): %d mismatches, %d rejected\n", bad, rejects);
    return bad != 0;
}
