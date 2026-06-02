#ifndef NTT_H
#define NTT_H

#include <stdint.h>
#include "params.h"

extern const int16_t gt_lambda[2][96];
extern const int16_t gt_rowbitrev_lambda[2][96];

void ntt(int16_t r[NTRUPLUS_N], const int16_t a[NTRUPLUS_N]);
void invntt(int16_t r[NTRUPLUS_N], const int16_t a[NTRUPLUS_N]);
void ntt_gt_rowbitrevlayout(int16_t r[NTRUPLUS_N], const int16_t a[NTRUPLUS_N]);
void invntt_gt_rowbitrevlayout(int16_t r[NTRUPLUS_N], const int16_t a[NTRUPLUS_N]);

int  baseinv(int16_t r[4], const int16_t a[4], const int16_t zeta);
void basemul(int16_t r[4], const int16_t a[4], const int16_t b[4], const int16_t zeta);
void basemul_add(int16_t r[4], const int16_t a[4], const int16_t b[4], const int16_t c[4], const int16_t zeta);
void basemul_incomplete_pair(int16_t r_lo[4], int16_t r_hi[4],
                             const int16_t a_lo[4], const int16_t a_hi[4],
                             const int16_t b_lo[4], const int16_t b_hi[4],
                             const int16_t zeta_lo,
                             const int16_t zeta_hi);
void basemul_add_incomplete_pair(int16_t r_lo[4], int16_t r_hi[4],
                                 const int16_t a_lo[4], const int16_t a_hi[4],
                                 const int16_t b_lo[4], const int16_t b_hi[4],
                                 const int16_t c_lo[4], const int16_t c_hi[4],
                                 const int16_t zeta_lo,
                                 const int16_t zeta_hi);
int  baseinv_incomplete_pair(int16_t r_lo[4], int16_t r_hi[4],
                             const int16_t a_lo[4], const int16_t a_hi[4],
                             const int16_t zeta_lo,
                             const int16_t zeta_hi);

#endif
