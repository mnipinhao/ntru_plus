/*
 * Same-binary benchmark wrapper for the unmodified KPQC-final poly_baseinv
 * algorithm. The companion ASM object is built from KPQC-final asm/base.s and
 * receives prefixed external symbols with objcopy.
 */
#include <stdint.h>
#include <string.h>

#include <arm_neon.h>

#include "poly.h"

static const int16_t kpqc_final_consts[8] __attribute__((aligned(16))) = {
    0x0d81, 0x4bd4, (int16_t)0xcd7f, (int16_t)0xff6d,
    (int16_t)0xfa8f, (int16_t)0xf9dd, (int16_t)0xc5d5, 0x0000};

void kpqc_final_poly_baseinv_1_for_bench(poly *r, int16x8_t *den,
                                         const poly *a);
void kpqc_final_poly_basemul_for_bench(poly *r, const poly *a,
                                       const poly *b);
int kpqc_final_poly_baseinv_for_bench(poly *r, const poly *a);
int kpqc_final_poly_baseinv_hier_k8_fqinv15_for_bench(poly *r,
                                                       const poly *a);
int kpqc_final_poly_baseinv_gt_layout_for_bench(poly *r, const poly *a);
void kpqc_final_poly_baseinv_prepare_for_bench(
    poly *r, int16_t den_out[24 * 8], const poly *a);
int kpqc_final_poly_fqinv_batch_for_bench(int16_t den_buf[24 * 8]);
int poly_baseinv_normal_hier_k8_tree_for_bench(int16_t den_buf[24 * 8]);

static inline int16x8_t kpqc_final_fqmul_neon(int16x8_t x, int16x8_t y,
                                              int16x8_t con)
{
  int32x4_t lo = vmull_s16(vget_low_s16(x), vget_low_s16(y));
  int32x4_t hi = vmull_high_s16(x, y);
  int16x8_t t;

  t = vuzp1q_s16(vreinterpretq_s16_s32(lo),
                  vreinterpretq_s16_s32(hi));
  t = vmulq_laneq_s16(t, con, 2);
  lo = vmlal_lane_s16(lo, vget_low_s16(t), vget_low_s16(con), 0);
  hi = vmlal_high_lane_s16(hi, t, vget_low_s16(con), 0);

  return vuzp2q_s16(vreinterpretq_s16_s32(lo),
                     vreinterpretq_s16_s32(hi));
}

static inline int16x8_t kpqc_final_fqinv16_neon(int16x8_t a,
                                                int16x8_t con)
{
  int16x8_t t1, t2, t3;

  t1 = kpqc_final_fqmul_neon(a, a, con);
  t2 = kpqc_final_fqmul_neon(t1, t1, con);
  t2 = kpqc_final_fqmul_neon(t2, t2, con);
  t3 = kpqc_final_fqmul_neon(t2, t2, con);
  t1 = kpqc_final_fqmul_neon(t1, t2, con);
  t2 = kpqc_final_fqmul_neon(t1, t3, con);
  t2 = kpqc_final_fqmul_neon(t2, t2, con);
  t2 = kpqc_final_fqmul_neon(t2, a, con);
  t1 = kpqc_final_fqmul_neon(t1, t2, con);
  t2 = kpqc_final_fqmul_neon(t2, t2, con);
  t2 = kpqc_final_fqmul_neon(t2, t2, con);
  t2 = kpqc_final_fqmul_neon(t2, t2, con);
  t2 = kpqc_final_fqmul_neon(t2, t2, con);
  t2 = kpqc_final_fqmul_neon(t2, t2, con);
  t2 = kpqc_final_fqmul_neon(t2, t2, con);
  t2 = kpqc_final_fqmul_neon(t2, t1, con);

  t1 = vqrdmulhq_laneq_s16(t2, con, 6);
  t2 = vmulq_laneq_s16(t2, con, 5);
  return vmlsq_laneq_s16(t2, t1, con, 0);
}

static int kpqc_final_fqinv_batch(int16x8_t r[24], int16x8_t con)
{
  int16x8_t c[24];
  int16x8_t inv;

  c[0] = r[0];
  for (int i = 1; i < 24; i++)
    c[i] = kpqc_final_fqmul_neon(c[i - 1], r[i], con);

  if (!vminvq_u16(vreinterpretq_u16_s16(c[23])))
    return 1;

  inv = kpqc_final_fqinv16_neon(c[23], con);
  for (int i = 23; i > 0; i--)
  {
    int16x8_t ri = r[i];

    r[i] = kpqc_final_fqmul_neon(c[i - 1], inv, con);
    inv = kpqc_final_fqmul_neon(inv, ri, con);
  }
  r[0] = inv;
  return 0;
}

static void kpqc_final_poly_baseinv_2(poly *r, int16x8_t den[24],
                                      int16x8_t con)
{
  int16_t *rp = r->coeffs;

  for (int i = 0; i < 24; i++)
  {
    const int offset = i * 32;
    int16x8_t pden = den[i];
    int16x8_t mden = vnegq_s16(pden);
    int16x8_t r0 = vld1q_s16(rp + offset + 0);
    int16x8_t r1 = vld1q_s16(rp + offset + 8);
    int16x8_t r2 = vld1q_s16(rp + offset + 16);
    int16x8_t r3 = vld1q_s16(rp + offset + 24);

    r0 = kpqc_final_fqmul_neon(r0, pden, con);
    r1 = kpqc_final_fqmul_neon(r1, mden, con);
    r2 = kpqc_final_fqmul_neon(r2, pden, con);
    r3 = kpqc_final_fqmul_neon(r3, mden, con);

    vst1q_s16(rp + offset + 0, r0);
    vst1q_s16(rp + offset + 8, r1);
    vst1q_s16(rp + offset + 16, r2);
    vst1q_s16(rp + offset + 24, r3);
  }
}

int kpqc_final_poly_baseinv_for_bench(poly *r, const poly *a)
{
  int16x8_t con = vld1q_s16(kpqc_final_consts);
  int16x8_t den[24] __attribute__((aligned(16)));

  kpqc_final_poly_baseinv_1_for_bench(r, den, a);
  if (kpqc_final_fqinv_batch(den, con))
  {
    for (int i = 0; i < NTRUPLUS_N; i++)
      r->coeffs[i] = 0;
    return 1;
  }

  kpqc_final_poly_baseinv_2(r, den, con);
  return 0;
}

int kpqc_final_poly_baseinv_hier_k8_fqinv15_for_bench(poly *r,
                                                       const poly *a)
{
  int16x8_t con = vld1q_s16(kpqc_final_consts);
  int16_t den_buf[24 * 8] __attribute__((aligned(16)));
  int16x8_t den[24] __attribute__((aligned(16)));

  kpqc_final_poly_baseinv_1_for_bench(r, den, a);
  for (int i = 0; i < 24; i++)
    vst1q_s16(den_buf + 8 * i, den[i]);

  if (poly_baseinv_normal_hier_k8_tree_for_bench(den_buf))
  {
    memset(r->coeffs, 0, sizeof(r->coeffs));
    return 1;
  }

  for (int i = 0; i < 24; i++)
    den[i] = vld1q_s16(den_buf + 8 * i);
  kpqc_final_poly_baseinv_2(r, den, con);
  return 0;
}

void kpqc_final_poly_baseinv_prepare_for_bench(
    poly *r, int16_t den_out[24 * 8], const poly *a)
{
  int16x8_t den[24] __attribute__((aligned(16)));

  kpqc_final_poly_baseinv_1_for_bench(r, den, a);
  for (int i = 0; i < 24; i++)
    vst1q_s16(den_out + 8 * i, den[i]);
}

int kpqc_final_poly_fqinv_batch_for_bench(int16_t den_buf[24 * 8])
{
  int16x8_t con = vld1q_s16(kpqc_final_consts);
  int16x8_t den[24] __attribute__((aligned(16)));
  int ret;

  for (int i = 0; i < 24; i++)
    den[i] = vld1q_s16(den_buf + 8 * i);
  ret = kpqc_final_fqinv_batch(den, con);
  for (int i = 0; i < 24; i++)
    vst1q_s16(den_buf + 8 * i, den[i]);
  return ret;
}

static void gt_aos_to_kpqc_qsoa(poly *out, const poly *in)
{
  for (int block = 0; block < 24; block++)
  {
    const int offset = 32 * block;
    int16x8x4_t q = vld4q_s16(in->coeffs + offset);

    vst1q_s16(out->coeffs + offset + 0, q.val[0]);
    vst1q_s16(out->coeffs + offset + 8, q.val[1]);
    vst1q_s16(out->coeffs + offset + 16, q.val[2]);
    vst1q_s16(out->coeffs + offset + 24, q.val[3]);
  }
}

static void kpqc_qsoa_to_gt_aos(poly *out, const poly *in)
{
  for (int block = 0; block < 24; block++)
  {
    const int offset = 32 * block;
    int16x8x4_t q;

    q.val[0] = vld1q_s16(in->coeffs + offset + 0);
    q.val[1] = vld1q_s16(in->coeffs + offset + 8);
    q.val[2] = vld1q_s16(in->coeffs + offset + 16);
    q.val[3] = vld1q_s16(in->coeffs + offset + 24);
    vst4q_s16(out->coeffs + offset, q);
  }
}

int kpqc_final_poly_baseinv_gt_layout_for_bench(poly *r, const poly *a)
{
  poly in_qsoa;
  poly out_qsoa;
  int ret;

  gt_aos_to_kpqc_qsoa(&in_qsoa, a);
  ret = kpqc_final_poly_baseinv_for_bench(&out_qsoa, &in_qsoa);
  if (ret != 0)
  {
    memset(r->coeffs, 0, sizeof(r->coeffs));
    return ret;
  }
  kpqc_qsoa_to_gt_aos(r, &out_qsoa);
  return 0;
}
