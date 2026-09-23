/*
 * Seed-matched paired Keypair harness for Official vs caller-lazy NTRU+864/1152
 * AVX2 (Phase-B follow-up).  supercop-derived diagnostic, not Native SUPERCOP.
 *
 * Both KEMs are linked into one ELF through the namespaced entries of
 * kem_diag.c (official_ref_keypair / official_lazy_keypair).  Per iteration the
 * harness derives one coin stream, SHAKE256(seed || iteration), outside the
 * timed region.  randombytes() serves that stream by memcpy and counts its
 * calls, so Official and candidate consume byte-identical coins in the same
 * iteration and hit identical f/g BaseInv retries (retries = calls - 2).
 * Each iteration times four calls in ABBA (even) / BAAB (odd) order with
 * SUPERCOP's cpucycles(), then checks outside the timed region that all four
 * calls made the same number of randombytes calls and that pk/sk are equal.
 *
 * Usage: bench_keypair_seedmatched <seed> <iterations> <warmup>
 * Output CSV: iteration,order,retries,official_1,lazy_1,lazy_2,official_2
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "cpucycles.h"
#include "fips202.h"
#include "params.h"

int official_ref_keypair(unsigned char *, unsigned char *);
int official_lazy_keypair(unsigned char *, unsigned char *);

enum { COIN_SLOTS = 32, COIN_BYTES = 32 };
static uint8_t stream[COIN_SLOTS * COIN_BYTES];
static size_t stream_pos;
static unsigned stream_calls;

void randombytes(unsigned char *x, unsigned long long n) {
    if (n > sizeof stream - stream_pos) __builtin_trap();
    memcpy(x, stream + stream_pos, n);
    stream_pos += n;
    stream_calls++;
}

static void derive_stream(uint64_t seed, uint64_t iteration) {
    uint8_t in[16];
    for (unsigned i = 0; i < 8; i++) {
        in[i] = (uint8_t)(seed >> (8 * i));
        in[8 + i] = (uint8_t)(iteration >> (8 * i));
    }
    shake256(stream, sizeof stream, in, sizeof in);
}

static uint8_t pk[4][NTRUPLUS_PUBLICKEYBYTES];
static uint8_t sk[4][NTRUPLUS_SECRETKEYBYTES];
static volatile int status_sink;

static long long timed(int lazy, unsigned slot, unsigned *calls) {
    stream_pos = 0;
    stream_calls = 0;
    long long start = cpucycles();
    status_sink = lazy ? official_lazy_keypair(pk[slot], sk[slot])
                       : official_ref_keypair(pk[slot], sk[slot]);
    long long cycles = cpucycles() - start;
    *calls = stream_calls;
    return cycles;
}

int main(int argc, char **argv) {
    if (argc != 4) {
        fprintf(stderr, "usage: %s seed iterations warmup\n", argv[0]);
        return 2;
    }
    uint64_t seed = strtoull(argv[1], NULL, 0);
    long iterations = strtol(argv[2], NULL, 0);
    long warmup = strtol(argv[3], NULL, 0);
    cpucycles_tracesetup();
    fprintf(stderr, "cpucycles=%s persecond=%lld\n", cpucycles_implementation(),
            cpucycles_persecond());
    puts("iteration,order,retries,official_1,lazy_1,lazy_2,official_2");
    for (long it = -warmup; it < iterations; it++) {
        /* warm-up iterations use a disjoint stream (high bit set) */
        derive_stream(seed, it < 0 ? (1ULL << 63) | (uint64_t)(-it) : (uint64_t)it);
        int baab = (int)(it & 1);
        /* ABBA: slot0=official slot1=lazy slot2=lazy slot3=official; BAAB swaps roles */
        static const int abba[4] = {0, 1, 1, 0}, baab_seq[4] = {1, 0, 0, 1};
        const int *seq = baab ? baab_seq : abba;
        long long cyc[4];
        unsigned calls[4];
        for (unsigned s = 0; s < 4; s++) cyc[s] = timed(seq[s], s, &calls[s]);
        for (unsigned s = 1; s < 4; s++) {
            if (calls[s] != calls[0]) __builtin_trap();
            if (memcmp(pk[s], pk[0], sizeof pk[0]) || memcmp(sk[s], sk[0], sizeof sk[0]))
                __builtin_trap();
        }
        if (calls[0] < 2) __builtin_trap();
        if (it < 0) continue;
        /* report in role order: official_1, lazy_1, lazy_2, official_2 (time order within role) */
        long long o[2], l[2];
        unsigned no = 0, nl = 0;
        for (unsigned s = 0; s < 4; s++) {
            if (seq[s]) l[nl++] = cyc[s];
            else o[no++] = cyc[s];
        }
        printf("%ld,%s,%u,%lld,%lld,%lld,%lld\n", it, baab ? "BAAB" : "ABBA", calls[0] - 2, o[0],
               l[0], l[1], o[1]);
    }
    fputs("seedmatched=pass\n", stderr);
    return 0;
}
