#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "../../ntruplus-GT-Production/Additional_Implementation/aarch64/NTRU+864/gt864_native_scaled_tables.h"
#include "../gt864-p13b-inverse16-arithmetic/composite_tables.h"
#include "route-masks.h"

void p13b_i16(int16_t *out, const int16_t *in, const void *unused,
              const int16_t *stage, const int16_t *composite);
void p28_paired_i16(int16_t *a, int16_t *b, const void *unused,
                    const int16_t *stage, const int16_t *composite);
void p13c_itail(int16_t *out, const int16_t *in, const void *unused,
                const int16_t *stage, const int16_t *composite);
void p28_dense_tail(int16_t *inout, const void *unused1, const void *unused2,
                    const int16_t *stage, const int16_t *composite);
void p28_route_ternary(int16_t *out, const int16_t *scratch,
                       const uint8_t *masks);

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
  _Alignas(16) int16_t a[128], b[128], ca[128], cb[128];
  _Alignas(16) int16_t tail[128], ctail[128];
  _Alignas(16) int16_t ra[864], rb[864], rt[864];
  _Alignas(16) int16_t scratch[896], candidate[896], natural[864], routed[864];
  for (unsigned iteration = 0; iteration < 1001; iteration++) {
    for (unsigned i = 0; i < 128; i++) {
      a[i] = sample(iteration, i);
      b[i] = sample(iteration, i + 137);
      tail[i] = sample(iteration, i + 311);
    }
    for (unsigned i = 0; i < 896; i++) scratch[i] = sample(iteration, i + 701);
    memcpy(ca, a, sizeof(a));
    memcpy(cb, b, sizeof(b));
    memcpy(ctail, tail, sizeof(tail));
    memset(ra, 0x5a, sizeof(ra));
    memset(rb, 0x5a, sizeof(rb));
    p13b_i16(ra, a, NULL, &gt864_inverse16_stage_barrett[0][0],
             &gt864_p13b_main[0][0]);
    p13b_i16(rb, b, NULL, &gt864_inverse16_stage_barrett[0][0],
             &gt864_p13b_main[0][0]);
    p28_paired_i16(ca, cb, NULL, &gt864_inverse16_stage_barrett[0][0],
                   &gt864_p13b_main[0][0]);
    p13c_itail(rt, tail, NULL, &gt864_inverse16_stage_barrett[0][0],
               &gt864_p13b_tail[0][0]);
    p28_dense_tail(ctail, NULL, NULL, &gt864_inverse16_stage_barrett[0][0],
                   &gt864_p13b_tail[0][0]);
    for (unsigned t = 0; t < 16; t++) {
      for (unsigned lane = 0; lane < 4; lane++) {
        const int16_t want_al = ra[27 * t + 3 * lane];
        const int16_t want_bl = rb[27 * t + 3 * lane];
        const int16_t want_ah = ra[432 + 27 * t + 3 * lane];
        const int16_t want_bh = rb[432 + 27 * t + 3 * lane];
        if (ca[8 * t + lane] != want_al || ca[8 * t + 4 + lane] != want_bl ||
            cb[8 * t + lane] != want_ah || cb[8 * t + 4 + lane] != want_bh) {
          fprintf(stderr,
                  "mismatch iter=%u t=%u lane=%u got=(%d,%d,%d,%d) want=(%d,%d,%d,%d)\n",
                  iteration, t, lane, ca[8*t+lane], ca[8*t+4+lane],
                  cb[8*t+lane], cb[8*t+4+lane], want_al, want_bl, want_ah, want_bh);
          return 1;
        }
      }
      for (unsigned component = 0; component < 3; component++) {
        const unsigned linear = 3 * t + component;
        if (ctail[linear] != rt[27 * t + component] ||
            ctail[48 + linear] != rt[432 + 27 * t + component]) {
          fprintf(stderr, "tail mismatch iter=%u t=%u component=%u\n",
                  iteration, t, component);
          return 1;
        }
      }
    }
    memcpy(candidate, scratch, sizeof(scratch));
    memset(natural, 0x5a, sizeof(natural));
    for (unsigned component = 0; component < 3; component++) {
      for (unsigned half = 0; half < 2; half++) {
        unsigned block = 2 * component + half;
        p13b_i16(natural + component + 12 * half, scratch + 128 * block, NULL,
                 &gt864_inverse16_stage_barrett[0][0], &gt864_p13b_main[0][0]);
      }
    }
    p13c_itail(natural + 24, scratch + 768, NULL,
                &gt864_inverse16_stage_barrett[0][0], &gt864_p13b_tail[0][0]);
    p28_paired_i16(candidate + 0, candidate + 256, NULL,
                   &gt864_inverse16_stage_barrett[0][0], &gt864_p13b_main[0][0]);
    p28_paired_i16(candidate + 128, candidate + 512, NULL,
                   &gt864_inverse16_stage_barrett[0][0], &gt864_p13b_main[0][0]);
    p28_paired_i16(candidate + 384, candidate + 640, NULL,
                   &gt864_inverse16_stage_barrett[0][0], &gt864_p13b_main[0][0]);
    p28_dense_tail(candidate + 768, NULL, NULL,
                   &gt864_inverse16_stage_barrett[0][0], &gt864_p13b_tail[0][0]);
    p28_route_ternary(routed, candidate, &gt864_p28_route_masks[0][0][0]);
    for (unsigned i = 0; i < 864; i++) {
      if (routed[i] != ternary(natural[i])) {
        fprintf(stderr, "route mismatch iter=%u coefficient=%u got=%d want=%d raw=%d\n",
                iteration, i, routed[i], ternary(natural[i]), natural[i]);
        return 1;
      }
    }
  }
  puts("P28 complete paired-main+dense-tail-route oracle: 1001/1001 exact cases passed");
  return 0;
}
