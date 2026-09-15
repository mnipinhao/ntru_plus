#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "../../ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864/gt864_native_scaled_tables.h"
#include "../gt864-p13b-inverse16-arithmetic/composite_tables.h"

void p13b_i16(int16_t *, const int16_t *, const void *, const int16_t *, const int16_t *);
void p13c_itail(int16_t *, const int16_t *, const void *, const int16_t *, const int16_t *);
void p28_paired_i16(int16_t *, int16_t *, const void *, const int16_t *, const int16_t *);
void p29_tail_direct(int16_t *, const int16_t *, const void *, const int16_t *, const int16_t *);
void p29_main_route(int16_t *, const int16_t *);

static uint32_t rng = 1;
static uint32_t next_u32(void) {
  rng ^= rng << 13;
  rng ^= rng >> 17;
  rng ^= rng << 5;
  return rng;
}
static int16_t sample(unsigned iteration, unsigned index) {
  static const int16_t edge[] = {-2617, -2616, -1, 0, 1, 2616, 2617};
  if (iteration == 0) return edge[index % (sizeof(edge) / sizeof(edge[0]))];
  return (int16_t)((int)(next_u32() % 5235) - 2617);
}
static int16_t ternary(int value) {
  value = value - (value > 1728) + (value < -1728);
  int quotient = (value * 10923 + 16384) >> 15;
  return (int16_t)(value - 3 * quotient);
}

int main(void) {
  _Alignas(16) int16_t scratch[896], candidate[896];
  _Alignas(16) int16_t natural[864], routed[864];
  for (unsigned iteration = 0; iteration < 1001; iteration++) {
    for (unsigned i = 0; i < 896; i++) scratch[i] = sample(iteration, i);
    memcpy(candidate, scratch, sizeof scratch);
    memset(natural, 0x5a, sizeof natural);
    memset(routed, 0x5a, sizeof routed);

    for (unsigned component = 0; component < 3; component++) {
      for (unsigned half = 0; half < 2; half++) {
        unsigned block = 2 * component + half;
        p13b_i16(natural + component + 12 * half, scratch + 128 * block, 0,
                 &gt864_inverse16_stage_barrett[0][0], &gt864_p13b_main[0][0]);
      }
    }
    p13c_itail(natural + 24, scratch + 768, 0,
                &gt864_inverse16_stage_barrett[0][0], &gt864_p13b_tail[0][0]);

    // Equal-row-half pairing: G00+G10, G01+G11, G20+G21.
    p28_paired_i16(candidate + 0, candidate + 256, 0,
                   &gt864_inverse16_stage_barrett[0][0], &gt864_p13b_main[0][0]);
    p28_paired_i16(candidate + 128, candidate + 384, 0,
                   &gt864_inverse16_stage_barrett[0][0], &gt864_p13b_main[0][0]);
    p28_paired_i16(candidate + 512, candidate + 640, 0,
                   &gt864_inverse16_stage_barrett[0][0], &gt864_p13b_main[0][0]);
    p29_tail_direct(routed, candidate + 768, 0,
                    &gt864_inverse16_stage_barrett[0][0], &gt864_p13b_tail[0][0]);
    p29_main_route(routed, candidate);

    for (unsigned i = 0; i < 864; i++) {
      int16_t want = ternary(natural[i]);
      if (routed[i] != want) {
        fprintf(stderr, "P29 mismatch iteration=%u coefficient=%u got=%d want=%d raw=%d\n",
                iteration, i, routed[i], want, natural[i]);
        return 1;
      }
    }
  }
  puts("P29 equal-half paired + direct full-ST3 oracle: 1001/1001 exact cases passed");
  return 0;
}
