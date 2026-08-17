#include "forward_intrinsic.h"

#include <stdint.h>
#include <stdio.h>
#include <string.h>

enum { WORDS = 128, FRONTEND_BOUND = 1778 };

static uint32_t state = 0x43543853u;

static uint32_t random32(void)
{
    state ^= state << 13;
    state ^= state >> 17;
    state ^= state << 5;
    return state;
}

static int check_one(const int16_t input[WORDS], size_t case_index)
{
    int16_t baseline[WORDS] __attribute__((aligned(32)));
    int16_t scheduled[WORDS] __attribute__((aligned(32)));
    memcpy(baseline, input, sizeof(baseline));
    memcpy(scheduled, input, sizeof(scheduled));
    round4c_forward_ct8_baseline_asm(baseline);
    round4c_forward_ct8_sched_asm(scheduled);
    if (memcmp(baseline, scheduled, sizeof(baseline)) != 0) {
        for (size_t i = 0; i < WORDS; ++i) {
            if (baseline[i] != scheduled[i]) {
                fprintf(stderr,
                        "ct8 schedule mismatch case=%zu word=%zu got=%d want=%d\n",
                        case_index, i, scheduled[i], baseline[i]);
                break;
            }
        }
        return 1;
    }
    return 0;
}

int main(void)
{
    int16_t input[WORDS] __attribute__((aligned(32)));
    size_t cases = 0;
    memset(input, 0, sizeof(input));
    if (check_one(input, cases++))
        return 1;
    for (size_t impulse = 0; impulse < WORDS; ++impulse) {
        memset(input, 0, sizeof(input));
        input[impulse] = (impulse & 1) ? -FRONTEND_BOUND : FRONTEND_BOUND;
        if (check_one(input, cases++))
            return 1;
    }
    for (size_t pattern = 0; pattern < 4; ++pattern) {
        for (size_t i = 0; i < WORDS; ++i) {
            if (pattern == 0)
                input[i] = FRONTEND_BOUND;
            else if (pattern == 1)
                input[i] = -FRONTEND_BOUND;
            else if (pattern == 2)
                input[i] = (i & 1) ? -FRONTEND_BOUND : FRONTEND_BOUND;
            else
                input[i] = (i & 1) ? 4 : -3;
        }
        if (check_one(input, cases++))
            return 1;
    }
    for (size_t random_case = 0; random_case < 256; ++random_case) {
        for (size_t i = 0; i < WORDS; ++i)
            input[i] = (int16_t)((int)(random32() %
                               (2 * FRONTEND_BOUND + 1)) - FRONTEND_BOUND);
        if (check_one(input, cases++))
            return 1;
    }
    printf("ct8 fixed-vs-scheduled cases=%zu exact=pass failures=0\n", cases);
    return 0;
}
