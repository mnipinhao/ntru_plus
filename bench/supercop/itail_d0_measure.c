#include <stdint.h>
#include "cpucycles.h"
#include "crypto_kem.h"
#include "measure.h"
#include "inverse_tail_d0_asm.h"

const char *primitiveimplementation = crypto_kem_IMPLEMENTATION;
const char *implementationversion = crypto_kem_VERSION;
const char *sizenames[] = { "repaired_d1_bytes", 0 };
const long long sizes[] = { sizeof(ntruplus1152_exp001_gt_terminal_major) };

static ntruplus1152_exp001_gt_terminal_major *input;
static ntruplus1152_exp001_gt_terminal_major *output;

void preallocate(void) {}

void allocate(void) {
  int branch, row, terminal, lane;
  input = (ntruplus1152_exp001_gt_terminal_major *)alignedcalloc(sizeof *input);
  output = (ntruplus1152_exp001_gt_terminal_major *)alignedcalloc(sizeof *output);
  for (branch = 0; branch < 2; ++branch)
    for (row = 0; row < 9; ++row)
      for (terminal = 0; terminal < 4; ++terminal)
        for (lane = 0; lane < 16; ++lane)
          input->state[branch][row][terminal][lane] = (int16_t)(
              ((branch * 71 + row * 43 + terminal * 17 + lane * 11 + 5)
               % 201) - 100);
}

#define TIMINGS 32
static long long cycles[TIMINGS + 1];

#define MEASURE_ENTRY(label, statement) do {                         \
  for (i = 0; i <= TIMINGS; ++i) {                                  \
    cycles[i] = cpucycles();                                        \
    statement;                                                      \
  }                                                                 \
  for (i = 0; i < TIMINGS; ++i) cycles[i] = cycles[i + 1] - cycles[i]; \
  printentry(-1, label, cycles, TIMINGS);                            \
} while (0)

void measure(void) {
  int i, loop;
  for (loop = 0; loop < LOOPS; ++loop) {
    MEASURE_ENTRY("inverse_tail_d0_m0_first_cycles",
                  ntruplus1152_exp001_inverse_tail_d0_m0(output, input));
    MEASURE_ENTRY("inverse_tail_d0_m1_second_cycles",
                  ntruplus1152_exp001_inverse_tail_d0_m1(output, input));
    MEASURE_ENTRY("inverse_tail_d0_m1_first_cycles",
                  ntruplus1152_exp001_inverse_tail_d0_m1(output, input));
    MEASURE_ENTRY("inverse_tail_d0_m0_second_cycles",
                  ntruplus1152_exp001_inverse_tail_d0_m0(output, input));
  }
}
