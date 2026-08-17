#include "forward_intrinsic.h"
#include "lane_ntt16_intrinsic.h"

#include <stdint.h>
#include <stdio.h>
#include <string.h>

enum { Q = 3457 };

static uint32_t state = 0x4c414e45u;

static uint32_t random32(void)
{
    state ^= state << 13;
    state ^= state >> 17;
    state ^= state << 5;
    return state;
}

static int modq(int value)
{
    value %= Q;
    return value < 0 ? value + Q : value;
}

static int check_one(const int16_t input[16], size_t case_index)
{
    int16_t lane_output[16] __attribute__((aligned(32)));
    int16_t cross[768] __attribute__((aligned(32)));
    memset(cross, 0, sizeof(cross));
    for (size_t i = 0; i < 16; ++i)
        cross[16 * i] = input[i];
    round4c_forward_ntt16_intrinsic(cross);
    round4c_lane_ntt16_x1(lane_output, input);
    for (size_t i = 0; i < 16; ++i) {
        if (modq(lane_output[i]) != modq(cross[16 * i])) {
            fprintf(stderr,
                    "lane NTT16 mismatch case=%zu lane=%zu got=%d want=%d\n",
                    case_index, i, lane_output[i], cross[16 * i]);
            return 1;
        }
    }
    return 0;
}

int main(void)
{
    int16_t input[16] __attribute__((aligned(32)));
    int16_t triple_input[48] __attribute__((aligned(32)));
    int16_t triple_output[48] __attribute__((aligned(32)));
    int16_t single_output[16] __attribute__((aligned(32)));
    size_t cases = 0;
    memset(input, 0, sizeof(input));
    if (check_one(input, cases++))
        return 1;
    for (size_t impulse = 0; impulse < 16; ++impulse) {
        memset(input, 0, sizeof(input));
        input[impulse] = (impulse & 1) ? -1728 : 1728;
        if (check_one(input, cases++))
            return 1;
    }
    for (size_t random_case = 0; random_case < 256; ++random_case) {
        for (size_t i = 0; i < 16; ++i)
            input[i] = (int16_t)((int)(random32() % Q) - 1728);
        if (check_one(input, cases++))
            return 1;
    }
    for (size_t i = 0; i < 48; ++i)
        triple_input[i] = (int16_t)((int)(random32() % Q) - 1728);
    round4c_lane_ntt16_x3(triple_output, triple_input);
    for (size_t row = 0; row < 3; ++row) {
        round4c_lane_ntt16_x1(single_output, triple_input + 16 * row);
        if (memcmp(single_output, triple_output + 16 * row,
                   sizeof(single_output)) != 0) {
            fprintf(stderr, "lane NTT16 x1/x3 mismatch row=%zu\n", row);
            return 1;
        }
    }
    printf("lane-i16 NTT16 cases=%zu x1-x3=exact failures=0\n", cases);
    return 0;
}
