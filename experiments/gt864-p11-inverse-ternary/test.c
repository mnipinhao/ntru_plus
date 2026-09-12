#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "gt864_native.h"
#include "gt864_native_scaled_tables.h"

int probe_inverse(int16_t *, const int16_t *, const int16_t *, const int16_t *, const int16_t *, const int16_t *);

static uint32_t seed = 110864;
static uint32_t rnd(void) {
    seed ^= seed << 13;
    seed ^= seed >> 17;
    seed ^= seed << 5;
    return seed;
}

int main(void) {
    poly input, reference, output, alias;
    for (int trial = 0; trial < 4096; trial++) {
        for (int i = 0; i < 864; i++) {
            input.coeffs[i] = trial == 0 ? 2497 : trial == 1 ? -2497 : (int)(rnd() % 4995) - 2497;
        }
        gt864_native_inverse(&reference, &input);
        poly_crepmod3(&reference, &reference);
        gt864_native_inverse_ternary(&output, &input);
        alias = input;
        gt864_native_inverse_ternary(&alias, &alias);
        if (memcmp(&reference, &output, sizeof output) || memcmp(&reference, &alias, sizeof alias)) {
            fprintf(stderr, "mismatch trial %d\n", trial);
            return 1;
        }
        if (probe_inverse(output.coeffs, input.coeffs,
                &gt864_inverse9_twist_barrett[0][0][0][0][0],
                &gt864_inverse16_stage_barrett[0][0],
                &gt864_inverse16_main_scale_barrett[0][0][0],
                &gt864_inverse16_tail_scale_barrett[0][0][0])) {
            fprintf(stderr, "AAPCS/wipe failure trial %d\n", trial);
            return 2;
        }
        if (memcmp(&reference, &output, sizeof output)) return 3;
    }
    puts("PASS 4096 inverse-to-ternary exact/alias/AAPCS/scratch-wipe cases");
    return 0;
}
