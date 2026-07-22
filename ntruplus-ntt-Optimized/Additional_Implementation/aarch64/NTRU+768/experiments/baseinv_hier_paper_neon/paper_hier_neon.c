/*
 * Neon implementation of the recursive hierarchy from
 * Algorithm 15 of "Accelerating NTRU+ Key Generation via Hierarchical Batch
 * Inversion". This is an independent implementation against the paper's
 * arithmetic contract. Production builds expose only k8 and select it through
 * the default-off GT_BASEINV_USE_PAPER_HIER_K8 gate.
 */

#include <arm_neon.h>
#include <stdint.h>
#include <string.h>

#include "ntt.h"
#include "params.h"
#include "poly.h"

#define GT_DEN_VECTORS 24
#define GT_DEN_LANES 8
#define GT_DEN_WORDS (GT_DEN_VECTORS * GT_DEN_LANES)

static const int16_t paper_hier_scaled_r_consts[8]
    __attribute__((aligned(16))) = {
        3457, 19412, -12929, -147, -1393, -682, -6464, 0};

int16x8_t gt_fqinv15_asm(int16x8_t a, int16x8_t con);
#if defined(GT_BASEINV_USE_PAPER_HIER_K8) && \
    defined(GT_BASEINV_SCALED_R_EXTERNAL_BACKEND)
void baseinv_batch_finish24_n1_asm(int16_t *dst, const int16_t *den_inv);
int poly_baseinv_scaled_r(poly *r, const poly *a);
#endif
#if !defined(GT_BASEINV_PAPER_HIER_K8_ONLY)
int gt_baseinv_paper_hier_k8_vec(int16x8_t den[GT_DEN_VECTORS],
                                 int16x8_t con);
int gt_baseinv_paper_hier_k8_preformed_vec(
    int16x8_t den[GT_DEN_VECTORS], int16x8_t c1[8], int16x8_t group[8],
    int16x8_t con);
int gt_baseinv_paper_hier_k6_den_for_bench(int16_t den[GT_DEN_WORDS]);
int gt_baseinv_paper_hier_k8_den_for_bench(int16_t den[GT_DEN_WORDS]);
int gt_baseinv_paper_hier_k12_den_for_bench(int16_t den[GT_DEN_WORDS]);
int gt_baseinv_paper_hier_k6_vec_for_bench(int16x8_t den[GT_DEN_VECTORS],
                                           int16x8_t con);
int gt_baseinv_paper_hier_k8_vec_for_bench(int16x8_t den[GT_DEN_VECTORS],
                                           int16x8_t con);
int gt_baseinv_paper_hier_k12_vec_for_bench(int16x8_t den[GT_DEN_VECTORS],
                                            int16x8_t con);
#endif

static inline int16x8_t paper_montgomery_reduce(int32x4_t lo, int32x4_t hi,
                                                int16x8_t con)
{
  int16x8_t t;

  t = vuzp1q_s16(vreinterpretq_s16_s32(lo), vreinterpretq_s16_s32(hi));
  t = vmulq_laneq_s16(t, con, 2);
  lo = vmlal_lane_s16(lo, vget_low_s16(t), vget_low_s16(con), 0);
  hi = vmlal_high_lane_s16(hi, t, vget_low_s16(con), 0);

  return vuzp2q_s16(vreinterpretq_s16_s32(lo),
                    vreinterpretq_s16_s32(hi));
}

static inline int16x8_t paper_fqmul(int16x8_t x, int16x8_t y,
                                    int16x8_t con)
{
  int32x4_t lo = vmull_s16(vget_low_s16(x), vget_low_s16(y));
  int32x4_t hi = vmull_high_s16(x, y);

  return paper_montgomery_reduce(lo, hi, con);
}

#if defined(GT_BASEINV_USE_PAPER_HIER_K8) && \
    defined(GT_BASEINV_SCALED_R_EXTERNAL_BACKEND)
static inline int16x8_t paper_reduce_mul2(int16x8_t a0, int16x8_t b0,
                                          int16x8_t a1, int16x8_t b1,
                                          int16x8_t con)
{
  int32x4_t lo = vmull_s16(vget_low_s16(a0), vget_low_s16(b0));
  int32x4_t hi = vmull_high_s16(a0, b0);

  lo = vmlal_s16(lo, vget_low_s16(a1), vget_low_s16(b1));
  hi = vmlal_high_s16(hi, a1, b1);
  return paper_montgomery_reduce(lo, hi, con);
}

static inline int16x8_t paper_reduce_mul3(int16x8_t a0, int16x8_t b0,
                                          int16x8_t a1, int16x8_t b1,
                                          int16x8_t a2, int16x8_t b2,
                                          int16x8_t con)
{
  int32x4_t lo = vmull_s16(vget_low_s16(a0), vget_low_s16(b0));
  int32x4_t hi = vmull_high_s16(a0, b0);

  lo = vmlal_s16(lo, vget_low_s16(a1), vget_low_s16(b1));
  hi = vmlal_high_s16(hi, a1, b1);
  lo = vmlal_s16(lo, vget_low_s16(a2), vget_low_s16(b2));
  hi = vmlal_high_s16(hi, a2, b2);
  return paper_montgomery_reduce(lo, hi, con);
}

static inline void paper_baseinv_8_prepare(int16_t *dst, int16x8_t *den,
                                            const int16_t *src,
                                            int16x8_t zeta, int16x8_t con)
{
  int16x8x4_t a = vld4q_s16(src);
  int16x8x4_t n;
  int16x8_t neg2a2 = vshlq_n_s16(vnegq_s16(a.val[2]), 1);
  int16x8_t neg2a3 = vshlq_n_s16(vnegq_s16(a.val[3]), 1);
  int16x8_t t0, t1, t2;

  t0 = paper_reduce_mul2(a.val[2], a.val[2], a.val[1], neg2a3, con);
  t1 = paper_fqmul(a.val[3], a.val[3], con);
  t0 = paper_reduce_mul2(t0, zeta, a.val[0], a.val[0], con);
  t1 = paper_reduce_mul3(t1, zeta, a.val[1], a.val[1],
                         a.val[0], neg2a2, con);
  t2 = paper_fqmul(t1, zeta, con);

  *den = paper_reduce_mul2(t0, t0, vnegq_s16(t1), t2, con);
  n.val[0] = paper_reduce_mul2(a.val[0], t0, a.val[2], t2, con);
  n.val[1] = paper_reduce_mul2(a.val[3], t2, a.val[1], t0, con);
  n.val[2] = paper_reduce_mul2(a.val[2], t0, a.val[0], t1, con);
  n.val[3] = paper_reduce_mul2(a.val[1], t1, a.val[3], t0, con);
  vst4q_s16(dst, n);
}
#endif

static inline int paper_has_zero_lane(int16x8_t x)
{
  return !vminvq_u16(vreinterpretq_u16_s16(x));
}

/* Pair recovery is kept separate so the compiler sees independent pairs. */
static inline void paper_recover_pair(int16x8_t *a, int16x8_t *b,
                                      int16x8_t product_inv,
                                      int16x8_t con)
{
  int16x8_t old_a = *a;
  int16x8_t old_b = *b;

  *a = paper_fqmul(old_b, product_inv, con);
  *b = paper_fqmul(old_a, product_inv, con);
}

#if !defined(GT_BASEINV_PAPER_HIER_K8_ONLY)
static int paper_inverse6_fixed(int16x8_t r[6], int16x8_t con)
{
  int16x8_t l3[3];
  int16x8_t l3_inv[3];
  int16x8_t prefix01;
  int16x8_t root;
  int16x8_t root_inv;
  int16x8_t w;

  l3[0] = paper_fqmul(r[0], r[1], con);
  l3[1] = paper_fqmul(r[2], r[3], con);
  l3[2] = paper_fqmul(r[4], r[5], con);

  prefix01 = paper_fqmul(l3[0], l3[1], con);
  root = paper_fqmul(prefix01, l3[2], con);
  if (paper_has_zero_lane(root))
    return 1;

  root_inv = gt_fqinv15_asm(root, con);

  l3_inv[2] = paper_fqmul(prefix01, root_inv, con);
  w = paper_fqmul(root_inv, l3[2], con);
  l3_inv[1] = paper_fqmul(l3[0], w, con);
  l3_inv[0] = paper_fqmul(w, l3[1], con);

  paper_recover_pair(&r[0], &r[1], l3_inv[0], con);
  paper_recover_pair(&r[2], &r[3], l3_inv[1], con);
  paper_recover_pair(&r[4], &r[5], l3_inv[2], con);
  return 0;
}
#endif

/* Recursive inner problem: 8 -> 4 -> 2 -> 1 -> 2 -> 4 -> 8. */
static int paper_inverse8(int16x8_t r[8], int16x8_t con)
{
  int16x8_t l4[4];
  int16x8_t l2[2];
  int16x8_t l2_inv[2];
  int16x8_t l4_inv[4];
  int16x8_t root;
  int16x8_t root_inv;

  l4[0] = paper_fqmul(r[0], r[1], con);
  l4[1] = paper_fqmul(r[2], r[3], con);
  l4[2] = paper_fqmul(r[4], r[5], con);
  l4[3] = paper_fqmul(r[6], r[7], con);

  l2[0] = paper_fqmul(l4[0], l4[1], con);
  l2[1] = paper_fqmul(l4[2], l4[3], con);
  root = paper_fqmul(l2[0], l2[1], con);
  if (paper_has_zero_lane(root))
    return 1;

  root_inv = gt_fqinv15_asm(root, con);
  l2_inv[0] = paper_fqmul(root_inv, l2[1], con);
  l2_inv[1] = paper_fqmul(root_inv, l2[0], con);

  l4_inv[0] = paper_fqmul(l2_inv[0], l4[1], con);
  l4_inv[1] = paper_fqmul(l2_inv[0], l4[0], con);
  l4_inv[2] = paper_fqmul(l2_inv[1], l4[3], con);
  l4_inv[3] = paper_fqmul(l2_inv[1], l4[2], con);

  paper_recover_pair(&r[0], &r[1], l4_inv[0], con);
  paper_recover_pair(&r[2], &r[3], l4_inv[1], con);
  paper_recover_pair(&r[4], &r[5], l4_inv[2], con);
  paper_recover_pair(&r[6], &r[7], l4_inv[3], con);
  return 0;
}

/* Recursive inner problem: 12 -> 6 -> 3 -> 1 -> 3 -> 6 -> 12. */
#if !defined(GT_BASEINV_PAPER_HIER_K8_ONLY)
static int paper_inverse12(int16x8_t r[12], int16x8_t con)
{
  int16x8_t l6[6];
  int16x8_t l3[3];
  int16x8_t l3_inv[3];
  int16x8_t l6_inv[6];
  int16x8_t prefix01;
  int16x8_t root;
  int16x8_t root_inv;
  int16x8_t w;

  l6[0] = paper_fqmul(r[0], r[1], con);
  l6[1] = paper_fqmul(r[2], r[3], con);
  l6[2] = paper_fqmul(r[4], r[5], con);
  l6[3] = paper_fqmul(r[6], r[7], con);
  l6[4] = paper_fqmul(r[8], r[9], con);
  l6[5] = paper_fqmul(r[10], r[11], con);

  l3[0] = paper_fqmul(l6[0], l6[1], con);
  l3[1] = paper_fqmul(l6[2], l6[3], con);
  l3[2] = paper_fqmul(l6[4], l6[5], con);

  prefix01 = paper_fqmul(l3[0], l3[1], con);
  root = paper_fqmul(prefix01, l3[2], con);
  if (paper_has_zero_lane(root))
    return 1;

  root_inv = gt_fqinv15_asm(root, con);
  l3_inv[2] = paper_fqmul(prefix01, root_inv, con);
  w = paper_fqmul(root_inv, l3[2], con);
  l3_inv[1] = paper_fqmul(l3[0], w, con);
  l3_inv[0] = paper_fqmul(w, l3[1], con);

  l6_inv[0] = paper_fqmul(l3_inv[0], l6[1], con);
  l6_inv[1] = paper_fqmul(l3_inv[0], l6[0], con);
  l6_inv[2] = paper_fqmul(l3_inv[1], l6[3], con);
  l6_inv[3] = paper_fqmul(l3_inv[1], l6[2], con);
  l6_inv[4] = paper_fqmul(l3_inv[2], l6[5], con);
  l6_inv[5] = paper_fqmul(l3_inv[2], l6[4], con);

  paper_recover_pair(&r[0], &r[1], l6_inv[0], con);
  paper_recover_pair(&r[2], &r[3], l6_inv[1], con);
  paper_recover_pair(&r[4], &r[5], l6_inv[2], con);
  paper_recover_pair(&r[6], &r[7], l6_inv[3], con);
  paper_recover_pair(&r[8], &r[9], l6_inv[4], con);
  paper_recover_pair(&r[10], &r[11], l6_inv[5], con);
  return 0;
}
#endif

#define FORM_GROUP2(G, B)                                                    \
  do                                                                        \
  {                                                                         \
    group[(G)] = paper_fqmul(den[(B)], den[(B) + 1], con);                  \
  } while (0)

#define RECOVER_GROUP2(G, B)                                                \
  paper_recover_pair(&den[(B)], &den[(B) + 1], group[(G)], con)

#define FORM_GROUP3(G, B)                                                    \
  do                                                                        \
  {                                                                         \
    c1[(G)] = paper_fqmul(den[(B)], den[(B) + 1], con);                     \
    group[(G)] = paper_fqmul(c1[(G)], den[(B) + 2], con);                   \
  } while (0)

#define RECOVER_GROUP3(G, B)                                                 \
  do                                                                        \
  {                                                                         \
    int16x8_t old1 = den[(B) + 1];                                          \
    int16x8_t old2 = den[(B) + 2];                                          \
    int16x8_t w = group[(G)];                                               \
    den[(B) + 2] = paper_fqmul(c1[(G)], w, con);                            \
    w = paper_fqmul(w, old2, con);                                          \
    den[(B) + 1] = paper_fqmul(den[(B)], w, con);                           \
    den[(B)] = paper_fqmul(w, old1, con);                                   \
  } while (0)

#define FORM_GROUP4(G, B)                                                    \
  do                                                                        \
  {                                                                         \
    c1[(G)] = paper_fqmul(den[(B)], den[(B) + 1], con);                     \
    c2[(G)] = paper_fqmul(c1[(G)], den[(B) + 2], con);                      \
    group[(G)] = paper_fqmul(c2[(G)], den[(B) + 3], con);                   \
  } while (0)

#define RECOVER_GROUP4(G, B)                                                 \
  do                                                                        \
  {                                                                         \
    int16x8_t old1 = den[(B) + 1];                                          \
    int16x8_t old2 = den[(B) + 2];                                          \
    int16x8_t old3 = den[(B) + 3];                                          \
    int16x8_t w = group[(G)];                                               \
    den[(B) + 3] = paper_fqmul(c2[(G)], w, con);                            \
    w = paper_fqmul(w, old3, con);                                          \
    den[(B) + 2] = paper_fqmul(c1[(G)], w, con);                            \
    w = paper_fqmul(w, old2, con);                                          \
    den[(B) + 1] = paper_fqmul(den[(B)], w, con);                           \
    den[(B)] = paper_fqmul(w, old1, con);                                   \
  } while (0)

#if !defined(GT_BASEINV_PAPER_HIER_K8_ONLY)
static int paper_hier_k6(int16x8_t den[GT_DEN_VECTORS], int16x8_t con)
{
  int16x8_t c1[6];
  int16x8_t c2[6];
  int16x8_t group[6];

  FORM_GROUP4(0, 0);
  FORM_GROUP4(1, 4);
  FORM_GROUP4(2, 8);
  FORM_GROUP4(3, 12);
  FORM_GROUP4(4, 16);
  FORM_GROUP4(5, 20);
  if (paper_inverse6_fixed(group, con))
    return 1;
  RECOVER_GROUP4(0, 0);
  RECOVER_GROUP4(1, 4);
  RECOVER_GROUP4(2, 8);
  RECOVER_GROUP4(3, 12);
  RECOVER_GROUP4(4, 16);
  RECOVER_GROUP4(5, 20);
  return 0;
}
#endif

static int paper_hier_k8(int16x8_t den[GT_DEN_VECTORS], int16x8_t con)
{
  int16x8_t c1[8];
  int16x8_t group[8];

  FORM_GROUP3(0, 0);
  FORM_GROUP3(1, 3);
  FORM_GROUP3(2, 6);
  FORM_GROUP3(3, 9);
  FORM_GROUP3(4, 12);
  FORM_GROUP3(5, 15);
  FORM_GROUP3(6, 18);
  FORM_GROUP3(7, 21);
  if (paper_inverse8(group, con))
    return 1;
  RECOVER_GROUP3(0, 0);
  RECOVER_GROUP3(1, 3);
  RECOVER_GROUP3(2, 6);
  RECOVER_GROUP3(3, 9);
  RECOVER_GROUP3(4, 12);
  RECOVER_GROUP3(5, 15);
  RECOVER_GROUP3(6, 18);
  RECOVER_GROUP3(7, 21);
  return 0;
}

#if !defined(GT_BASEINV_PAPER_HIER_K8_ONLY)
static int paper_hier_k12(int16x8_t den[GT_DEN_VECTORS], int16x8_t con)
{
  int16x8_t group[12];

  FORM_GROUP2(0, 0);
  FORM_GROUP2(1, 2);
  FORM_GROUP2(2, 4);
  FORM_GROUP2(3, 6);
  FORM_GROUP2(4, 8);
  FORM_GROUP2(5, 10);
  FORM_GROUP2(6, 12);
  FORM_GROUP2(7, 14);
  FORM_GROUP2(8, 16);
  FORM_GROUP2(9, 18);
  FORM_GROUP2(10, 20);
  FORM_GROUP2(11, 22);
  if (paper_inverse12(group, con))
    return 1;
  RECOVER_GROUP2(0, 0);
  RECOVER_GROUP2(1, 2);
  RECOVER_GROUP2(2, 4);
  RECOVER_GROUP2(3, 6);
  RECOVER_GROUP2(4, 8);
  RECOVER_GROUP2(5, 10);
  RECOVER_GROUP2(6, 12);
  RECOVER_GROUP2(7, 14);
  RECOVER_GROUP2(8, 16);
  RECOVER_GROUP2(9, 18);
  RECOVER_GROUP2(10, 20);
  RECOVER_GROUP2(11, 22);
  return 0;
}
#endif

#if !defined(GT_BASEINV_PAPER_HIER_K8_ONLY)
int gt_baseinv_paper_hier_k8_vec(int16x8_t den[GT_DEN_VECTORS],
                                 int16x8_t con)
{
  return paper_hier_k8(den, con);
}

int gt_baseinv_paper_hier_k8_preformed_vec(
    int16x8_t den[GT_DEN_VECTORS], int16x8_t c1[8], int16x8_t group[8],
    int16x8_t con)
{
  if (paper_inverse8(group, con))
    return 1;
  RECOVER_GROUP3(0, 0);
  RECOVER_GROUP3(1, 3);
  RECOVER_GROUP3(2, 6);
  RECOVER_GROUP3(3, 9);
  RECOVER_GROUP3(4, 12);
  RECOVER_GROUP3(5, 15);
  RECOVER_GROUP3(6, 18);
  RECOVER_GROUP3(7, 21);
  return 0;
}
#endif

#if defined(GT_BASEINV_USE_PAPER_HIER_K8) && \
    defined(GT_BASEINV_SCALED_R_EXTERNAL_BACKEND)
int poly_baseinv_scaled_r(poly *r, const poly *a)
{
  int16x8_t con = vld1q_s16(paper_hier_scaled_r_consts);
  int16x8_t den[GT_DEN_VECTORS] __attribute__((aligned(16)));
  const int16_t *src = a->coeffs;
  int16_t *dst = r->coeffs;
  const int16_t *lambda = &gt_rowbitrev_lambda[0][0];

  for (int i = 0; i < GT_DEN_VECTORS; i++)
  {
    paper_baseinv_8_prepare(dst, &den[i], src, vld1q_s16(lambda), con);
    src += 8 * 4;
    dst += 8 * 4;
    lambda += 8;
  }

  if (paper_hier_k8(den, con))
  {
    memset(r->coeffs, 0, sizeof(r->coeffs));
    return 1;
  }

  baseinv_batch_finish24_n1_asm(r->coeffs, (const int16_t *)den);
  return 0;
}
#endif

#if !defined(GT_BASEINV_PAPER_HIER_K8_ONLY)
typedef int (*paper_hier_core)(int16x8_t den[GT_DEN_VECTORS],
                               int16x8_t con);

static int paper_den_wrapper(int16_t den_buf[GT_DEN_WORDS],
                             paper_hier_core core)
{
  int16x8_t den[GT_DEN_VECTORS] __attribute__((aligned(16)));
  int16x8_t con = vld1q_s16(paper_hier_scaled_r_consts);
  int ret;

  for (int i = 0; i < GT_DEN_VECTORS; i++)
    den[i] = vld1q_s16(den_buf + GT_DEN_LANES * i);
  ret = core(den, con);
  for (int i = 0; i < GT_DEN_VECTORS; i++)
    vst1q_s16(den_buf + GT_DEN_LANES * i, den[i]);
  return ret;
}

int gt_baseinv_paper_hier_k6_den_for_bench(int16_t den[GT_DEN_WORDS])
{
  return paper_den_wrapper(den, paper_hier_k6);
}

int gt_baseinv_paper_hier_k8_den_for_bench(int16_t den[GT_DEN_WORDS])
{
  return paper_den_wrapper(den, paper_hier_k8);
}

int gt_baseinv_paper_hier_k12_den_for_bench(int16_t den[GT_DEN_WORDS])
{
  return paper_den_wrapper(den, paper_hier_k12);
}

int gt_baseinv_paper_hier_k6_vec_for_bench(int16x8_t den[GT_DEN_VECTORS],
                                           int16x8_t con)
{
  return paper_hier_k6(den, con);
}

int gt_baseinv_paper_hier_k8_vec_for_bench(int16x8_t den[GT_DEN_VECTORS],
                                           int16x8_t con)
{
  return gt_baseinv_paper_hier_k8_vec(den, con);
}

int gt_baseinv_paper_hier_k12_vec_for_bench(int16x8_t den[GT_DEN_VECTORS],
                                            int16x8_t con)
{
  return paper_hier_k12(den, con);
}
#endif
