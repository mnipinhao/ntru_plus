#define _GNU_SOURCE
#include "fused_tobytes.h"
#include "p3b5_tables.h"

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>

static uint32_t rng = 1;

static uint32_t next_u32(void)
{
    rng = rng * 1664525u + 1013904223u;
    return rng;
}

static int16_t canonical(int16_t value)
{
    int32_t result = value % 3457;
    return (int16_t)(result < 0 ? result + 3457 : result);
}

static void oracle(uint8_t out[1296], const int16_t fr0[864])
{
    for (int pair = 0; pair < 432; pair++) {
        uint16_t a = (uint16_t)canonical(fr0[p3b5_map[2 * pair]]);
        uint16_t b = (uint16_t)canonical(fr0[p3b5_map[2 * pair + 1]]);
        out[3 * pair] = (uint8_t)a;
        out[3 * pair + 1] = (uint8_t)((a >> 8) | (b << 4));
        out[3 * pair + 2] = (uint8_t)(b >> 4);
    }
}

static void fail_at(int test, const uint8_t expected[1296],
                    const uint8_t actual[1296])
{
    for (int i = 0; i < 1296; i++) {
        if (expected[i] != actual[i]) {
            fprintf(stderr,
                    "mismatch test=%d byte=%d expected=%u actual=%u\n",
                    test, i, expected[i], actual[i]);
            exit(1);
        }
    }
    exit(1);
}

int main(void)
{
    int16_t input[864];
    uint8_t expected[1296];
    uint8_t actual[1296];

    for (int test = 0; test < 256; test++) {
        for (int i = 0; i < 864; i++) {
            if (test == 0)
                input[i] = (int16_t)i;
            else if (test == 1)
                input[i] = INT16_MIN;
            else if (test == 2)
                input[i] = INT16_MAX;
            else if (test == 3)
                input[i] = (int16_t)((i & 1) ? -3457 : 3457);
            else
                input[i] = (int16_t)next_u32();
        }
        oracle(expected, input);
        memset(actual, 0xa5, sizeof actual);
        gt864_fr0_fused_tobytes(actual, input);
        if (memcmp(expected, actual, sizeof actual) != 0)
            fail_at(test, expected, actual);
    }

    /* Cover every signed-int16 input to close the reduction precondition. */
    for (int base = INT16_MIN; base <= INT16_MAX; base += 864) {
        for (int i = 0; i < 864; i++) {
            int32_t value = (int32_t)base + i;
            input[i] = (int16_t)(value <= INT16_MAX ? value : INT16_MAX);
        }
        oracle(expected, input);
        gt864_fr0_fused_tobytes(actual, input);
        if (memcmp(expected, actual, sizeof actual) != 0)
            fail_at(300 + (base - INT16_MIN) / 864, expected, actual);
        if (base > INT16_MAX - 864)
            break;
    }

    long page_size = sysconf(_SC_PAGESIZE);
    if (page_size <= 0)
        return 2;
    size_t page = (size_t)page_size;
    uint8_t *input_map = mmap(NULL, 3 * page, PROT_READ | PROT_WRITE,
                              MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    uint8_t *output_map = mmap(NULL, 3 * page, PROT_READ | PROT_WRITE,
                               MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (input_map == MAP_FAILED || output_map == MAP_FAILED)
        return 2;
    if (mprotect(input_map, page, PROT_NONE) != 0 ||
        mprotect(input_map + 2 * page, page, PROT_NONE) != 0 ||
        mprotect(output_map, page, PROT_NONE) != 0 ||
        mprotect(output_map + 2 * page, page, PROT_NONE) != 0)
        return 2;

    for (int edge = 0; edge < 2; edge++) {
        int16_t *guarded_input = (int16_t *)(input_map + page +
            (edge ? page - sizeof input : 0));
        uint8_t *guarded_output = output_map + page +
            (edge ? page - sizeof actual : 0);
        for (int i = 0; i < 864; i++)
            guarded_input[i] = (int16_t)(i - 432);
        oracle(expected, guarded_input);
        gt864_fr0_fused_tobytes(guarded_output, guarded_input);
        if (memcmp(expected, guarded_output, sizeof expected) != 0)
            fail_at(256 + edge, expected, guarded_output);
    }

    munmap(input_map, 3 * page);
    munmap(output_map, 3 * page);
    puts("p3b5_correctness=pass cases=256 int16_exhaustive=65536 "
         "guarded_edges=2 bytes=1296");
    return 0;
}
