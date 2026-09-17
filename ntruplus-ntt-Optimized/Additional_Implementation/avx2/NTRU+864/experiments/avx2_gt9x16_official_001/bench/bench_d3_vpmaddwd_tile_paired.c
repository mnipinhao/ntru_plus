#include <immintrin.h>
#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include "d3_vpmaddwd_tile.h"

#define BLOCKS 16
#define OBSERVATIONS 96
#define INNER 64
#define Q 3457
#define QINV 12929

typedef void (*tile_fn)(int16_t *, const int16_t *, const int16_t *,
                        const int16_t *, int16_t *);

static _Alignas(32) int16_t a[48];
static _Alignas(32) int16_t b[48];
static _Alignas(32) int16_t zeta[32];
static _Alignas(32) int16_t out[48];
static _Alignas(32) int16_t scratch[96];
static volatile int16_t sink;

static uint64_t cycles_start(void)
{
    unsigned int auxiliary;
    _mm_lfence();
    return __rdtscp(&auxiliary);
}

static uint64_t cycles_stop(void)
{
    unsigned int auxiliary;
    uint64_t value = __rdtscp(&auxiliary);
    _mm_lfence();
    return value;
}

static int compare_u64(const void *left, const void *right)
{
    uint64_t a0 = *(const uint64_t *)left;
    uint64_t b0 = *(const uint64_t *)right;
    return (a0 > b0) - (a0 < b0);
}

static uint64_t measure(tile_fn selected)
{
    uint64_t samples[OBSERVATIONS];
    for (int observation = 0; observation < OBSERVATIONS; ++observation) {
        uint64_t begin = cycles_start();
        for (int iteration = 0; iteration < INNER; ++iteration)
            selected(out, a, b, zeta, scratch);
        samples[observation] = (cycles_stop() - begin + INNER / 2) / INNER;
        sink ^= out[(observation * 17) % 48];
    }
    qsort(samples, OBSERVATIONS, sizeof samples[0], compare_u64);
    return (samples[OBSERVATIONS / 2 - 1] + samples[OBSERVATIONS / 2]) / 2;
}

int main(void)
{
    static const int odd[4] = {0, 1, 1, 0};
    static const int even[4] = {1, 0, 0, 1};
    tile_fn implementations[2] = {
        ntruplus864_exp001_d3_tile_baseline,
        ntruplus864_exp001_d3_tile_vpmaddwd,
    };
    const char *names[2] = {"two-P-plus-official-cubic", "direct-packed-vpmaddwd-mr32"};
    for (int i = 0; i < 48; ++i) {
        a[i] = (int16_t)((i * 2053u + 17u) % Q);
        b[i] = (int16_t)(i * 4051u + 0x8123u);
    }
    for (int i = 0; i < 16; ++i) {
        int16_t value = (int16_t)(((i * 733u + 19u) % Q) - (Q - 1) / 2);
        zeta[i] = (int16_t)((uint16_t)value * (uint16_t)QINV);
        zeta[16 + i] = value;
    }
    implementations[0](out, a, b, zeta, scratch);
    implementations[1](out, a, b, zeta, scratch);
    puts("{\"benchmark_class\":\"repository-local-d3-tile-paired-not-for-promotion\","
         "\"blocks\":16,\"observations_per_slot\":96,\"inner_calls\":64,\"records\":[");
    for (int block = 0; block < BLOCKS; ++block) {
        const int *order = (block & 1) == 0 ? odd : even;
        for (int slot = 0; slot < 4; ++slot) {
            int selected = order[slot];
            printf("{\"block\":%d,\"slot\":%d,\"implementation\":\"%s\","
                   "\"median_cycles\":%" PRIu64 "},\n",
                   block + 1, slot + 1, names[selected],
                   measure(implementations[selected]));
        }
    }
    printf("{\"block\":0,\"slot\":0,\"implementation\":\"sink\","
           "\"median_cycles\":%" PRId16 "}]}\n", sink);
    return 0;
}
