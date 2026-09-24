/* P134: the full serializer's reduction, old (Barrett, then sign mask + mls)
 * against new (Barrett, then add + umin), for every int16 input. */
#include <arm_neon.h>
#include <stdio.h>
#define Q 3457
static int16x8_t old_r(int16x8_t a){ int16x8_t t = vqrdmulhq_n_s16(a, 9); a = vmlsq_n_s16(a, t, (int16_t)Q);
  int16x8_t m = vreinterpretq_s16_u16(vcltq_s16(a, vdupq_n_s16(0))); return vmlsq_n_s16(a, m, (int16_t)Q); }
static int16x8_t new_r(int16x8_t a){ int16x8_t t = vqrdmulhq_n_s16(a, 9); a = vmlsq_n_s16(a, t, (int16_t)Q);
  uint16x8_t u = vreinterpretq_u16_s16(a); return vreinterpretq_s16_u16(vminq_u16(u, vaddq_u16(u, vdupq_n_u16(Q)))); }
int main(void){ int bad = 0, lo = 99999, hi = -99999;
  for (int x = -32768; x < 32768; x += 8) {
    int16_t in[8], o[8], n[8]; for (int i = 0; i < 8; i++) in[i] = (int16_t)(x + i);
    vst1q_s16(o, old_r(vld1q_s16(in))); vst1q_s16(n, new_r(vld1q_s16(in)));
    for (int i = 0; i < 8; i++) { bad += o[i] != n[i]; if (n[i] < lo) lo = n[i]; if (n[i] > hi) hi = n[i];
      int want = ((in[i] % Q) + Q) % Q; bad += n[i] != want; } }
  printf("65536 inputs: %d disagreements (old vs new, or vs x mod q); output range [%d, %d]\n", bad, lo, hi); return bad != 0; }
