#include <stdint.h>
#include <stdio.h>
#include <string.h>

#define N 864
#define Q 3457

void gt864_forward_poly_ntt_p41_k1_kem_only(int16_t *out,
                                             const int16_t *in);

static uint64_t state = UINT64_C(0x5033380864150915);

static uint32_t next32(void)
{
    state ^= state << 13;
    state ^= state >> 7;
    state ^= state << 17;
    return (uint32_t)state;
}

static void make_input(int16_t a[N], unsigned trial, int keygen_f)
{
    if (trial < 2 * N) {
        memset(a, 0, N * sizeof(*a));
        a[trial % N] = (int16_t)((trial < N ? 1 : -1) *
                                 (keygen_f ? 3 : 1));
        if (keygen_f) a[0]++;
        return;
    }
    for (unsigned i = 0; i < N; i++) {
        int value = (int)(next32() % 3) - 1;
        a[i] = (int16_t)(keygen_f ? 3 * value : value);
    }
    if (keygen_f) a[0]++;
}

static void run_mode(const char *name, int keygen_f, int comma)
{
    int16_t in[N] __attribute__((aligned(16)));
    int16_t out[N] __attribute__((aligned(16)));
    int16_t outside_value[N] = {0};
    int outside_trial[N];
    unsigned outside = 0;
    int observed_min = 32767, observed_max = -32768;
    memset(outside_trial, 0xff, sizeof(outside_trial));

    for (unsigned trial = 0; trial < 32768; trial++) {
        make_input(in, trial, keygen_f);
        gt864_forward_poly_ntt_p41_k1_kem_only(out, in);
        for (unsigned i = 0; i < N; i++) {
            if (out[i] < observed_min) observed_min = out[i];
            if (out[i] > observed_max) observed_max = out[i];
            if (outside_trial[i] < 0 && (out[i] <= -Q || out[i] >= Q)) {
                outside_trial[i] = (int)trial;
                outside_value[i] = out[i];
                outside++;
            }
        }
    }

    printf("    \"%s\": {\n", name);
    printf("      \"trials\": 32768,\n");
    printf("      \"coordinates_observed_outside_small_contract\": %u,\n", outside);
    printf("      \"observed_output_range\": [%d, %d],\n", observed_min,
           observed_max);
    printf("      \"outside_witnesses\": [\n");
    unsigned emitted = 0;
    for (unsigned i = 0; i < N; i++) {
        if (outside_trial[i] < 0) continue;
        printf("        %s{\"coordinate\": %u, \"trial\": %d, \"value\": %d}\n",
               emitted++ ? ", " : "", i, outside_trial[i], outside_value[i]);
    }
    printf("      ]\n    }%s\n", comma ? "," : "");
}

int main(void)
{
    printf("{\n  \"modes\": {\n");
    run_mode("small", 0, 1);
    run_mode("keygen_f", 1, 0);
    printf("  }\n}\n");
    return 0;
}
