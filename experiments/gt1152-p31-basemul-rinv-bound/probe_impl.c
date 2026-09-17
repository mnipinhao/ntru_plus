#include <stdint.h>
#include <arm_neon.h>
#define Q 3457
extern int probe_pre, probe_post;
int16x8_t probe_normalize(int16x8_t a)
{
    const int16x8_t q = vdupq_n_s16(Q), hi = vdupq_n_s16(1728), lo = vdupq_n_s16(-1728);
    int16_t t[8];
    vst1q_s16(t, a);
    for (int i = 0; i < 8; i++) { int v = t[i] < 0 ? -t[i] : t[i]; if (v > probe_pre) probe_pre = v; }
    a = vsubq_s16(a, vandq_s16(vreinterpretq_s16_u16(vcgtq_s16(a, hi)), q));
    a = vaddq_s16(a, vandq_s16(vreinterpretq_s16_u16(vcltq_s16(a, lo)), q));
    vst1q_s16(t, a);
    for (int i = 0; i < 8; i++) { int v = t[i] < 0 ? -t[i] : t[i]; if (v > probe_post) probe_post = v; }
    return a;
}
