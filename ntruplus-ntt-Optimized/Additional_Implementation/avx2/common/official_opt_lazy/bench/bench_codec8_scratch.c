/*
 * SCRATCH decision-gate measurement (supercop-derived, not Native) for a direct
 * 12-bit codec on the Official NTRU+768 / NTRU+1152 AVX2 8-way layout.  Same
 * structure as bench_freeze2op.c: cpucycles from the disposable SUPERCOP
 * campaign, 16 banks, 32 observations per block, 4 warm-ups per slot, 12
 * rotated blocks (balanced for 2- and 4-variant rotations), one call per
 * observation (the perf-event cpucycles overhead, ~220 cycles, cancels in deltas).
 *
 * Build with -DFREEZE_TOBYTES=ntruplus{N}_officialopt_tobytes_freeze2op.
 *   region 0 tobytes    0 Official  1 freeze2op  2 scratch pack  3 scratch madd
 *   region 1 frombytes  0 Official  1 scratch
 *
 * `bench_codec8_scratch check` instead runs the differential sweep (every int16
 * at every position for K = 0, 1, 40503; random polys; every 12-bit value at
 * every position; random valid and random byte strings; wire and poly guard
 * canaries) and exits.
 */
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "cpucycles.h"
#include "params.h"
#include "poly.h"

void FREEZE_TOBYTES(uint8_t *, const poly *);
void codec8_scratch_tobytes_pack(uint8_t *, const poly *);
void codec8_scratch_tobytes_madd(uint8_t *, const poly *);
int codec8_scratch_frombytes(poly *, const uint8_t *);

enum { BANKS = 16, OBS = 32, BLOCKS = 12, REGIONS = 2, MAXV = 4, PAD = 64 };
static poly src_poly[BANKS], dst_poly[BANKS];
static uint8_t wire[BANKS][NTRUPLUS_POLYBYTES];
static uint8_t bytes_out[BANKS][NTRUPLUS_POLYBYTES];
static volatile int status_sink;

static uint64_t rng_state = 0x9e3779b97f4a7c15ULL;
static uint64_t rnd(void) {
    rng_state ^= rng_state << 13; rng_state ^= rng_state >> 7; rng_state ^= rng_state << 17;
    return rng_state;
}

typedef void (*operation)(unsigned);
static void tb_o(unsigned b) { poly_tobytes(bytes_out[b], &src_poly[b]); }
static void tb_f(unsigned b) { FREEZE_TOBYTES(bytes_out[b], &src_poly[b]); }
static void tb_p(unsigned b) { codec8_scratch_tobytes_pack(bytes_out[b], &src_poly[b]); }
static void tb_m(unsigned b) { codec8_scratch_tobytes_madd(bytes_out[b], &src_poly[b]); }
static void fb_o(unsigned b) { status_sink = poly_frombytes(&dst_poly[b], wire[b]); }
static void fb_s(unsigned b) { status_sink = codec8_scratch_frombytes(&dst_poly[b], wire[b]); }
static const unsigned nvariants[REGIONS] = {4, 2};
static operation ops[REGIONS][MAXV] = {{tb_o, tb_f, tb_p, tb_m}, {fb_o, fb_s}};

/* ------------------------------------------------------------ differential */
typedef void (*tobytes_fn)(uint8_t *, const poly *);
static const tobytes_fn tb_impl[] = {FREEZE_TOBYTES, codec8_scratch_tobytes_pack,
                                     codec8_scratch_tobytes_madd};
static struct { uint8_t pre[PAD]; uint8_t b[NTRUPLUS_POLYBYTES]; uint8_t post[PAD]; } w_ref, w_out;
static struct { poly p; uint8_t post[PAD]; } p_ref, p_out;
static long tb_cases, fb_cases, fb_rejected, failures;

static void tb_case(const poly *a) {
    memset(&w_ref, 0xA5, sizeof w_ref);
    poly_tobytes(w_ref.b, a);
    for (unsigned k = 0; k < sizeof tb_impl / sizeof tb_impl[0]; k++) {
        memset(&w_out, 0xA5, sizeof w_out);
        poly in_copy = *a;
        tb_impl[k](w_out.b, &in_copy);
        if (memcmp(&w_ref, &w_out, sizeof w_ref) || memcmp(&in_copy, a, sizeof in_copy)) failures++;
    }
    tb_cases++;
}

static void fb_case(const uint8_t *bytes) {
    memset(&p_ref, 0x5A, sizeof p_ref);
    memset(&p_out, 0x5A, sizeof p_out);
    memset(&w_out, 0xC3, sizeof w_out);
    memcpy(w_out.b, bytes, NTRUPLUS_POLYBYTES);
    int x = poly_frombytes(&p_ref.p, bytes);
    int y = codec8_scratch_frombytes(&p_out.p, w_out.b);
    if (x != y || memcmp(&p_ref, &p_out, sizeof p_ref) || memcmp(w_out.b, bytes, NTRUPLUS_POLYBYTES))
        failures++;
    fb_rejected += x;
    fb_cases++;
}

static void set12(uint8_t *b, unsigned pos, unsigned v) {
    unsigned o = 3 * (pos / 2);
    if (pos & 1) { b[o + 1] = (uint8_t)((b[o + 1] & 15) | ((v & 15) << 4)); b[o + 2] = (uint8_t)(v >> 4); }
    else { b[o] = (uint8_t)v; b[o + 1] = (uint8_t)((b[o + 1] & 0xf0) | (v >> 8)); }
}

static int check(void) {
    static poly a;
    static uint8_t bg[NTRUPLUS_POLYBYTES], t[NTRUPLUS_POLYBYTES];
    static const int mul[3] = {0, 1, 40503};
    for (unsigned k = 0; k < 3; k++)
        for (unsigned base = 0; base < 65536; base++) {
            for (unsigned i = 0; i < NTRUPLUS_N; i++) a.coeffs[i] = (int16_t)(base + mul[k] * i);
            tb_case(&a);
        }
    for (unsigned n = 0; n < 20000; n++) {
        for (unsigned i = 0; i < NTRUPLUS_N; i++) a.coeffs[i] = (int16_t)rnd();
        tb_case(&a);
    }
    for (unsigned i = 0; i < NTRUPLUS_N; i++) a.coeffs[i] = (int16_t)(rnd() % NTRUPLUS_Q);
    poly_tobytes(bg, &a);
    for (unsigned pos = 0; pos < NTRUPLUS_N; pos++)
        for (unsigned v = 0; v < 4096; v++) { memcpy(t, bg, sizeof t); set12(t, pos, v); fb_case(t); }
    for (unsigned v = 0; v < 4096; v++) {
        for (unsigned pos = 0; pos < NTRUPLUS_N; pos++) set12(t, pos, v);
        fb_case(t);
    }
    for (unsigned n = 0; n < 20000; n++) {
        for (unsigned i = 0; i < NTRUPLUS_N; i++) a.coeffs[i] = (int16_t)(rnd() % NTRUPLUS_Q);
        poly_tobytes(t, &a); fb_case(t);
        for (unsigned i = 0; i < sizeof t; i++) t[i] = (uint8_t)rnd();
        fb_case(t);
    }
    printf("{\"param\": %d, \"tobytes_cases\": %ld, \"tobytes_impls\": 3, \"frombytes_cases\": %ld, "
           "\"frombytes_rejected_by_official\": %ld, \"failures\": %ld}\n",
           NTRUPLUS_N, tb_cases, fb_cases, fb_rejected, failures);
    return failures != 0;
}

/* ------------------------------------------------------------ timing */
static void fixture(void) {
    for (unsigned b = 0; b < BANKS; b++) {
        for (unsigned i = 0; i < NTRUPLUS_N; i++) src_poly[b].coeffs[i] = (int16_t)rnd();
        poly tmp;
        for (unsigned i = 0; i < NTRUPLUS_N; i++) tmp.coeffs[i] = (int16_t)(rnd() % NTRUPLUS_Q);
        poly_tobytes(wire[b], &tmp);
    }
}

static void preflight(void) {
    for (unsigned b = 0; b < BANKS; b++) {
        uint8_t ref[NTRUPLUS_POLYBYTES];
        tb_o(b); memcpy(ref, bytes_out[b], sizeof ref);
        for (unsigned v = 1; v < nvariants[0]; v++) {
            memset(bytes_out[b], 0, sizeof bytes_out[b]);
            ops[0][v](b);
            if (memcmp(ref, bytes_out[b], sizeof ref)) __builtin_trap();
        }
        poly pref;
        fb_o(b); if (status_sink) __builtin_trap();
        pref = dst_poly[b];
        memset(&dst_poly[b], 0, sizeof dst_poly[b]);
        fb_s(b); if (status_sink || memcmp(&pref, &dst_poly[b], sizeof pref)) __builtin_trap();
    }
    fputs("preflight=pass\n", stderr);
}

int main(int argc, char **argv) {
    if (argc > 1 && !strcmp(argv[1], "check")) return check();
    fixture();
    preflight();
    cpucycles_tracesetup();
    fprintf(stderr, "cpucycles=%s persecond=%lld\n", cpucycles_implementation(), cpucycles_persecond());
    puts("region,variant,block,observation,cycles");
    for (unsigned region = 0; region < REGIONS; region++) {
        unsigned nv = nvariants[region];
        for (unsigned block = 0; block < BLOCKS; block++)
            for (unsigned slot = 0; slot < nv; slot++) {
                unsigned variant = (block + slot) % nv;
                operation run = ops[region][variant];
                for (unsigned warm = 0; warm < 4; warm++) run(warm);
                for (unsigned obs = 0; obs < OBS; obs++) {
                    unsigned bank = obs & (BANKS - 1);
                    long long start = cpucycles();
                    run(bank);
                    long long cycles = cpucycles() - start;
                    printf("%u,%u,%u,%u,%lld\n", region, variant, block, obs, cycles);
                }
            }
    }
    return 0;
}
