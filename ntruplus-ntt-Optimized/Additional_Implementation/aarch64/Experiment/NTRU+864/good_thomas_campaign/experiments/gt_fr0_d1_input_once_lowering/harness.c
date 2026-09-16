#include "lowered_tobytes.h"

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void gt864_fr0_input_once_tobytes(uint8_t out[1296],
                                  const int16_t fr0[864]);

static uint32_t rng = 1;

static uint32_t next_u32(void)
{
    rng = rng * 1664525u + 1013904223u;
    return rng;
}

int main(void)
{
    int16_t input[864] __attribute__((aligned(16)));
    uint8_t control[1296], actual[1296];
    for (int test = 0; test < 256; test++) {
        for (int index = 0; index < 864; index++) {
            if (test == 0)
                input[index] = (int16_t)index;
            else if (test == 1)
                input[index] = INT16_MIN;
            else if (test == 2)
                input[index] = INT16_MAX;
            else
                input[index] = (int16_t)next_u32();
        }
        gt864_fr0_input_once_tobytes(control, input);
        gt864_fr0_input_once_l1_tobytes(actual, input);
        if (memcmp(control, actual, sizeof control) != 0)
            return 1;
        gt864_fr0_input_once_l12_tobytes(actual, input);
        if (memcmp(control, actual, sizeof control) != 0)
            return 1;
    }
    puts("p3b7_correctness=pass cases=256 bytes=1296 variants=2");
    return 0;
}
