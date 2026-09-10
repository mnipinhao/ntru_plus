#include <stdint.h>
#include <stdio.h>
#include <string.h>

enum { N = 864, BYTES = 1296, Q = 3457, CANARY = 32 };

void p4_baseline_decode(int16_t out[N], const uint8_t in[BYTES]);
int p4_candidate_checked(int16_t out[N], const uint8_t in[BYTES]);

static uint32_t state = 0x8645a17u;

static uint32_t next_u32(void)
{
    state = state * 1664525u + 1013904223u;
    return state;
}

static void pack(uint8_t out[BYTES], const uint16_t values[N])
{
    for (int i = 0; i < N; i += 2) {
        uint16_t a = values[i], b = values[i + 1];
        out[3 * i / 2 + 0] = (uint8_t)a;
        out[3 * i / 2 + 1] = (uint8_t)((a >> 8) | (b << 4));
        out[3 * i / 2 + 2] = (uint8_t)(b >> 4);
    }
}

static int check(const uint16_t values[N], unsigned trial)
{
    uint8_t input[BYTES];
    struct guarded { uint8_t pre[CANARY]; int16_t data[N]; uint8_t post[CANARY]; } baseline, candidate;
    pack(input, values);
    memset(&baseline, 0xa5, sizeof baseline);
    memset(&candidate, 0xa5, sizeof candidate);
    p4_baseline_decode(baseline.data, input);
    int observed = p4_candidate_checked(candidate.data, input);
    int expected = 0;
    for (int i = 0; i < N; i++)
        expected |= values[i] >= Q;
    if (observed != expected || memcmp(baseline.data, candidate.data, sizeof baseline.data) ||
        memcmp(baseline.pre, candidate.pre, CANARY) || memcmp(baseline.post, candidate.post, CANARY)) {
        fprintf(stderr, "P4 verify failure at trial %u: status %d expected %d\n", trial, observed, expected);
        return 1;
    }
    return 0;
}

int main(void)
{
    uint16_t values[N];
    unsigned trial = 0;
    const uint16_t uniform[] = {0, Q - 1, Q, 4095};
    for (unsigned u = 0; u < sizeof uniform / sizeof uniform[0]; u++) {
        for (int i = 0; i < N; i++) values[i] = uniform[u];
        if (check(values, trial++)) return 1;
    }
    for (int position = 0; position < N; position++) {
        for (int i = 0; i < N; i++) values[i] = 0;
        values[position] = Q - 1;
        if (check(values, trial++)) return 1;
        values[position] = Q;
        if (check(values, trial++)) return 1;
    }
    for (int random_trial = 0; random_trial < 4096; random_trial++) {
        for (int i = 0; i < N; i++) values[i] = next_u32() & 4095;
        if (check(values, trial++)) return 1;
    }
    printf("P4 fused legality: PASS cases=%u boundary_positions=%d random=4096 canaries=pass\n", trial, N);
    return 0;
}
