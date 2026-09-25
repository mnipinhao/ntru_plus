/* P138: where GT's hash_f / hash_g beat Official's, step by step.  Both sides run GT's permutation
 * (Official's sponge calls f1600, a one-instruction branch to it).  O0 is Official's hash exactly as
 * symmetric.c + CE/fips202.c write it (copied here); each next row removes one difference; GT is
 * shake256_prefixed as shipped.
 *   O0  copy input behind the domain byte, upstream sponge, clear the copy (hash_g only)
 *   O1  O0 without clearing the copy
 *   O2  O1 with the final partial block absorbed lane by lane (tail buffer) instead of byte by byte
 *   O3  O2 with the output written straight from the state instead of through temp[] + a byte copy
 *   O4  O3 without the copy: the domain byte is absorbed in place (GT's first-block shift)
 *   GT  shake256_prefixed (O4 plus clearing its state and tail buffer)
 * -DMEMCPY_LOAD64 builds every O-row with GT's load64 (one unaligned 64-bit load) instead of
 * upstream's byte loop, which gcc vectorises into a byte-transposing uzp/zip network. */
#include <stdio.h>
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#ifdef __APPLE__
#include <time.h>
#include <pthread.h>
#include <sys/qos.h>
static inline uint64_t now(void){ return clock_gettime_nsec_np(CLOCK_UPTIME_RAW); }
#define UNIT "ns"
#define START() uint64_t t0=now()
#define STOP() (double)(now()-t0)
#else
#include "perf_counter.h"
#define UNIT "cyc"
#define START() perf_counter_start()
#define STOP() (double)perf_counter_stop()
#endif
#if SET == 768
#define POLYBYTES 1152
#define GOUT 192
#elif SET == 864
#define POLYBYTES 1296
#define GOUT 216
#else
#define POLYBYTES 1728
#define GOUT 288
#endif
#define RATE 136
extern void f1600(uint64_t *state, const uint64_t *rc);
void shake256_prefixed(uint8_t *out, size_t outlen, uint8_t domain, const uint8_t *in, size_t inlen);
static const uint64_t RC[24] = {
 0x0000000000000001ULL, 0x0000000000008082ULL, 0x800000000000808aULL, 0x8000000080008000ULL,
 0x000000000000808bULL, 0x0000000080000001ULL, 0x8000000080008081ULL, 0x8000000000008009ULL,
 0x000000000000008aULL, 0x0000000000000088ULL, 0x0000000080008009ULL, 0x000000008000000aULL,
 0x000000008000808bULL, 0x800000000000008bULL, 0x8000000000008089ULL, 0x8000000000008003ULL,
 0x8000000000008002ULL, 0x8000000000000080ULL, 0x000000000000800aULL, 0x800000008000000aULL,
 0x8000000080008081ULL, 0x8000000000008080ULL, 0x0000000080000001ULL, 0x8000000080008008ULL};
#ifdef MEMCPY_LOAD64       /* GT's form: one unaligned 64-bit load */
static uint64_t load64(const uint8_t *x){ uint64_t r; memcpy(&r, x, sizeof r); return r; }
#else                      /* upstream CE/fips202.c's form */
static uint64_t load64(const uint8_t *x){ uint64_t r = 0; for (unsigned i = 0; i < 8; i++) r |= ((uint64_t)x[i]) << (8 * i); return r; }
#endif
static void store64(uint8_t *x, uint64_t u){ for (unsigned i = 0; i < 8; i++) x[i] = (uint8_t)(u >> (8 * i)); }

/* upstream CE/fips202.c keccak_absorb, verbatim apart from the tail switch */
static void absorb(uint64_t s[25], const uint8_t *in, size_t inlen, int lane_tail){
    for (unsigned i = 0; i < 25; i++) s[i] = 0;
    while (inlen >= RATE) { for (unsigned i = 0; i < RATE / 8; i++) s[i] ^= load64(in + 8 * i); in += RATE; inlen -= RATE; f1600(s, RC); }
    if (!lane_tail) {
        unsigned i;
        for (i = 0; i < inlen; i++) s[i / 8] ^= ((uint64_t)in[i]) << (8 * (i % 8));
        s[i / 8] ^= ((uint64_t)0x1F) << (8 * (i % 8));
        s[(RATE - 1) / 8] ^= 1ULL << 63;
    } else {
        uint8_t t[RATE]; memset(t, 0, sizeof t); memcpy(t, in, inlen); t[inlen] ^= 0x1F; t[RATE - 1] ^= 0x80;
        for (unsigned i = 0; i < RATE / 8; i++) s[i] ^= load64(t + 8 * i);
    }
}
/* the same, with the domain byte absorbed in place (GT's shake256_prefixed first block) */
static void absorb_prefixed(uint64_t s[25], uint8_t dom, const uint8_t *in, size_t inlen){
    size_t total = inlen + 1, pos = 0;
    for (unsigned i = 0; i < 25; i++) s[i] = 0;
    while (total - pos >= RATE) {
        if (pos == 0) { s[0] ^= (uint64_t)dom | (load64(in) << 8); for (unsigned i = 1; i < RATE / 8; i++) s[i] ^= load64(in + 8 * i - 1); }
        else for (unsigned i = 0; i < RATE / 8; i++) s[i] ^= load64(in + pos - 1 + 8 * i);
        f1600(s, RC); pos += RATE;
    }
    uint8_t t[RATE]; memset(t, 0, sizeof t); size_t rem = total - pos;
    if (pos == 0) { t[0] = dom; memcpy(t + 1, in, rem - 1); } else memcpy(t, in + pos - 1, rem);
    t[rem] ^= 0x1F; t[RATE - 1] ^= 0x80;
    for (unsigned i = 0; i < RATE / 8; i++) s[i] ^= load64(t + 8 * i);
}
/* upstream shake256's squeeze: whole blocks, then one more into temp[] and a byte copy */
static void squeeze_upstream(uint8_t *out, size_t outlen, uint64_t s[25]){
    size_t nb = outlen / RATE;
    while (nb--) { f1600(s, RC); for (unsigned i = 0; i < RATE / 8; i++) store64(out + 8 * i, s[i]); out += RATE; outlen -= RATE; }
    if (outlen > 0) { uint8_t temp[RATE]; f1600(s, RC); for (unsigned i = 0; i < RATE / 8; i++) store64(temp + 8 * i, s[i]);
                      for (size_t i = 0; i < outlen; i++) out[i] = temp[i]; }
}
/* GT's squeeze: whole lanes straight from the state, bytes only for a final partial lane */
static void squeeze_direct(uint8_t *out, size_t outlen, uint64_t s[25]){
    while (outlen > 0) { size_t n = outlen < RATE ? outlen : RATE, i; f1600(s, RC);
        for (i = 0; i + 8 <= n; i += 8) store64(out + i, s[i / 8]);
        for (; i < n; ++i) out[i] = (uint8_t)(s[i / 8] >> (8 * (i % 8)));
        out += n; outlen -= n; }
}
static void clear(void *v, size_t n){ memset(v, 0, n); __asm__ volatile("" : : "r"(v) : "memory"); }

static void hash(int v, uint8_t dom, uint8_t *out, size_t outlen, const uint8_t *msg, int clear_copy){
    uint64_t s[25];
    if (v >= 4) { absorb_prefixed(s, dom, msg, POLYBYTES); squeeze_direct(out, outlen, s); return; }
    uint8_t data[1 + POLYBYTES]; data[0] = dom; memcpy(data + 1, msg, POLYBYTES);
    absorb(s, data, sizeof data, v >= 2);
    if (v >= 3) squeeze_direct(out, outlen, s); else squeeze_upstream(out, outlen, s);
    if (v == 0 && clear_copy) clear(data, sizeof data);
    __asm__ volatile("" : : "r"(data) : "memory");
}
static uint8_t in[POLYBYTES], out[GOUT];
static int V; static volatile int sink;
static void run_g(void){ if (V == 5) shake256_prefixed(out, GOUT, 0x01, in, POLYBYTES); else hash(V, 0x01, out, GOUT, in, 1); sink += out[0]; }
static void run_f(void){ if (V == 5) shake256_prefixed(out, 32, 0x00, in, POLYBYTES); else hash(V, 0x00, out, 32, in, 0); sink += out[0]; }
static double best(void (*f)(void)){ double b = 1e30; for (int w = 0; w < 2000; w++) f();
  for (int k = 0; k < 300; k++){ START(); for (int i = 0; i < 100; i++) f(); double d = STOP() / 100; if (d < b) b = d; } return b; }
int main(void){
#ifdef __APPLE__
  pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE, 0);
  { uint64_t t1 = now(); V = 0; while (now() - t1 < 3000000000ull) run_g(); }
#else
  if (perf_counter_open()) return 2;
#endif
  for (int i = 0; i < POLYBYTES; i++) in[i] = (uint8_t)(i * 131 + 7);
  /* all six forms give the same digest */
  uint8_t ref[GOUT], ref_f[32];
  for (V = 0; V <= 5; V++) { run_g(); if (V == 0) memcpy(ref, out, GOUT); else if (memcmp(ref, out, GOUT)) { printf("hash_g mismatch at %d\n", V); return 1; }
                             run_f(); if (V == 0) memcpy(ref_f, out, 32); else if (memcmp(ref_f, out, 32)) { printf("hash_f mismatch at %d\n", V); return 1; } }
  const char *nm[6] = {"O0 Official as written", "O1  - clear of the copy", "O2  - byte-wise tail absorb",
                       "O3  - temp[] squeeze", "O4  - input copy (prefix in place)", "GT shake256_prefixed"};
  printf("NTRU+%d, per call (%s); both on GT's permutation; all six forms agree on the digest\n", SET, UNIT);
  printf("  %-36s %10s %8s   %10s %8s\n", "", "hash_g", "step", "hash_f", "step");
  double pg = 0, pf = 0;
  for (V = 0; V <= 5; V++) { double g = best(run_g), f = best(run_f);
    if (V == 0) printf("  %-36s %10.1f %8s   %10.1f %8s\n", nm[V], g, "", f, "");
    else printf("  %-36s %10.1f %+8.1f   %10.1f %+8.1f\n", nm[V], g, g - pg, f, f - pf);
    pg = g; pf = f; }
  return 0; }
