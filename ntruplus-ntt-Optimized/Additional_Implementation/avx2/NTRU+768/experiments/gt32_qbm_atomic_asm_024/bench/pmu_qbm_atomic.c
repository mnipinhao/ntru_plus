#define _GNU_SOURCE
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "qbm_atomic.h"
#include "quadratic-constants.h"

enum { WORDS = 768, ITERATIONS = 1000000 };
static _Alignas(32) int16_t input_a[WORDS];
static _Alignas(32) int16_t input_b[WORDS];
static _Alignas(32) int16_t output[WORDS];

static int pin_first_available_cpu(void)
{
    cpu_set_t available, selected;
    if (sched_getaffinity(0, sizeof available, &available) != 0)
        return -1;
    for (int cpu = 0; cpu < CPU_SETSIZE; ++cpu) {
        if (!CPU_ISSET(cpu, &available))
            continue;
        CPU_ZERO(&selected);
        CPU_SET(cpu, &selected);
        return sched_setaffinity(0, sizeof selected, &selected) == 0 ? cpu : -1;
    }
    return -1;
}

int main(int argc, char **argv)
{
    if (argc != 2 || (strcmp(argv[1], "control") != 0 &&
                      strcmp(argv[1], "atomic") != 0))
        return 2;
    qbm_asm_fn function = strcmp(argv[1], "control") == 0
        ? qbm_selected_control_asm : qbm_atomic_expanded_asm;
    uint64_t random = UINT64_C(0x13198a2e03707344);
    int cpu = pin_first_available_cpu();
    for (size_t i = 0; i < WORDS; ++i) {
        random ^= random << 13; random ^= random >> 7; random ^= random << 17;
        input_a[i] = (int16_t)((int)(random % 6913) - 3456);
        random ^= random << 13; random ^= random >> 7; random ^= random << 17;
        input_b[i] = (int16_t)((int)(random % 6913) - 3456);
    }
    for (size_t i = 0; i < 1000; ++i)
        function(output, input_a, input_b,
                 round4c_weight_mont, round4c_weight_qinv);
    for (size_t i = 0; i < ITERATIONS; ++i)
        function(output, input_a, input_b,
                 round4c_weight_mont, round4c_weight_qinv);
    printf("mode=%s cpu=%d iterations=%d checksum=%d\n",
           argv[1], cpu, ITERATIONS, output[0]);
    return 0;
}
