/* P137: frombytes_tbl2 and frombytes_tbl2_asm against the production frombytes_asm: canonical
 * encodings, random bytes, one out-of-range coefficient at every position;
 * the input ends at a guard page. */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>
int frombytes_asm(int16_t out[1152], const uint8_t in[1728]);
int frombytes_tbl2(int16_t out[1152], const uint8_t in[1728]);
int frombytes_tbl2_asm(int16_t out[1152], const uint8_t in[1728]);
static uint32_t s = 20260924u;
static uint32_t rnd(void) { s ^= s << 13; s ^= s >> 17; s ^= s << 5; return s; }
static void encode(uint8_t *b, const int *c) { for (int k = 0; k < 576; k++) { int a = c[2*k], d = c[2*k+1];
    b[3*k] = a & 0xff; b[3*k+1] = (a >> 8) | ((d & 0xf) << 4); b[3*k+2] = d >> 4; } }
int main(void)
{
    long pg = sysconf(_SC_PAGESIZE);
    uint8_t *m = mmap(0, 2 * pg, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANON, -1, 0);
    mprotect(m + pg, pg, PROT_NONE);
    uint8_t *in = m + pg - 1728;
    int bad = 0, rej = 0, c[1152];
    for (int t = 0; t < 200000; t++) {
        if (t % 2) for (int i = 0; i < 1728; i++) in[i] = rnd();
        else { for (int i = 0; i < 1152; i++) c[i] = rnd() % 3457; encode(in, c); }
        int16_t r1[1152], r2[1152], r3[1152];
        int e1 = frombytes_asm(r1, in), e2 = frombytes_tbl2(r2, in), e3 = frombytes_tbl2_asm(r3, in); rej += e1;
        if (e1 != e2 || e1 != e3 || memcmp(r1, r2, sizeof r1) || memcmp(r1, r3, sizeof r1)) if (bad++ < 3) printf("mismatch at %d: %d vs %d\n", t, e1, e2);
    }
    int single = 0;
    for (int pos = 0; pos < 1152; pos++) {
        for (int i = 0; i < 1152; i++) c[i] = rnd() % 3457;
        c[pos] = 3457 + (int)(rnd() % (4096 - 3457)); encode(in, c);
        int16_t r1[1152], r2[1152], r3[1152];
        if (frombytes_asm(r1, in) == 1 && frombytes_tbl2(r2, in) == 1 && frombytes_tbl2_asm(r3, in) == 1
            && !memcmp(r1, r2, sizeof r1) && !memcmp(r1, r3, sizeof r1)) single++;
    }
    printf("200000 trials: %d mismatches (%d rejected); single out-of-range coefficient rejected identically at %d/1152 positions\n", bad, rej, single);
    return bad != 0 || single != 1152;
}
