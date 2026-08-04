#ifndef GT_BACKEND_H
#define GT_BACKEND_H

#include <stdint.h>

#include "poly.h"

typedef enum {
    GT_N32_B1 = 1,
    GT_N32_B2 = 2,
    GT_N32_C = 3,
} gt_n32_variant;

typedef struct {
    int top_min;
    int top_max;
    int preweight_min;
    int preweight_max;
    int dft3_min;
    int dft3_max;
    int split_min;
    int split_max;
    int ntt32_min;
    int ntt32_max;
    int output_min;
    int output_max;
} gt_range_trace;

void gt_ref_ntt_variant(poly *r, gt_n32_variant variant,
                        gt_range_trace *trace);
void gt_poly_ntt_avx2_b1(poly *r);
void gt_poly_ntt_avx2_b2(poly *r);
void gt_avx2_ntt32_b1_rows(int16_t out[32][16],
                           const int16_t in[32][16]);
void gt_avx2_ntt32_b2_rows(int16_t out[32][16],
                           const int16_t in[32][16]);
void gt_avx2_intt32_b_rows(int16_t out[32][16],
                           const int16_t in[32][16]);
void gt_poly_invntt_avx2_b(poly *r);

void gt_poly_ntt(poly *r);
void gt_poly_ntt_lazy(poly *r);
void gt_poly_ntt_canonical(poly *r);
void gt_ref_poly_basemul(poly *r, const poly *a, const poly *b);
void gt_poly_basemul(poly *r, const poly *a, const poly *b);
void gt_poly_basemul_bm_b(poly *r, const poly *a, const poly *b);
void gt_poly_basemul_scale(poly *r, const poly *a, const poly *b);
int gt_ref_poly_baseinv(poly *r, const poly *a);
int gt_poly_baseinv(poly *r, const poly *a);
void gt_ref_poly_invntt_scale(poly *r);
void gt_poly_invntt_scale(poly *r);
void gt_poly_tobytes(uint8_t out[NTRUPLUS_POLYBYTES], const poly *a);
int gt_poly_frombytes(poly *r, const uint8_t in[NTRUPLUS_POLYBYTES]);
int gt_ntt_equal_canonical(const poly *a, const poly *b);

void gt_avx2_reduce32_test(int16_t out[8], const int32_t in[8]);

#endif
